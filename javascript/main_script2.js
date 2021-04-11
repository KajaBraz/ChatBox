function format_sent_message(id_length, my_login, value) {
    var name = my_login.slice(0, -id_length)
    return `${name}: ${value}`;
}


function append_div_messages(my_name, message, message_box_element, class_name, id_length) {
    var m = format_sent_message(id_length, my_name, message);
    var div = append_div(m, message_box_element, class_name);
    if (my_name === login) {
        div.style.float = "right";
    };
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
        append_div_messages(name, val, message_box_element, class_name, id_length);
        message_box_element.scrollTo(0, message_box_element.scrollHeight);
    };
}


function send_button(message_type, message_element, my_name, chat_name, websocket) {
    var message = message_element.value;
    send_websocket(message_type, message, my_name, chat_name, websocket);
    message_element.value = "";
    console.log('websocket sent');
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
    };
    console.log(id);
    return id;
}


function connect(user_name, chat_name, id_length) {
    if (webSocket != null) {
        console.log('not nnull');
        webSocket.close();
    };
    if (user_name != "" && chat_name != "") {
        var url = `ws://${server_address}/${chat_name}/${user_name}`;
        console.log("url", url);
        webSocket = new WebSocket(url);

        webSocket.onopen = () => {
            retrieve_messages(login, chat, webSocket);
        };
        webSocket.onmessage = (event) => {
            console.log("message received");
            handle_receive(event.data, all_messages_element, "message", id_length);
        };
        webSocket.onclose = (e) => {
            console.log('closing ws');
        };
        webSocket.onerror = (e) => {
            console.log('ws error');
        };
    };
}


function remove_redundant_chat(chat_array, max_num) {
    if (chat_array.length > max_num) {
        var to_remove = document.getElementById(chat_array[0]);
        to_remove.remove();
        chat_array.shift();
        console.log("removed");
    };
}


function add_chat(new_chat, public_chat = true) {
    console.log("adding");
    if (public_chat === true) {
        if (!active_public_chats.includes(new_chat)) {
            active_public_chats.push(new_chat);
            var new_div = append_div(new_chat, public_chats, "availableChat");
            new_div.id = new_chat;
            remove_redundant_chat(active_public_chats, 5);
        };

    }
    else {
        if (!active_private_chats.includes(new_chat)) {
            active_private_chats.push(new_chat);
            var new_div = append_div(new_chat, private_chats, "availableChat");
            var node = document.createTextNode(new_chat);
            new_div.id = new_chat;
            remove_redundant_chat(active_private_chats, 5);
        };
    };
}


function retrieve_messages(user_name, chat_name, ws) {
    send_websocket("previous_messages", "history", user_name, chat_name, ws);
    console.log("retrieving old messages");
}


var button_element = document.getElementById("sendMessageButton");
var message_element = document.getElementById("newMessage");
var all_messages_element = document.getElementById("receivedMessages");
var my_name_element = document.getElementById("login");
var connect_button = document.getElementById("connectButton");
var chat_destination_element = document.getElementById("findChat");
var chat_name_header = document.getElementById("chatNameHeader");
var public_chats = document.getElementById("publicChats");
var private_chats = document.getElementById("privateChats");

var login = "";
var chat = "";
var webSocket = null;
var id_length = 20;
var server_address = "localhost:11000";
var active_public_chats = [];
var active_private_chats = [];
var recently_used_chats = [];

window.onload = function () {
    console.log("onload");
    login = localStorage.getItem("active_user");
    chat = localStorage.getItem("active_chat");
    console.log('user storage', login);
    console.log('chat storage', chat);
    if (chat != null) {
        add_chat(chat);
        chat_name_header.innerHTML = chat;
    };
    connect(login, chat, id_length);
    webSocket.onopen = () => {
        retrieve_messages(login, chat, webSocket);
    };
}


connect_button.onclick = () => {
    var id = generate_unique_id(id_length);
    login = my_name_element.value + id;
    chat = chat_destination_element.value;
    chat_name_header.innerHTML = chat_destination_element.value;
    localStorage.setItem("active_user", login);
    localStorage.setItem("active_chat", chat);

    console.log(login, chat);
    connect(login, chat, id_length);
    add_chat(chat);
};


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
    };
});
