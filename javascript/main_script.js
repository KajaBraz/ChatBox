function format_sent_message(my_login, value) {
    return `${my_login}: ${value}`;
}

function append_div_messages(my_name, message, message_box_element) {
    var m = format_sent_message(my_name, message);
    var node = document.createTextNode(m);
    var div = document.createElement("div");
    div.appendChild(node);
    message_box_element.appendChild(div);
}

function send_websocket(message, sender, chat_destination, websocket) {
    var json_message = {
        message_type: "message",
        message_value: message,
        message_destination: chat_destination,
        message_sender: sender
    };
    console.log(json_message);
    websocket.send(JSON.stringify(json_message));
}

function handle_receive(message, message_box_element) {
    // todo fix 'ok' after successful login
    var m = JSON.parse(message);
    if(m["message_type"] == "message") {
        var name = m["message_sender"];
        var val = m["message_value"];
        var formatted = format_sent_message(name, val);
        append_div_messages(name, val, message_box_element);
    }
}

function send_button(message_element, message_box_element, my_name, chat_name, websocket) {
    var message = message_element.value;
    console.log(message);
    append_div_messages(my_name, message, message_box_element);
    send_websocket(message, my_name, chat_name, websocket);
    message_element.value = "";
    console.log('done');
}

function log_in(websocket, my_login) {
    console.log("begin login");
    var login_json = {
        message_type: "user_login",
        message_value: my_login
    };
    websocket.send(JSON.stringify(login_json));
    console.log("login request sent");
}

var button_element = document.getElementById("send_button_id");
var message_element = document.getElementById("message_id");
var all_messages_element = document.getElementById("all_messages_id");
var my_name_element = document.getElementById("your_login_id");
var chat_destination_element = document.getElementById("receiver_login_id");
var connect_button_element = document.getElementById("connect_button_id");
var server_address_element = document.getElementById("server_address_id");

var webSocket = null;

button_element.onclick = () => {
    send_button(
        message_element,
        all_messages_element,
        my_name_element.value,
        chat_destination_element.value,
        webSocket
    );
};

connect_button_element.onclick = () => {
    var url = `ws://${server_address_element.value}/psiaki`;
    console.log("url", url);
    webSocket = new WebSocket(url);
    webSocket.onopen = () => {
        console.log('opening');
        log_in(webSocket, my_name_element.value);
    };
    webSocket.onmessage = (event) => {
        console.log("received");
        console.log(event);
        console.log(event.data);
        handle_receive(event.data, all_messages_element);
    };
};
