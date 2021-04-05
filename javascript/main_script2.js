function format_sent_message(my_login, value) {
    return `${my_login}: ${value}`;
}


function append_div_messages(my_name, message, message_box_element, class_name) {
    var m = format_sent_message(my_name, message);
    var node = document.createTextNode(m);
    var div = document.createElement("div");
    div.className = class_name;
    if (my_name === login) {
        div.style.float = "right";
    };
    div.appendChild(node);
    message_box_element.appendChild(div);
}


function handle_receive(message, message_box_element, class_name) {
    var m = JSON.parse(message);
    if (m["message_type"] == "message") {
        var name = m["message_sender"];
        var val = m["message_value"];
        append_div_messages(name, val, message_box_element, class_name);
        message_box_element.scrollTo(0, message_box_element.scrollHeight);
    };
}


function send_button(message_type, message_element, my_name, chat_name, websocket) {
    var message = message_element.value;
    console.log(message);
    send_websocket(message_type, message, my_name, chat_name, websocket);
    message_element.value = "";
    console.log('done');
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


function connect(user_name, chat_name) {
    if (user_name != "" && chat_name != "") {
        var url = `ws://${server_address}/${chat_name}/${user_name}`;
        console.log("url", url);
        webSocket = new WebSocket(url);
        webSocket.onopen = () => {
            console.log('opening');
        };
        webSocket.onmessage = (event) => {
            console.log("received");
            console.log(event);
            console.log(event.data);
            handle_receive(event.data, all_messages_element, "message");
        };
    };
}


function add_chat(new_chat, public_chat = true) {
    if (public_chat === true) {
        if (!active_public_chats.includes(new_chat)) {
            active_public_chats.push(new_chat);
            node = document.createTextNode(new_chat);
            new_div = document.createElement("DIV");
            new_div.className = "availableChat";
            new_div.appendChild(node);
            public_chats.appendChild(new_div);
        };
    }
    else {
        if (!active_private_chats.includes(new_chat)) {
            active_private_chats.push(new_chat);
            node = document.createTextNode(new_chat);
            new_div = document.createElement("DIV");
            new_div.className = "availableChat";
            new_div.appendChild(node);
            private_chats.appendChild(new_div);
        };
    };
}


var button_element = document.getElementById("sendMessageButton");
var message_element = document.getElementById("newMessage");
var all_messages_element = document.getElementById("receivedMessages");
var my_name_element = document.getElementById("login");
var choose_name_button = document.getElementById("chooseLoginButton");
var chat_destination_element = document.getElementById("findChat");
var choose_chat_button = document.getElementById("findChatButton");
var chat_name_header = document.getElementById("chatNameHeader");
var public_chats = document.getElementById("publicChats");
var private_chats = document.getElementById("privateChats");

var login = "";
var chat = "";
var server_address = "localhost:11000";
var active_public_chats = [];
var active_private_chats = [];


choose_name_button.onclick = () => {
    login = my_name_element.value;
    console.log(login);
    connect(login, chat);
};


choose_chat_button.onclick = () => {
    chat_name_header.innerHTML = chat_destination_element.value;
    chat = chat_destination_element.value;
    console.log(chat);
    connect(login, chat);
    add_chat(chat);
};


button_element.onclick = () => {
    send_button(
        "message",
        message_element,
        my_name_element.value,
        chat_destination_element.value,
        webSocket
    );
};


message_element.addEventListener("keypress", function (event) {
    if (event.code === 'Enter') {
        send_button(
            "message",
            message_element,
            my_name_element.value,
            chat_destination_element.value,
            webSocket
        );
    };
});
