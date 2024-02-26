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
    let name = user_name.slice(0, -ID_LENGTH);
    console.log("retrieving user name:", name);
    return name;
}


function disable_button(text = BUTTON_CONNECTED) {
    connect_button.innerHTML = text;
    connect_button.style.opacity = 0.5;
    connect_button.disabled = true;
}


function enable_button(text = BUTTON_CONNECT) {
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
    console.log('***is_unchanged***', typeof (typed_login), typeof (typed_chat));
    return typed_login.slice(0, -ID_LENGTH) && typed_chat === chat;
}


function inspect_inputs_updates(typed_login, typed_chat, login_elem, chat_elem, key_event) {
    if (is_unchanged(typed_login, typed_chat)) {
        mark_correct_input(login_elem);
        mark_correct_input(chat_elem);
        disable_button();

    } else if (typed_login.length === 0 || typed_chat.length === 0) {
        disable_button(BUTTON_CONNECT);
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
                window.location.href = open_chat_page(chat_elem.value);
            }

        } else if (!valid_login && !valid_chat) {
            mark_incorrect_input(login_elem);
            mark_incorrect_input(chat_elem);
            disable_button(BUTTON_CONNECT);

        } else if (!valid_login) {
            mark_incorrect_input(login_elem);
            mark_correct_input(chat_elem);
            disable_button(BUTTON_CONNECT);

        } else if (!valid_chat) {
            mark_incorrect_input(chat_elem);
            mark_correct_input(login_elem);
            disable_button(BUTTON_CONNECT);
        }
    }
}

function open_chat_page(destination_chat) {
    if (validate_input(destination_chat)) {
        window.location.href = `${window.location.origin}/chat/${destination_chat}`;
    }
}
