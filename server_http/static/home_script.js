var my_name_element = document.getElementById("login");
var connect_button = document.getElementById("connectButton");
var chat_destination_element = document.getElementById("findChat");


function store_input() {
    let typed_chat = chat_destination_element.value
    let typed_login = my_name_element.value;

    if (validate_input(typed_login)) {
        let id = generate_random_string(ID_LENGTH);
        let username = typed_login + id;
        localStorage.setItem(ACTIVE_USER_STORAGE, username);
    } else {
        return false
    }

    if (validate_input(typed_chat) === true) {
        localStorage.setItem(ACTIVE_CHAT_STORAGE, typed_chat);
    } else {
        return false
    }
    return true
}


function retrieve_stored_recent_chats() {
    let stored_chats = localStorage.getItem(RECENT_CHATS_STORAGE);
    let stored_chats_array = stored_chats.split(",");
    if (stored_chats_array) {
        for (let i = 0; i < stored_chats_array.length; i++) {
            display_recent_chat(stored_chats_array[i]);
        }
    }
}

function display_recent_chat(new_chat) {
    let recent_chats_elem = document.getElementById("recentChatsList");
    let new_div = add_element(new_chat, recent_chats_elem, "recentChat", true, "button");
    new_div.id = new_chat;
    new_div.onclick = () => {
        update_stored_chats(new_chat);
        open_chat_page(new_chat);
    }
}


function update_stored_chats(new_chat) {
    let stored_chats = localStorage.getItem(RECENT_CHATS_STORAGE);
    var stored_chats_array = stored_chats.split(",");
    if (!stored_chats_array.includes(new_chat)) {
        stored_chats_array.push(new_chat);
    }
    else if (stored_chats_array.includes(new_chat) && stored_chats_array.indexOf(new_chat) != stored_chats_array.length - 1) {
        var elem_ind = stored_chats_array.indexOf(new_chat);
        stored_chats_array.splice(elem_ind, 1);
        stored_chats_array.push(new_chat);
    }
    let updated_chats_to_store = stored_chats_array.join();
    localStorage.setItem(RECENT_CHATS_STORAGE, updated_chats_to_store);
}


window.onload = function () {
    let full_user_name = localStorage.getItem(ACTIVE_USER_STORAGE);
    let short_name;

    if (full_user_name) {
        short_name = retrieve_display_login(full_user_name);
    }

    my_name_element.value = short_name;

    disable_button(BUTTON_CONNECT);
    retrieve_stored_recent_chats();
}


document.onkeyup = (e) => {
    if (e.code === 'Enter') {
        store_input()
        open_chat_page(chat_destination_element.value);
    }
}


connect_button.onclick = () => {
    store_input()
    open_chat_page(chat_destination_element.value);
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