function append_div_messages(append_insert_func, my_name, timestamp, message, message_box_element, class_name, as_first_div = false) {
    var div = append_insert_func("", message_box_element, class_name, as_first_div);
    if (my_name === login) {
        div.style.float = "right";
    } else {
        div.style.float = "left";
    }
    let message_header_div = add_element("", div, "messageHeader");
    let name = retrieve_display_login(my_name);
    add_element(name, message_header_div, "divAuthor");
    let date = new Date(timestamp);
    let timestamp_div = add_element(`${date.toLocaleDateString()} - ${date.toLocaleTimeString()}`, message_header_div, "divTimestamp");
    let message_text_div = add_element(message, div, "messageText");
    return div;
}


function add_element(text, parent, class_name, as_first = false, tag = 'div') {
    var elem = document.createElement(tag);
    elem.className = class_name;
    elem.innerHTML = text;
    if (!as_first) {
        parent.appendChild(elem);
    } else {
        parent.insertBefore(elem, parent.firstChild);
    }
    return elem;
}


function handle_receive(message, message_box_element, class_name) {
    var m = JSON.parse(message);
    if (m["message_type"] == "message") {
        val = m["message_value"];
        var name = val["sender_login"];
        var message_text = detect_hyperlink(val["message"]);
        var timestamp = val["timestamp"];
        console.log('message val', message_text);
        var new_message = append_div_messages(add_element, name, timestamp, message_text, message_box_element, class_name);
        new_message.id = val["id"];
        message_box_element.scrollTo(0, message_box_element.scrollHeight);
        if (class_name === "message messageUnread") {
            unread_messages_ids.push(new_message.id);
            console.log("unread messages pushed:", unread_messages_ids);
        }
        adjust_displayed_messages();
        if (!check_focus()) {
            new_msgs_count++;
            activate_on_message();
        }
    }
    else if (m["message_type"] == "previous_messages") {
        m["multiple_messages"].forEach(single_message => {
            var name = single_message["sender_login"];
            var message_text = detect_hyperlink(single_message["message"]);
            var timestamp = single_message["timestamp"];
            var status = assign_read_unread_class(single_message["id"]);
            var new_message = append_div_messages(add_element, name, timestamp, message_text, message_box_element, status);
            new_message.id = single_message["id"];
            message_box_element.scrollTo(0, message_box_element.scrollHeight);
            if (status === "message messageUnread") {
                unread_messages_ids.push(new_message.id);
                console.log("unread messages pushed:", unread_messages_ids);
            }
        })
    }
    else if (m["message_type"] == "more_previous_messages") {
        messages_array = m["multiple_messages"].reverse();
        console.log('QQ MORE PREVIOUS');
        console.log(messages_array);
        messages_array.forEach(single_message => {
            var name = single_message["sender_login"];
            var message_text = detect_hyperlink(single_message["message"]);
            var timestamp = single_message["timestamp"];
            var status = assign_read_unread_class(single_message["id"]);
            var new_message = append_div_messages(add_element, name, timestamp, message_text, message_box_element, status, true);
            new_message.id = single_message["id"];
            message_box_element.scrollTo(0, message_box_element.offsetHeight);
            if (status === "message messageUnread") {
                unread_messages_ids.push(new_message.id);
                console.log("unread messages pushed:", unread_messages_ids);
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


function generate_random_string(n) {
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
            let stored_msg_id = localStorage.getItem(LAST_MSG_IDS_STORAGE);
            if (stored_msg_id) {
                last_msg_ids_dict = JSON.parse(stored_msg_id);
            }
            console.log("retrieved messages ids", last_msg_ids_dict);

            if (chat_name in last_msg_ids_dict) {
                last_seen_message_id = last_msg_ids_dict[chat_name];
            }
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
        webSocket.onerror = (e) => {
            console.log('ws error');
        };
    }
}


function store_last_msgs_ids() {
    console.log('storing last message id');
    if (all_messages_element.children.length) {
        last_seen_message_id = all_messages_element.lastChild.id;
        console.log('storing', chat, last_seen_message_id);
        last_msg_ids_dict[chat] = last_seen_message_id;
        console.log("saved dict: last message ids", last_msg_ids_dict);
        let last_msg_ids_json = JSON.stringify(last_msg_ids_dict);
        localStorage.setItem(LAST_MSG_IDS_STORAGE, last_msg_ids_json);
        last_seen_message_id = -1;
    } else {
        console.log('no messages detected; nothing stored');
    }
    clear_message_element(all_messages_element);
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
        // var new_div = add_div(new_chat, recent_chats, "availableChat");
        var new_div = add_element(new_chat, recent_chats, "availableChat", true, "button");
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
        // var new_div = add_div(new_chat, recent_chats, "availableChat");
        var new_div = add_element(new_chat, recent_chats, "availableChat", true, "button");
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
            var child_div = add_element(short_name, active_users_element, class_name, null);
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


function chat_change(new_chat) {
    console.log(`chat_change: old - ${chat}; new - ${new_chat}`);
    leave_chat(chat);
    enter_chat(new_chat);
    window.location.href = `${window.location.origin}/chat/${new_chat}`;
}


function leave_chat(old_chat) {
    store_last_msgs_ids();
    if (validate_input(old_chat) === true) {
        localStorage.setItem(ACTIVE_CHAT_STORAGE, old_chat);
    }
    localStorage.setItem(RECENT_CHATS_STORAGE, active_recent_chats);
}


function enter_chat(new_chat) {
    chat = new_chat;
    chat_name_header.innerHTML = chat;
    chat_destination_element.value = chat;
}


function retrieve_messages(user_name, chat_name, ws) {
    if (all_messages_element.children.length) {
        var from_id = all_messages_element.firstChild.id;
        var mes_type = "more_previous_messages"
    } else {
        var from_id = -1;
        var mes_type = "previous_messages";
    }
    console.log("from id", from_id, mes_type);
    send_websocket(mes_type, from_id, user_name, chat_name, ws);
    console.log("retrieving old messages");
}


function assign_read_unread_class(msg_id) {
    if (last_seen_message_id != -1 && last_seen_message_id < msg_id) {
        console.log("assigning class: message messageUnread");
        return "message messageUnread";
    }
    console.log("assigning class: message");
    return "message";
}


function retrieve_recent_chats() {
    recently_used_chats = localStorage.getItem(RECENT_CHATS_STORAGE);
    if (recently_used_chats) {
        recently_used_chats = recently_used_chats.split(",");
        console.log(recently_used_chats);
        for (let i = 0; i < recently_used_chats.length; i++) {
            add_chat(recently_used_chats[i]);
        }
    }
}


function clear_message_element(message_box) {
    all_messages_element.removeEventListener('scroll', activate_scroll_event);
    while (message_box.firstChild) {
        message_box.removeChild(message_box.firstChild);
    }
    setTimeout(() => {
        all_messages_element.addEventListener('scroll', activate_scroll_event);
        activate_scroll_event();
    }, 100);
}


function not_blank(variable) {
    if (variable === false) {
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
        console.log("qqq READING - READING - READING");
    }
    unread_messages_ids = [];
}


function activate_on_message() {
    audio.play();
    document.title = (`${TAB_TITLE} - New Messages (${new_msgs_count})`);
}


function deactivate_on_focus() {
    document.title = TAB_TITLE;
    new_msgs_count = 0;
}


function detect_hyperlink(text) {
    let link_pattern = /(www\.\S+\.\S+|https?:\/\/\S+)/g;
    let links = text.match(link_pattern);
    console.log("LINKS", links);
    var updated_text = text.slice();
    if (links != null) {
        links.forEach(link => {
            if (link.includes("http")) {
                // var replace_link = '<a href="' + link + '" target="_blank">' + link + '</a>';
                var replace_link = `<a href="${link}" target="_blank">${link}</a>`;
            }
            else {
                var replace_link = `<a href="https://${link}" target="_blank">${link}</a>`;
                // var replace_link = '<a href="https://' + link + '" target="_blank">' + link + '</a>';
            }
            updated_text = updated_text.replace(link, replace_link);
        });
    }
    console.log('***', updated_text);
    return updated_text;
}


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
        let message_header_div = add_element("", img_elem, "messageHeader");
        let name = retrieve_display_login(my_name);
        add_element(name, message_header_div, "divAuthor");
        // let date = new Date(timestamp);
        // new_div = add_div(date.toLocaleDateString() + " - " + date.toLocaleTimeString(), message_header_div, "divTimestamp");

        // img_elem.appendChild(node);
        all_messages_element.appendChild(img_elem)

        // document.getElementById("container").src = event.target.result;
    };
    reader.readAsDataURL(img_as_file);
}


function activate_scroll_event(scroll_event = null) {
    if (scroll_event) {
        var elem = scroll_event.target;
    } else {
        var elem = all_messages_element;
    }
    if (elem.scrollTop === 0) {
        retrieve_messages(login, chat, webSocket);
    }
}


function adjust_displayed_messages() {
    console.log('removing or not', all_messages_element.children.length);
    while (all_messages_element.children.length > MAX_MSGS_ON_PAGE_NUM) {
        console.log(all_messages_element.childNodes[0], 'removing')
        all_messages_element.removeChild(all_messages_element.childNodes[0]);
    }
}


function update_save_login() {
    let typed_login = my_name_element.value;
    if (validate_input(typed_login)) {
        let id = generate_random_string(id_length);
        let username = typed_login + id;
        localStorage.setItem(ACTIVE_USER_STORAGE, username);
        return (true, username);
    }
    return (false, username);
}


function activate_actions_on_entering_chat() {
    if (validate_input(chat_destination_element.value)) {
        enter_chat(chat_destination_element.value)
    } else {
        enter_chat(DEFAULT_CHAT_NAME);
    }

    connect(login, chat);
    add_chat(chat);
    console.log(login, chat);

    disable_button();
}


function copy_chat_url() {
    let chat_url = window.location.href;
    navigator.clipboard.writeText(chat_url);
}


function disable_button(text = "Connected") {
    connect_button.innerHTML = text;
    connect_button.style.opacity = 0.5;
    connect_button.disabled = true;
}


function enable_button(text = "Connect") {
    connect_button.innerHTML = text;
    connect_button.style.opacity = 1;
    connect_button.disabled = false;
}


function check_input_characters(text) {
    text = text.replaceAll('-', '').replaceAll('_', '');

    if (text.length === 0) {
        return false;
    }

    return Array.from(text).every(is_alnum);
}

function is_alnum(char) {
    if (!is_simple_alnum(char)) {
        return check_diacritics(char);
    }
    return true;
}

function is_simple_alnum(char) {
    let char_code = char.charCodeAt(0);
    if ((char_code > 47 && char_code < 58) || // numeric (0-9)
        (char_code > 64 && char_code < 91) || // upper alpha (A-Z)
        (char_code > 96 && char_code < 123)   // lower alpha (a-z)
    ) {
        return true;
    }
    return false;
}

function check_diacritics(char) {
    let decomposed = Array.from(char.normalize('NFD'));
    return is_simple_alnum(decomposed[0]);
}

function check_input_length(text, max_length) {
    if (text.length > max_length) {
        return false;
    }
    return true;
}


function validate_input(text, max_length) {
    return check_input_length(text, max_length) && check_input_characters(text);
}


function mark_incorrect_input(box) {
    box.classList.add(INCORRECT_INPUT_CLASS);
}


function mark_correct_input(box) {
    box.classList.remove(INCORRECT_INPUT_CLASS);
}


function is_unchanged(typed_login, typed_chat) {
    return typed_login === login.slice(0, -id_length) && typed_chat === chat;
}


function inspect_inputs_updates(typed_login, typed_chat, login_elem, chat_elem, key_event) {
    if (is_unchanged(typed_login, typed_chat)) {
        mark_correct_input(login_elem);
        mark_correct_input(chat_elem);
        disable_button();

    } else if (typed_login.length === 0 || typed_chat.length === 0) {
        disable_button('Connect');
        if (typed_login.length === 0) {
            mark_correct_input(login_elem);
        }
        if (typed_chat.length === 0) {
            mark_correct_input(chat_elem);
        }

    } else {
        let valid_login = validate_input(typed_login, MAX_INPUT_LENGTH);
        let valid_chat = validate_input(typed_chat, MAX_INPUT_LENGTH);

        if (valid_login && valid_chat) {
            mark_correct_input(login_elem);
            mark_correct_input(chat_elem);
            enable_button();

            if (key_event.code == 'Enter') {
                window.location.href = `${window.location.origin}/chat/${chat_elem.value}`;
            }

        } else if (!valid_login && !valid_chat) {
            mark_incorrect_input(login_elem);
            mark_incorrect_input(chat_elem);
            disable_button('Connect');

        } else if (!valid_login) {
            mark_incorrect_input(login_elem);
            mark_correct_input(chat_elem);
            disable_button('Connect');

        } else if (!valid_chat) {
            mark_incorrect_input(chat_elem);
            mark_correct_input(login_elem);
            disable_button('Connect');
        }
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
var share_button = document.querySelector("#clipboard");

var login = "";
var chat = "";
var server_address = "localhost:11000";
var webSocket = null;
var id_length = 20;
var active_recent_chats = [];
var recently_used_chats = [];
var unread_messages_ids = [];
var chat_participants = new Set();
var last_msg_ids_dict = {};
var last_seen_message_id = -1;
var new_msgs_count = 0;


const LAST_MSG_IDS_STORAGE = "chatbox_stored_last_msg_ids";
const ACTIVE_CHAT_STORAGE = "chatbox_stored_active_chat";
const ACTIVE_USER_STORAGE = "chatbox_stored_active_user";
const RECENT_CHATS_STORAGE = "chatbox_stored_recent_chats";
const MAX_MSGS_ON_PAGE_NUM = 20;
const TAB_TITLE = 'ChatBox';
const audio = document.getElementById('audioSheep');
const INCORRECT_INPUT_CLASS = "incorrectInput";
const MAX_INPUT_LENGTH = 20;
const DEFAULT_CHAT_NAME = "WelcomeInChatBox";


window.onload = function () {
    let full_user_name = localStorage.getItem(ACTIVE_USER_STORAGE);
    let short_name;
    let user_id;

    if (full_user_name) {
        short_name = retrieve_display_login(full_user_name);
    } else {
        short_name = generate_random_string(5);
        user_id = generate_random_string(id_length);
        full_user_name = short_name + user_id
    }

    my_name_element.value = short_name;
    login = full_user_name;

    retrieve_recent_chats();
    activate_actions_on_entering_chat();
}


window.onbeforeunload = () => {
    store_last_msgs_ids();
    update_save_login();
}


window.onunload = function () {
    webSocket.close(1000);
}


connect_button.onclick = () => {
    chat_change(chat_destination_element.value);
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


share_button.onclick = copy_chat_url;

all_messages_element.addEventListener('scroll', activate_scroll_event);
document.addEventListener('click', read_message);
document.addEventListener('keypress', read_message);

document.onclick = deactivate_on_focus;
document.onkeydown = deactivate_on_focus;

// todo fix special characters (e.g., "_") in chat names which are displayed but break active users list
// todo fix active users in Firefox
