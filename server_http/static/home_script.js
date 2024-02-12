const ACTIVE_USER_STORAGE = "chatbox_stored_active_user";
const ACTIVE_CHAT_STORAGE = "chatbox_stored_active_chat";
const INCORRECT_INPUT_CLASS = "incorrectInput";
const MAX_INPUT_LENGTH = 20;
const DEFAULT_CHAT_NAME = "WelcomeInChatBox";

var my_name_element = document.getElementById("login");
var connect_button = document.getElementById("connectButton");
var chat_destination_element = document.getElementById("findChat");
var id_length = 20;


function join_chat() {
    let typed_chat = chat_destination_element.value
    let typed_login = my_name_element.value;

    if (validate_input(typed_login)) {
        let id = generate_random_string(id_length);
        let username = typed_login + id;
        localStorage.setItem(ACTIVE_USER_STORAGE, username);
    }

    if (validate_input(typed_chat) === true) {
        localStorage.setItem(ACTIVE_CHAT_STORAGE, typed_chat);
    }
}


window.onload = function () {
    let full_user_name = localStorage.getItem(ACTIVE_USER_STORAGE);
    let short_name;

    if (full_user_name) {
        short_name = retrieve_display_login(full_user_name);
    }

    my_name_element.value = short_name;

    disable_button("Connect");
}


window.onbeforeunload = () => {
    join_chat()
}


connect_button.onclick = () => {
    console.log("clicking connect");
    window.location.href = `${window.location.origin}/chat/${chat_destination_element.value}`;
}


my_name_element.onkeyup = (e) => {
    let typed_login = my_name_element.value;
    let typed_chat = chat_destination_element.value;

    inspect_inputs_updates(typed_login, typed_chat, my_name_element, chat_destination_element, e);
}


chat_destination_element.onkeyup = (e) => {
    let typed_login = my_name_element.value;
    let typed_chat = chat_destination_element.value;

    inspect_inputs_updates(typed_login, typed_chat, my_name_element, chat_destination_element, e);
}