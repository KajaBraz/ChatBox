function append_div_messages(my_name, timestamp, message, message_box_element, class_name) {
    var div = append_div("", message_box_element, class_name);
    if (my_name === login) {
        div.style.float = "right";
    } else {
        div.style.float = "left";
    }
    let message_header_div = append_div("", div, "messageHeader");
    let name = retrieve_display_login(my_name);
    append_div(name, message_header_div, "divAuthor");
    let date = new Date(timestamp);
    let timestamp_div = append_div(date.toLocaleDateString() + " - " + date.toLocaleTimeString(), message_header_div, "divTimestamp");
    let message_text_div = append_div(message, div, "messageText");
    return div;
}


function append_div(child, parent, class_name) {
    var node = document.createTextNode(child);
    var div = document.createElement("div");
    div.className = class_name;
    div.appendChild(node);
    parent.appendChild(div);
    return div;
}


function insert_div(child, parent, class_name) {
    var node = document.createTextNode(child);
    var div = document.createElement("div");
    div.className = class_name;
    div.appendChild(node);
    parent.insertBefore(div, parent.firstChild);
    return div;
}


function handle_receive(message, message_box_element, class_name) {
    var m = JSON.parse(message);
    if (m["message_type"] == "message") {
        val = m["message_value"];
        var name = val["sender_login"];
        var message_text = detect_hyperlink(val["message"]);
        var timestamp = val["timestamp"];
        console.log('message val', message_text);
        var new_message = append_div_messages(name, timestamp, message_text, message_box_element, class_name);
        new_message.id = val["id"];
        message_box_element.scrollTo(0, message_box_element.scrollHeight);
        if (class_name === "message messageUnread") {
            new_message.id = generate_unique_id(5);
            console.log("pushing");
            unread_messages_ids.push(new_message.id);
        }
    }
    else if (m["message_type"] == "previous_messages") {
        m["multiple_messages"].forEach(single_message => {
            var name = single_message["sender_login"];
            var message_text = detect_hyperlink(single_message["message"]);
            var timestamp = single_message["timestamp"];
            var status = assign_read_unread_class(timestamp);
            var new_message = append_div_messages(name, timestamp, message_text, message_box_element, status);
            new_message.id = single_message["id"];
            message_box_element.scrollTo(0, message_box_element.scrollHeight);
            if (status === "message messageUnread") {
                new_message.id = generate_unique_id(5);
                console.log("pushing");
                unread_messages_ids.push(new_message.id);
            }
        })
    }
    else if (m["message_type"] == "users_update") {
        let active_users_element = document.getElementById("activeUsers");
        console.log("active users ", active_users_element);
        let new_users = m["message_value"];
        let chat_name = m["message_destination"];
        update_user_list(new_users, active_users_element, "chatUser");
        console.log(new_users, chat_name);
    }
}


function send_button(message_type, message_element, my_name, chat_name, websocket) {
    var message = message_element.value;
    if (not_blank(message)) {
        send_websocket(message_type, message, my_name, chat_name, websocket);
        message_element.value = "";
        console.log('websocket sent', websocket);
    }
}


function send_websocket(message_type, message, sender, chat_destination, websocket) {
    var json_message = {
        message_type: message_type,
        message_value: message,
        message_destination: chat_destination,
        message_sender: sender
    };
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


function retrieve_display_login(user_name) {
    let name = user_name.slice(0, -id_length);
    console.log("retrieving user name:", name);
    return name;
}


function connect(user_name, chat_name) {
    if (webSocket != null) {
        console.log('not nnull');
        webSocket.close(1000);
    }
    let short_name = retrieve_display_login(user_name);
    if (not_blank(short_name) && not_blank(chat_name)) {
        var url = `ws://${server_address}/${chat_name}/${user_name}`;
        console.log("url", url);
        webSocket = new WebSocket(url);

        webSocket.onopen = () => {
            retrieve_messages(login, chat, webSocket);
            chat_participants = new Set();
            document.getElementById("activeUsers").innerHTML = "";
            console.log(webSocket.readyState);
            message_element.focus();
            if (localStorage.getItem(LEAVING_LOCAL_STORAGE)) {
                leaving_times_dict = JSON.parse(localStorage.getItem(LEAVING_LOCAL_STORAGE));
            }
            if (chat_name in leaving_times_dict) {
                last_active_in_chat = leaving_times_dict[chat_name];
            }
            console.log("retrieved leaving times", leaving_times_dict);
        };
        webSocket.onmessage = (event) => {
            console.log(event.data);
            if (check_focus()) {
                var class_name = "message";
            }
            else {
                var class_name = "message messageUnread";
            }
            handle_receive(event.data, all_messages_element, class_name);
        };
        webSocket.onclose = (e) => {
            console.log(`ws closed (${user_name}, ${chat_name}), code: ${e.code}, reason: ${e.reason}`);
            console.log(webSocket.readyState);
            if (e.code === 4000) {
                window.alert(e.reason);
            }
            let t = new Date().getTime();
            leaving_times_dict[chat_name] = t;
            console.log("saved leaving times", leaving_times_dict);
            let leaving_times_json = JSON.stringify(leaving_times_dict);
            localStorage.setItem(LEAVING_LOCAL_STORAGE, leaving_times_json);
            last_active_in_chat = -1;
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

function remove_given_chat(chat_array, chat_name) {
    let to_remove = document.getElementById(chat_name);
    to_remove.remove();
    console.log("removed", to_remove);
}


function add_chat(new_chat) {
    console.log("adding");
    if (!active_recent_chats.includes(new_chat) && not_blank(new_chat)) {
        console.log("IF");
        console.log(active_recent_chats);
        active_recent_chats.push(new_chat);
        // var new_div = append_div(new_chat, recent_chats, "availableChat");
        var new_div = insert_div(new_chat, recent_chats, "availableChat");
        new_div.id = new_chat;
        new_div.onclick = () => {
            chat_change(new_chat);
        }
        remove_redundant_chat(active_recent_chats, 5);
    }
    else if (active_recent_chats.includes(new_chat) && active_recent_chats.indexOf(new_chat) != 4) {
        console.log("ELSE");
        console.log(active_recent_chats);
        var elem_ind = active_recent_chats.indexOf(new_chat);
        active_recent_chats.splice(elem_ind, 1);
        active_recent_chats.push(new_chat);
        remove_given_chat(active_recent_chats, new_chat);
        // var new_div = append_div(new_chat, recent_chats, "availableChat");
        var new_div = insert_div(new_chat, recent_chats, "availableChat");
        new_div.id = new_chat;
        new_div.onclick = () => {
            chat_change(new_chat);
        }
    }
}


function update_user_list(new_users_array, active_users_element, class_name) {
    console.log("new users number", new_users_array.length);
    for (let n = 0; n < new_users_array.length; n++) {
        let user_name = new_users_array[n];
        let short_name = retrieve_display_login(user_name);
        console.log("updating:", user_name);
        if (!chat_participants.has(user_name)) {
            var child_div = append_div(short_name, active_users_element, class_name);
            child_div.id = user_name;
            chat_participants.add(user_name);
        }
        else if (user_name != login) {
            console.log("removing ", user_name);
            active_users_element.removeChild(document.getElementById(user_name));
            chat_participants.delete(user_name);
        }
        console.log(chat_participants);
    }
}


function chat_change(chat_name) {
    clear_message_element(all_messages_element);
    chat = chat_name;
    chat_name_header.innerHTML = chat;
    chat_destination_element.value = chat;
    localStorage.setItem("active_chat", chat);
    connect(login, chat);
    localStorage.setItem("recent_chats", active_recent_chats);

}


function retrieve_messages(user_name, chat_name, ws) {
    send_websocket("previous_messages", "", user_name, chat_name, ws);
    console.log("retrieving old messages");
}


function assign_read_unread_class(sending_time) {
    if (last_active_in_chat > 0 && sending_time > last_active_in_chat) {
        console.log("assigning class: message messageUnread");
        return "message messageUnread";
    }
    console.log("assigning class: message");
    return "message";
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


function not_blank(variable) {
    if (variable == false) {
        console.log("blank field");
        return false;
    }
    return true;
}


function check_focus() {
    if (document.hasFocus()) {
        return true;
    }
    console.log("no focus");
    return false;
}


function read_message() {
    for (let i = 0; i < unread_messages_ids.length; i++) {
        var div = document.getElementById(unread_messages_ids[i]);
        div.className = "message";
    }
    unread_messages_ids = [];
}


function detect_hyperlink(text) {
    let link_pattern = /(www\.\S+\.\S+|https?:\/\/\S+)/g;
    let links = text.match(link_pattern);
    console.log("LINKS", links);
    var updated_text = text.slice();
    if (links != null) {
        links.forEach(link => {
            if (link.includes("http")) {
                var replace_link = '<a href="' + link + '" target="_blank">' + link + '</a>';
            }
            else {
                var replace_link = '<a href="https://' + link + '" target="_blank">' + link + '</a>';
            }
            updated_text = updated_text.replace(link, replace_link);
        });
    }
    return updated_text;
}


// function append_div_messages(my_name, timestamp, message, message_box_element, class_name) {
//     var div = append_div("", message_box_element, class_name);
//     if (my_name === login) {
//         div.style.float = "right";
//     }
//     let message_header_div = append_div("", div, "messageHeader");
//     let name = retrieve_display_login(my_name);
//     append_div(name, message_header_div, "divAuthor");
//     let date = new Date(timestamp);
//     new_div = append_div(date.toLocaleDateString() + " - " + date.toLocaleTimeString(), message_header_div, "divTimestamp");
//     div.innerHTML += message;
//     return div;
// }


function prepare_image_message(img_as_file, my_name) {
    var reader = new FileReader();
    reader.onload = function (event) {
        var img_str = event.target.result;
        console.log(img_str);

        // var node = all_messages_element.createTextNode(img_as_file);
        var img_elem = document.createElement("img");
        img_elem.className = "message";
        img_elem.width = "300";
        img_elem.height = "150";
        img_elem.src = img_str;

        if (my_name === login) {
            img_elem.style.float = "right";
        }
        let message_header_div = append_div("", img_elem, "messageHeader");
        let name = retrieve_display_login(my_name);
        append_div(name, message_header_div, "divAuthor");
        // let date = new Date(timestamp);
        // new_div = append_div(date.toLocaleDateString() + " - " + date.toLocaleTimeString(), message_header_div, "divTimestamp");

        // img_elem.appendChild(node);
        all_messages_element.appendChild(img_elem)

        // document.getElementById("container").src = event.target.result;
    };
    reader.readAsDataURL(img_as_file);
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
var unread_messages_ids = [];
var chat_participants = new Set();
var leaving_times_dict = {};
var last_active_in_chat = -1;

const LEAVING_LOCAL_STORAGE = "chatbox_stored_leaving_times";


window.onload = function () {
    console.log("onload");
    if (localStorage.getItem("active_user") && localStorage.getItem("active_chat")) {
        let short_name = retrieve_display_login(localStorage.getItem("active_user"));
        my_name_element.value = short_name;
        chat_destination_element.value = localStorage.getItem("active_chat");
        retrieve_recent_chats();
    }
}


connect_button.onclick = () => {
    if (localStorage.getItem("active_user") && my_name_element.value === retrieve_display_login(localStorage.getItem("active_user"))) {
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
    if (event.code === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        message_element.value = message_element.value.replaceAll(/\n/g, "<br>");
        send_button(
            "message",
            message_element,
            login,
            chat,
            webSocket
        );
    }
});


message_element.onpaste = function (e) {
    console.log(e.clipboardData.items);
    var item = e.clipboardData.items[0];
    console.log(item.type.indexOf("image"));

    if (item.type.indexOf("image") === 0) {
        console.log("++++++++++++++++++++++++", item);
        var blob = item.getAsFile();

        prepare_image_message(blob, login);
    }
}


document.addEventListener('click', read_message);
document.addEventListener('keypress', read_message);
