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
    send_websocket(message, my_name, chat_name, websocket);
    message_element.value = "";
    console.log('done');
}

var button_element = document.getElementById("send_button_id");
var message_element = document.getElementById("message_id");
var all_messages_element = document.getElementById("all_messages_id");
var my_name_element = document.getElementById("your_login_id");
var chat_destination_element = document.getElementById("receiver_login_id");
var connect_button_element = document.getElementById("connect_button_id");
var server_address_element = document.getElementById("server_address_id");

var webSocket = null;
my_name_element.value = "alpaczino" + Math.ceil(Math.random() * 1000);

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
    login = my_name_element.value;
    chat_name = chat_destination_element.value;
    var url = `ws://${server_address_element.value}/${chat_name}/${login}`;
    console.log("url", url);
    console.log(login, chat_name)
    webSocket = new WebSocket(url);
    webSocket.onopen = () => {
        console.log('opening');
    };
    webSocket.onmessage = (event) => {
        console.log("received");
        console.log(event);
        console.log(event.data);
        handle_receive(event.data, all_messages_element);
    };
};
