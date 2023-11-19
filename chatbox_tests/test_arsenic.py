import asyncio
import multiprocessing
import os.path
from typing import Union

import arsenic
import pytest
import pytest_asyncio
from arsenic import keys

from chatbox_tests import mocked_database, arsenic_tests_helpers
from src import helper_functions, chatbox_websocket_server, enums


class User:
    def __init__(self):
        self.chat_room = helper_functions.generate_random_string(10)
        self.user_name = ''
        self.session: Union[arsenic.Session, None] = None
        self.headless = True
        self.timeout = 20


@pytest_asyncio.fixture
async def chatbox_server():
    config_relative_path = os.path.join('chatbox_tests', 'chatbox_tests_config.json')
    config_absolute_path = os.path.abspath(config_relative_path)
    data = helper_functions.read_config(config_absolute_path)
    address = data['address']['name']
    port = data['address']['port']
    server = chatbox_websocket_server.Server(data)
    server.chatbox_database = mocked_database.MockedDatabase()
    await server.start(address, port)

    yield
    server.stop()
    await server.wait_stop()


@pytest_asyncio.fixture
async def http_server():
    p = multiprocessing.Process(target=arsenic_tests_helpers.run_http_server)
    p.start()

    yield
    p.terminate()

    # make sure there's enough time between server's stop / start (to avoid tests failures) 
    await asyncio.sleep(2)


@pytest_asyncio.fixture
async def user():
    client = User()
    client.session = await arsenic_tests_helpers.create_session(client.chat_room, client.headless)
    client.user_name = await arsenic_tests_helpers.get_login_input_value(client.session)

    yield client
    if client.session:
        await arsenic.stop_session(client.session)


@pytest.mark.asyncio
async def test_open_chatbox_default_link(chatbox_server, http_server):
    default_chat_name = enums.Constants.DEFAULT_CHAT_NAME
    session1 = await arsenic.start_session(arsenic.services.Geckodriver(),
                                           arsenic.browsers.Firefox(**{'moz:firefoxOptions': {'args': ['-headless']}}))
    session2 = await arsenic.start_session(arsenic.services.Geckodriver(),
                                           arsenic.browsers.Firefox(**{'moz:firefoxOptions': {'args': ['-headless']}}))
    await session1.get(f'localhost:5000/')
    await session2.get(f'localhost:5000/chat/')

    for session in [session1, session2]:
        await session.wait_for_element(20, '.gridContainer')
        chat_elem = await session.get_element('#findChat')
        displayed_url = await session.get_url()
        header_elem = await session.get_element('#chatNameHeader')
        chat_list_elem = await session.get_element('#recentlyUsedChats')
        displayed_chat = await chat_list_elem.get_element(f'#{default_chat_name}')
        active_users = await session.get_element('#activeUsers')
        login = await arsenic_tests_helpers.get_login_input_value(session)

        assert await chat_elem.get_attribute('value') == default_chat_name
        assert await header_elem.get_text() == default_chat_name
        assert await displayed_chat.get_text() == default_chat_name
        assert default_chat_name not in displayed_url
        assert login != ''
        assert login in await active_users.get_text()

    await arsenic.stop_session(session1)
    await arsenic.stop_session(session2)


@pytest.mark.asyncio
async def test_open_chatbox_chat_link(chatbox_server, http_server, user):
    chat_elem = await user.session.get_element('#findChat')
    displayed_url = await user.session.get_url()
    header_elem = await user.session.get_element('#chatNameHeader')
    chat_list_elem = await user.session.get_element('#recentlyUsedChats')
    displayed_chat = await chat_list_elem.get_element(f'#{user.chat_room}')

    assert await chat_elem.get_attribute('value') == user.chat_room
    assert await header_elem.get_text() == user.chat_room
    assert await displayed_chat.get_text() == user.chat_room
    assert user.chat_room in displayed_url


@pytest.mark.asyncio
async def test_connect_with_button(chatbox_server, http_server, user):
    new_login = helper_functions.generate_random_string(5)
    new_chat = helper_functions.generate_random_string(5)
    await arsenic_tests_helpers.connect_user(user.session, new_login, new_chat)

    header_elem = await user.session.get_element('#chatNameHeader')
    recent_chat_1 = await user.session.get_element(f'#{new_chat}')
    recent_chat_2 = await user.session.get_element(f'#{user.chat_room}')
    recent_chat_1 = await recent_chat_1.get_text()
    recent_chat_2 = await recent_chat_2.get_text()
    displayed_user = await user.session.get_element('#activeUsers')

    assert await header_elem.get_text() == new_chat
    assert {recent_chat_1, recent_chat_2} == {user.chat_room, new_chat}
    assert await displayed_user.get_text() == new_login


@pytest.mark.asyncio
async def test_sending_and_displaying_messages(chatbox_server, http_server, user):
    new_message_box = await user.session.get_element('#newMessage')
    send_button = await user.session.get_element('#sendMessageButton')

    # SEND MESSAGES
    messages = [helper_functions.generate_random_string(15) for _ in range(5)]
    for message in messages:
        await new_message_box.send_keys(message)
        await send_button.click()

    # CHECK RECEIVED MESSAGES
    received_messages_box = await user.session.get_element('#receivedMessages')
    received_messages = [await m.get_text() for m in await received_messages_box.get_elements('.messageText')]
    assert messages == received_messages


@pytest.mark.asyncio
async def test_recent_chats_display(chatbox_server, http_server, user):
    chat_names = [helper_functions.generate_random_string(10) for _ in range(4)]
    for chat_name in chat_names:
        await arsenic_tests_helpers.connect_user(user.session, user.user_name, chat_name)
    resulting_chat_names = [await elem.get_text() for elem in await user.session.get_elements('.availableChat')]
    assert chat_names[::-1] + [user.chat_room] == resulting_chat_names


@pytest.mark.asyncio
async def test_active_users_display(chatbox_server, http_server, user):
    await arsenic_tests_helpers.connect_user(user.session, user.user_name)
    # todo fix the below version to open tabs instead of new windows
    active_users = await user.session.get_element('#activeUsers')
    assert user.user_name == await active_users.get_text()

    new_users = {helper_functions.generate_random_string(10) for _ in range(4)}
    new_sessions = set()
    temp_users = {user.user_name}
    temp_drivers = {user.session}

    for new_user in new_users:
        new_session = await arsenic_tests_helpers.create_session(user.chat_room, user.headless)
        await arsenic_tests_helpers.connect_user(new_session, new_user)
        # todo refactor connect_user and make user/chat optional
        new_sessions.add(new_session)
        temp_users.add(new_user)
        temp_drivers.add(new_session)
        temp_active_users_elems = [await dr.get_element('#activeUsers') for dr in temp_drivers]
        temp_active_users = [await active_users_elem.get_text() for active_users_elem in temp_active_users_elems]
        assert all((temp_user in displayed for temp_user in temp_users) for displayed in temp_active_users)
        # Temporary solution until Active Users are displayed as buttons

    # todo, temporary to remove, use separate windows instead, not drivers
    for ns in new_sessions:
        await arsenic.stop_session(ns)


@pytest.mark.asyncio
async def test_messages_position(chatbox_server, http_server, user):
    # CONNECT USER 2
    user2 = helper_functions.generate_random_string(5)
    new_session = await arsenic_tests_helpers.create_session(headless=user.headless)
    await arsenic_tests_helpers.connect_user(new_session, user2, user.chat_room)

    # PREPARE MESSAGES USER1
    messages_user1 = [helper_functions.generate_random_string(15) for _ in range(2)]
    new_message_box_user1 = await user.session.get_element('#newMessage')
    send_button_user1 = await user.session.get_element('#sendMessageButton')

    # PREPARE MESSAGES USER2
    messages_user2 = [helper_functions.generate_random_string(15) for _ in range(2)]
    new_message_box_user2 = await new_session.get_element('#newMessage')
    send_button_user2 = await new_session.get_element('#sendMessageButton')

    # SEND MESSAGES
    await new_message_box_user1.send_keys(messages_user1[0])
    await send_button_user1.click()

    await new_message_box_user2.send_keys(messages_user2[0])
    await send_button_user2.click()

    await new_message_box_user1.send_keys(messages_user1[1])
    await send_button_user1.click()

    await new_message_box_user2.send_keys(messages_user2[1])
    await send_button_user2.click()

    # GATHER MESSAGES
    await new_message_box_user1.click()
    await new_message_box_user2.click()
    received_messages_user1 = await user.session.get_elements('.message')
    received_messages_user2 = await new_session.get_elements('.message')

    # CHECK MESSAGES STYLE
    messages_style_user1 = [await m.get_attribute('style') for m in received_messages_user1]
    messages_style_user2 = [await m.get_attribute('style') for m in received_messages_user2]

    assert all(['right' in messages_style_user1[i] for i in range(len(messages_style_user1)) if i % 2 == 0])
    assert all(['right' in messages_style_user2[i] for i in range(len(messages_style_user2)) if i % 2 == 1])
    assert all(['left' in messages_style_user1[i] for i in range(len(messages_style_user1)) if i % 2 == 1])
    assert all(['left' in messages_style_user2[i] for i in range(len(messages_style_user2)) if i % 2 == 0])

    # todo temporary, to remove, make seperate windows not drivers
    await arsenic.stop_session(new_session)


@pytest.mark.asyncio
async def test_previous_messages(chatbox_server, http_server, user):
    messages_displayed_on_connection = 10

    # USER 1 SENDS MESSAGES
    messages = [helper_functions.generate_random_string(5) for _ in range(25)]
    new_msg_box = await user.session.get_element('#newMessage')
    send_button = await user.session.get_element('#sendMessageButton')

    for i in range(len(messages)):
        await new_msg_box.clear()
        await new_msg_box.send_keys(messages[i])
        await send_button.click()
        await user.session.wait_for_element(user.timeout, f'[id="{i}"]')

    # USER CHANGES LOGIN AND CONNECTS
    new_login = helper_functions.generate_random_string(5)
    await arsenic_tests_helpers.connect_user(user.session, new_login)
    await user.session.wait_for_element(user.timeout, f'[id="{len(messages) - 1}"]')
    received_messages_box = await user.session.get_element('#receivedMessages')
    displayed_messaged_on_connection = await received_messages_box.get_elements('.messageText')
    displayed_messaged_on_connection = [await m.get_text() for m in displayed_messaged_on_connection]

    assert messages[-messages_displayed_on_connection:] == displayed_messaged_on_connection
    await user.session.execute_script("receivedMessages.scrollTo(0, -receivedMessages.offsetHeight)")
    displayed_messaged_on_connection_after_scoll = await received_messages_box.get_elements('.messageText')
    displayed_messaged_on_connection_after_scoll = [await m.get_text() for m in
                                                    displayed_messaged_on_connection_after_scoll]
    assert messages[-messages_displayed_on_connection * 2:] == displayed_messaged_on_connection_after_scoll


@pytest.mark.asyncio
async def test_adjust_number_of_displayed_messages(chatbox_server, http_server, user):
    # works for max num of messgaes in messages box set to 20
    max_msgs_on_page_num = 20

    received_messages_box = await user.session.get_element('#receivedMessages')
    new_message_box = await user.session.get_element('#newMessage')
    send_button = await user.session.get_element('#sendMessageButton')

    messages = [helper_functions.generate_random_string(5) for _ in range(25)]
    for message in messages[:max_msgs_on_page_num]:
        await new_message_box.send_keys(message)
        await send_button.click()

    displayed_messages = await received_messages_box.get_elements('.messageText')
    assert len(displayed_messages) == max_msgs_on_page_num
    assert messages[:max_msgs_on_page_num] == [await m.get_text() for m in displayed_messages]

    i_start = 1
    for message in messages[max_msgs_on_page_num:]:
        await new_message_box.send_keys(message)
        await send_button.click()

        displayed_messages = await received_messages_box.get_elements('.messageText')
        assert len(displayed_messages) == max_msgs_on_page_num
        assert messages[i_start:i_start + max_msgs_on_page_num] == [await m.get_text() for m in displayed_messages]
        i_start += 1


@pytest.mark.asyncio
async def test_send_and_open_link(chatbox_server, http_server, user):
    message_1 = 'www.rai.it'
    message_2 = 'https://www.gazzetta.it/Calcio/Serie-A/Napoli/' \
                '04-05-2023/scudetto-napoli-campione-d-italia-la-terza-volta-4601354295987.shtml'
    new_message_box = await user.session.get_element('#newMessage')
    send_button = await user.session.get_element('#sendMessageButton')

    # SEND MESSAGES
    await new_message_box.send_keys(message_1)
    await send_button.click()
    await new_message_box.send_keys(message_2)
    await send_button.click()

    # CLICK LINKS
    messages = await user.session.get_elements('a')
    await messages[-1].click()
    await messages[-2].click()

    assert len(await user.session.get_window_handles()) == 3

    # SEND MESSAGE
    message_3 = 'abc abc https://www.italia.it/it/sicilia/agrigento abc abc'
    await new_message_box.send_keys(message_3)
    await send_button.click()

    # CLICK LINKS
    a = await user.session.get_elements('a')
    await a[-1].click()

    assert len(await user.session.get_window_handles()) == 4


@pytest.mark.asyncio
async def test_copy_to_clipboard(chatbox_server, http_server, user):
    # COPY
    copy_elem = await user.session.get_element('#clipboard')
    await copy_elem.click()

    # PASTE
    new_message_box = await user.session.get_element('#newMessage')
    await new_message_box.send_keys(f'{keys.CONTROL}v')

    # VERIFY COPIED TEXT
    pasted_message = await user.session.execute_script('return document.querySelector("#newMessage").value')
    assert pasted_message == f'http://localhost:5000/chat/{user.chat_room}'


@pytest.mark.asyncio
async def test_connect_button(chatbox_server, http_server, user):
    # VERIFY BUTTON ON CONNECTION
    connect_button = await user.session.get_element('#connectButton')
    button_text = await connect_button.get_text()

    assert await connect_button.is_enabled() is False
    assert button_text == 'Connected'

    # CHANGE USER NAME
    login_elem = await user.session.get_element('#login')
    await login_elem.send_keys('a')

    # VERIFY BUTTON
    connect_button = await user.session.get_element('#connectButton')
    button_text = await connect_button.get_text()

    assert await connect_button.is_enabled() is True
    assert button_text == 'Connect'

    # BRING BACK USER NAME
    await login_elem.clear()
    await login_elem.send_keys(user.user_name)

    # VERIFY BUTTON
    connect_button = await user.session.get_element('#connectButton')
    button_text = await connect_button.get_text()

    assert await connect_button.is_enabled() is False
    assert button_text == 'Connected'

    # CHANGE CHAT NAME
    chat_elem = await user.session.get_element('#findChat')
    await chat_elem.send_keys('a')

    # VERIFY BUTTON
    connect_button = await user.session.get_element('#connectButton')
    button_text = await connect_button.get_text()

    assert await connect_button.is_enabled() is True
    assert button_text == 'Connect'

    # BRING BACK CHAT NAME
    await chat_elem.clear()
    await chat_elem.send_keys(user.chat_room)

    # VERIFY BUTTON
    connect_button = await user.session.get_element('#connectButton')
    button_text = await connect_button.get_text()

    assert await connect_button.is_enabled() is False
    assert button_text == 'Connected'


@pytest.mark.asyncio
async def test_invalid_input_verification(chatbox_server, http_server, user):
    invalid_inputs = ['Da Vinci', 'da vinci', 'DaVinci.', 'da#vinci', 'da@vinci', 'da(vinci)', 'da&vinci', 'da_vinci!',
                      'da/vinci', 'davinci?', 'da[vinci]', 'da{vinci}', 'da|vinci', '-', '_', 'da+vinci', 'da*vinci',
                      '"davinci"', "fofo'", "lunedi'", '#3', '5!', '1$', '2~3', 'dþ', '012345678901234567890']
    input_elements_ids = ['login', 'findChat']

    for input_element in input_elements_ids:
        # ENSURE THE LOOP STARTS WITH CORRECT VALUES
        login = await user.session.get_element('#login')
        chat = await user.session.get_element('#findChat')
        await login.clear()
        await chat.clear()
        await login.send_keys('abc')
        await chat.send_keys('abc')

        for invalid_input in invalid_inputs:
            # SET INPUT
            elem = await user.session.get_element(f'#{input_element}')
            await elem.clear()
            await elem.send_keys(invalid_input)

            # GET DETAILS
            class_name = await elem.get_attribute('class')
            connect_button = await user.session.get_element('#connectButton')
            button_text = await connect_button.get_text()

            # VERIFY
            assert class_name == 'incorrectInput'
            assert await connect_button.is_enabled() is False
            assert button_text == 'Connect'


@pytest.mark.asyncio
async def test_valid_inputs(chatbox_server, http_server, user):
    valid_inputs = ['davinci', 'DaVinci', 'da_vinci', 'Da-Vinci', 'davinci_15', 'fofò', 'tribù', 'verità', 'lunedì',
                    'ventitré', 'ą', '100', '2-1', 'cç', 'nň', 'uŰ', '01234567890123456789']
    input_elements_ids = ['login', 'findChat']

    for input_element in input_elements_ids:
        for valid_input in valid_inputs:
            # SET INPUT
            elem = await user.session.get_element(f'#{input_element}')
            await elem.clear()
            await elem.send_keys(valid_input)

            # GET DETAILS
            class_name = await elem.get_attribute('class')
            connect_button = await user.session.get_element('#connectButton')
            button_text = await connect_button.get_text()

            # VERIFY
            assert class_name is None
            assert await connect_button.is_enabled() is True
            assert button_text == 'Connect'


@pytest.mark.asyncio
async def test_blank_username_input(chatbox_server, http_server, user):
    # CLEAR LOGIN INPUT
    login_elem = await user.session.get_element('#login')
    await login_elem.clear()

    # GET ELEMENTS
    class_name = await login_elem.get_attribute('class')
    connect_button = await user.session.get_element('#connectButton')

    # VERIFY
    assert class_name is None
    assert await connect_button.is_enabled() is False


@pytest.mark.asyncio
async def test_blank_chatname_input(chatbox_server, http_server, user):
    # CLEAR CHAT NAME INPUT
    chat_elem = await user.session.get_element('#findChat')
    await chat_elem.clear()

    # GET ELEMENTS
    class_name = await chat_elem.get_attribute('class')
    connect_button = await user.session.get_element('#connectButton')

    # VERIFY
    assert class_name is None
    assert await connect_button.is_enabled() is False


@pytest.mark.asyncio
async def test_leave_chat_without_login_and_chat(chatbox_server, http_server, user):
    # CLEAR LOGIN AND CHAT NAME INPUTS
    login_elem = await user.session.get_element('#login')
    await login_elem.clear()

    chat_elem = await user.session.get_element('#findChat')
    await chat_elem.clear()

    # # CLOSE PAGE
    await arsenic.stop_session(user.session)
    user.session = None

    # OPEN NEW PAGE AND CHECK DATA
    new_session = await arsenic_tests_helpers.create_session(user.chat_room, user.headless)

    # VERIFY INPUTS
    login_input_value = await arsenic_tests_helpers.get_login_input_value(new_session)
    chat_elem = await new_session.get_element('#findChat')
    chat_input_value = await chat_elem.get_attribute('value')

    assert login_input_value != ''
    assert chat_input_value == user.chat_room

    await arsenic.stop_session(new_session)



@pytest.mark.asyncio
async def test_leave_chat_with_invalid_inputs(chatbox_server, http_server, user):
    # PROVIDE INCORRECT LOGIN AND CHAT NAME INPUTS
    login_elem = await user.session.get_element('#login')
    await login_elem.clear()
    await login_elem.send_keys('This is wrong!')

    chat_elem = await user.session.get_element('#findChat')
    await chat_elem.clear()
    await chat_elem.send_keys('This is wrong!')

    # CLOSE PAGE
    await arsenic.stop_session(user.session)
    user.session = None

    # OPEN NEW PAGE AND CHECK DATA
    new_session = await arsenic_tests_helpers.create_session(user.chat_room, user.headless)

    # VERIFY INPUTS
    login_input_value = await arsenic_tests_helpers.get_login_input_value(new_session)
    chat_elem = await new_session.get_element('#findChat')
    chat_input_value = await chat_elem.get_attribute('value')

    assert login_input_value != 'This is wrong!' and login_input_value != ''
    assert chat_input_value != 'This is wrong!' and chat_input_value == user.chat_room

    await arsenic.stop_session(new_session)
