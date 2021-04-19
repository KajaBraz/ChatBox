function append_div_messages(my_name, timestamp, message, message_box_element, class_name, id_length) {
    var div = append_div("", message_box_element, class_name);
    if (my_name === login) {
        div.style.float = "right";
    }
    let message_header_div = append_div("", div, "messageHeader");
    let name = my_name.slice(0, -id_length);
    append_div(name, message_header_div, "divAuthor");
    let date = new Date(timestamp);
    append_div(date.toLocaleDateString() + " - " + date.toLocaleTimeString(), message_header_div, "divTimestamp");
    div.innerHTML += message;
}


function append_div(child, parent, class_name) {
    var node = document.createTextNode(child);
    var div = document.createElement("div");
    div.className = class_name;
    div.appendChild(node);
    parent.appendChild(div);
    return div;
}


function handle_receive(message, message_box_element, class_name, id_length) {
    var m = JSON.parse(message);
    if (m["message_type"] == "message") {
        var name = m["message_sender"];
        var val = m["message_value"];
        var timestamp = m["message_timestamp"];
        append_div_messages(name, timestamp, val, message_box_element, class_name, id_length);
        message_box_element.scrollTo(0, message_box_element.scrollHeight);
    }
}


function send_button(message_type, message_element, my_name, chat_name, websocket) {
    var message = message_element.value;
    send_websocket(message_type, message, my_name, chat_name, websocket);
    message_element.value = "";
    console.log('websocket sent', websocket);
}


function send_websocket(message_type, message, sender, chat_destination, websocket) {
    var json_message = {
        message_type: message_type,
        message_value: message,
        message_destination: chat_destination,
        message_sender: sender
    };
    console.log(json_message);
    websocket.send(JSON.stringify(json_message));
}


function generate_unique_id(n) {
    var s = "qwertyuioopasdfghjklzxcvbnmWERTYUIOPASDFGHJKLZXCVBNM1234567890";
    var id = '';
    for (let i = 0; i < n; i++) {
        id += s[Math.floor(Math.random() * s.length)];
    }
    console.log(id);
    return id;
}


function connect(user_name, chat_name, id_length) {
    if (webSocket != null) {
        console.log('not nnull');
        webSocket.close(1000);
    }
    if (user_name != "" && chat_name != "") {
        var url = `ws://${server_address}/${chat_name}/${user_name}`;
        console.log("url", url);
        webSocket = new WebSocket(url);

        webSocket.onopen = () => {
            retrieve_messages(login, chat, webSocket);
            console.log(webSocket.readyState);
        };
        webSocket.onmessage = (event) => {
            console.log("message received");
            handle_receive(event.data, all_messages_element, "message", id_length);
        };
        webSocket.onclose = (e) => {
            console.log(`ws closed (${user_name}, ${chat_name}), code: ${e.code}, reason: ${e.reason}`);
            console.log(webSocket.readyState);
            if (e.code === 4000) {
                window.alert(e.reason);
            }
        };
        webSocket.onerror = (e) => {
            console.log('ws error');
        };
    }
}


function remove_redundant_chat(chat_array, max_num) {
    if (chat_array.length > max_num) {
        var to_remove = document.getElementById(chat_array[0]);
        to_remove.remove();
        chat_array.shift();
        console.log("removed", to_remove);
    }
}


function add_chat(new_chat) {
    console.log("adding");
    if (!active_recent_chats.includes(new_chat)) {
        active_recent_chats.push(new_chat);
        var new_div = append_div(new_chat, recent_chats, "availableChat");
        new_div.id = new_chat;
        new_div.onclick = () => {
            chat_change(new_chat);
        }
        remove_redundant_chat(active_recent_chats, 5);
    }
}

function chat_change(chat_name) {
    clear_message_element(all_messages_element);
    chat = chat_name;
    chat_name_header.innerHTML = chat;
    chat_destination_element.value = chat;
    localStorage.setItem("active_chat", chat);
    connect(login, chat, id_length);
    localStorage.setItem("recent_chats", active_recent_chats);
}


function retrieve_messages(user_name, chat_name, ws) {
    send_websocket("previous_messages", "history", user_name, chat_name, ws);
    console.log("retrieving old messages");
}


function retrieve_recent_chats() {
    recently_used_chats = localStorage.getItem("recent_chats").split(",");
    console.log(recently_used_chats);
    for (let i = 0; i < recently_used_chats.length; i++) {
        add_chat(recently_used_chats[i]);
    }
}


function clear_message_element(message_box) {
    while (message_box.firstChild) {
        message_box.removeChild(message_box.firstChild);
    }
}


var button_element = document.getElementById("sendMessageButton");
var message_element = document.getElementById("newMessage");
var all_messages_element = document.getElementById("receivedMessages");
var my_name_element = document.getElementById("login");
var connect_button = document.getElementById("connectButton");
var chat_destination_element = document.getElementById("findChat");
var chat_name_header = document.getElementById("chatNameHeader");
var recent_chats = document.getElementById("recentlyUsedChats");

var login = "";
var chat = "";
var server_address = "localhost:11000";
var webSocket = null;
var id_length = 20;
var active_recent_chats = [];
var recently_used_chats = [];


window.onload = function () {
    console.log("onload");
    my_name_element.value = localStorage.getItem("active_user").slice(0, -id_length);
    chat_destination_element.value = localStorage.getItem("active_chat");
    retrieve_recent_chats();
}


connect_button.onclick = () => {
    if (localStorage.getItem("active_user") && my_name_element.value === localStorage.getItem("active_user").slice(0, -id_length)) {
        login = localStorage.getItem("active_user");
        console.log('equal logins');
    } else {
        var id = generate_unique_id(id_length);
        login = my_name_element.value + id;
        localStorage.setItem("active_user", login);
    }

    chat_change(chat_destination_element.value);
    add_chat(chat);
    console.log(login, chat);
}


button_element.onclick = () => {
    send_button(
        "message",
        message_element,
        login,
        chat,
        webSocket
    );
};


message_element.addEventListener("keypress", function (event) {
    if (event.code === 'Enter') {
        event.preventDefault();
        send_button(
            "message",
            message_element,
            login,
            chat,
            webSocket
        );
    }
});
