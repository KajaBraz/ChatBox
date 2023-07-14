import asyncio
import multiprocessing
import os.path

import arsenic
import pytest
import pytest_asyncio

from chatbox_tests import mocked_database, arsenic_tests_helpers
from src import helper_functions, chatbox_websocket_server, enums


class TestUser:
    def __init__(self):
        self.chat_room = helper_functions.generate_random_string(10)
        self.user_name = helper_functions.generate_random_string(10)
        self.session: arsenic.Session = None


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


@pytest_asyncio.fixture
async def user_connected_with_button():
    client = TestUser()
    client.session = await arsenic_tests_helpers.creaate_session()
    await arsenic_tests_helpers.connect_user(client.user_name, client.chat_room, client.session)

    yield client
    await arsenic.stop_session(client.session)


@pytest_asyncio.fixture
async def user():
    client = TestUser()
    client.session = await arsenic_tests_helpers.creaate_session(client.chat_room)

    yield client
    await arsenic.stop_session(client.session)


@pytest.mark.asyncio
async def test_open_chatbox_default_link(chatbox_server, http_server, user):
    default_chat_name = enums.Constants.DEFAULT_CHAT_NAME
    await user.session.get(f'localhost:5000/')
    await asyncio.sleep(2)

    login_elem = await user.session.get_element('#login')
    chat_elem = await user.session.get_element('#findChat')
    displayed_url = await user.session.get_url()
    header_elem = await user.session.get_element('#chatNameHeader')
    chat_list_elem = await user.session.get_element('#recentlyUsedChats')
    displayed_chat = await chat_list_elem.get_element(f'#{default_chat_name}')
    active_users = await user.session.get_element('.chatUser')

    assert await chat_elem.get_attribute('value') == default_chat_name
    assert await header_elem.get_text() == default_chat_name
    assert await displayed_chat.get_text() == default_chat_name
    assert default_chat_name not in displayed_url
    # assert await login_elem.get_attribute('value') != ''
    # assert await login_elem.get_attribute('value') == await active_users.get_text()


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


# @pytest.mark.asyncio
# async def test_connect_with_button(chatbox_server, http_server, user_connected_with_button):
#     header_elem = await user_connected_with_button.session.get_element('#chatNameHeader')
#     chat_list_elem = await user_connected_with_button.session.get_element('#recentlyUsedChats')
#     displayed_chat = await chat_list_elem.get_element(f'#{user_connected_with_button.chat_room}')
#     displayed_user = await user_connected_with_button.session.get_element('#activeUsers')
#     await asyncio.sleep(2)
#     assert await header_elem.get_text() == user_connected_with_button.chat_room
#     assert await displayed_chat.get_text() == user_connected_with_button.chat_room
#     assert await displayed_user.get_text() == user_connected_with_button.user_name
#
# @pytest.mark.asyncio
# async def test_sending_and_displaying_messages(chatbox_server, http_server, user):
#     new_message_box = await user.session.get_element('#newMessage')
#     send_button = await user.session.get_element('#sendMessageButton')
#
#     # SEND MESSAGES
#     messages = [helper_functions.generate_random_string(15) for _ in range(5)]
#     for message in messages:
#         await new_message_box.send_keys(message)
#         await send_button.click()
#
#     # CHECK RECEIVED MESSAGES
#     received_messages_box = await user.session.get_element('#receivedMessages')
#     received_messages = [await m.get_text() for m in await received_messages_box.get_elements('.messageText')]
#     assert messages == received_messages


@pytest.mark.asyncio
async def test_recent_chats_display(chatbox_server, http_server, user):
    chat_rooms = [helper_functions.generate_random_string(10) for _ in range(4)]
    chat_elem = await user.session.get_element('#findChat')
    connect_button_elem = await user.session.get_element('#connectButton')
    for chat_room in chat_rooms:
        await chat_elem.clear()
        await chat_elem.send_keys(chat_room)
        await connect_button_elem.click()
    resulting_chat_names = [await elem.get_text() for elem in await user.session.get_elements('.availableChat')]
    assert chat_rooms[::-1] + [user.chat_room] == resulting_chat_names


@pytest.mark.asyncio
async def test_active_users_display(chatbox_server, http_server, user_connected_with_button):
    # todo fix the below version to open tabs instead of new windows
    activer_users = await user_connected_with_button.session.get_elements('.chatUser')
    assert {user_connected_with_button.user_name} == {await active_user.get_text() for active_user in activer_users}

    new_users = {helper_functions.generate_random_string(10) for _ in range(4)}
    new_sessions = set()
    temp_users = {user_connected_with_button.user_name}
    temp_drivers = {user_connected_with_button.session}

    for new_user in new_users:
        new_session = await arsenic_tests_helpers.creaate_session()
        await arsenic_tests_helpers.connect_user(new_user, user_connected_with_button.chat_room, new_session)
        # todo refactor connect_user and make user/chat optional
        new_sessions.add(new_session)
        temp_users.add(new_user)
        temp_drivers.add(new_session)
        temp_active_users = [{await u.get_text() for u in await dr.get_elements('.chatUser')} for dr in temp_drivers]
        assert all(temp_users == displayed for displayed in temp_active_users)

    # todo, temporary to remove, use separate windows instead, not drivers
    for ns in new_sessions:
        await arsenic.stop_session(ns)


@pytest.mark.asyncio
async def test_messages_position(chatbox_server, http_server, user):
    # CONNECT USER 2
    user2 = helper_functions.generate_random_string(5)
    new_session = await arsenic_tests_helpers.creaate_session()
    await arsenic_tests_helpers.connect_user(user2, user.chat_room, new_session)

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
    received_messages_box = await user.session.get_element('#receivedMessages')

    # USER 1 SENDS MESSAGES
    messages = [helper_functions.generate_random_string(5) for _ in range(25)]
    new_msg_box = await user.session.get_element('#newMessage')
    send_button = await user.session.get_element('#sendMessageButton')
    for message in messages:
        await new_msg_box.clear()
        await new_msg_box.send_keys(message)
        await send_button.click()

    # USER CHANGES LOGIN AND CONNECTS
    new_login = helper_functions.generate_random_string(5)
    await arsenic_tests_helpers.connect_user(new_login, user.chat_room, user.session)

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
    messages = await user.session.get_elements('.messageText')
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
