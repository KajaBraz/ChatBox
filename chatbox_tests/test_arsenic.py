import os

import arsenic
import pytest
import pytest_asyncio

from src import helper_functions, chatbox_websocket_server


class TestUser:
    def __init__(self):
        self.chat_room = helper_functions.generate_random_string(10)
        self.user_name = helper_functions.generate_random_string(10)
        self.session: arsenic.Session = None


@pytest_asyncio.fixture
async def server():
    # config_path = '../chatbox_tests_config.json'
    # await chatbox_websocket_server.main(config_path, True)
    # yield
    # # print('\nserver')

    config_path = '../chatbox_tests_config.json'
    data = helper_functions.read_config(config_path)
    address = data['address']['name']
    port = data['address']['port']
    chatbox_server = chatbox_websocket_server.Server(data)
    await chatbox_server.start(address, port)
    yield
    chatbox_server.stop()
    await chatbox_server.wait_stop()


@pytest_asyncio.fixture
async def user():
    client = TestUser()
    relative_path = os.path.join(os.pardir, 'javascript', 'index.html')
    absolute_path = os.path.abspath(relative_path)
    client.session = await arsenic.start_session(arsenic.services.Geckodriver(), arsenic.browsers.Firefox())
    # client.session = await arsenic.start_session(arsenic.services.Geckodriver(), arsenic.browsers.Firefox(firefoxOptions={'args': ['-headless']}))
    await client.session.get(f'file:///{absolute_path}')
    login_elem = await client.session.get_element('#login')
    chat_elem = await client.session.get_element('#findChat')
    connect_button_elem = await client.session.get_element('#connectButton')
    await login_elem.send_keys(client.user_name)
    await chat_elem.send_keys(client.chat_room)
    await connect_button_elem.click()
    # try:
    yield client
    # finally:
    await arsenic.stop_session(client.session)


@pytest.mark.asyncio
async def test_first_connection(server, user):
    header_elem = await user.session.get_element('#chatNameHeader')
    chat_list_elem = await user.session.get_element('#recentlyUsedChats')
    displayed_chat = await chat_list_elem.get_element(f'#{user.chat_room}')
    displayed_user = await user.session.get_element('#activeUsers')
    assert await header_elem.get_text() == user.chat_room
    assert await displayed_chat.get_text() == user.chat_room
    assert await displayed_user.get_text() == user.user_name


@pytest.mark.asyncio
async def test_sending_and_displaying_messages(server, user):
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
async def test_recent_chats_display(server, user):
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
async def test_active_users_display(server, user):
    async def make_drivers(username):
        # todo move to a general function (connection) and use in other tests
        # todo fix the below version to open tabs instead of new windows

        new_session = await arsenic.start_session(arsenic.services.Geckodriver(), arsenic.browsers.Firefox())
        relative_path = os.path.join(os.pardir, 'javascript', 'index.html')
        absolute_path = os.path.abspath(relative_path)
        await new_session.get(f'file:///{absolute_path}')

        login_elem = await new_session.get_element('#login')
        chat_elem = await new_session.get_element('#findChat')
        connect_button_elem = await new_session.get_element('#connectButton')
        await login_elem.send_keys(username)
        await chat_elem.send_keys(user.chat_room)
        await connect_button_elem.click()
        return new_session

    activer_users = await user.session.get_elements('.chatUser')
    assert {user.user_name} == {await active_user.get_text() for active_user in activer_users}

    new_users = {helper_functions.generate_random_string(10) for _ in range(4)}
    new_sessions = set()
    temp_users = {user.user_name}
    temp_drivers = {user.session}

    for new_user in new_users:
        new_sessioniver = await make_drivers(new_user)
        new_sessions.add(new_sessioniver)
        temp_users.add(new_user)
        temp_drivers.add(new_sessioniver)
        temp_active_users = [{await u.get_text() for u in await dr.get_elements('.chatUser')} for dr in temp_drivers]
        assert all(temp_users == displayed for displayed in temp_active_users)

    # todo, temporary to remove, use separate windows instead, not drivers
    for ns in new_sessions:
        await arsenic.stop_session(ns)


@pytest.mark.asyncio
async def test_messages_position(server, user):
    # CONNECT USER 2
    new_session = await arsenic.start_session(arsenic.services.Geckodriver(), arsenic.browsers.Firefox())
    relative_path = os.path.join(os.pardir, 'javascript', 'index.html')
    absolute_path = os.path.abspath(relative_path)
    await new_session.get(f'file:///{absolute_path}')

    user2_login = helper_functions.generate_random_string(10)
    login_elem = await new_session.get_element('#login')
    chat_elem = await new_session.get_element('#findChat')
    connect_button_elem = await new_session.get_element('#connectButton')
    await login_elem.send_keys(user2_login)
    await chat_elem.send_keys(user.chat_room)
    await connect_button_elem.click()

    # todo move into a connection function

    # PREPARE MESSAGES USER1
    messages_user1 = [helper_functions.generate_random_string(15) for i in range(2)]
    new_message_box_user1 = await user.session.get_element('#newMessage')
    send_button_user1 = await user.session.get_element('#sendMessageButton')

    # PREPARE MESSAGES USER2
    messages_user2 = [helper_functions.generate_random_string(15) for i in range(2)]
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


# @pytest.mark.asyncio
# async def test_previous_messages(server,user):
#     # todo enable to work without database
#     # works for displaying 10 messages on the client's connection
#
#     received_messages_box = client.driver.get_element_by_id('receivedMessages')
#
#     # USER 1 SENDS MESSAGES
#     messages = [helper_functions.generate_random_string(5) for i in range(20)]
#     new_msg_box = client.driver.get_element_by_id('newMessage')
#     send_button = client.driver.get_element_by_id('sendMessageButton')
#     for message in messages:
#         new_msg_box.clear()
#         new_msg_box.send_keys(message)
#         send_button.click()
#
#     # wait = WebDriverWait(client.driver, 10)
#     # wait.until(
#     #     lambda d: [m.text for m in received_messages_box.get_elements_by_class_name('messageText')] == messages,
#     #     f"Message not found - wait 1, {[m.text for m in received_messages_box.get_elements_by_class_name('messageText')]}"
#     # )
#     await asyncio.sleep(10)
#
#     # USER 2 CONNECTS
#     login_elem = client.driver.get_element_by_id('login')
#     chat_elem = client.driver.get_element_by_id('findChat')
#     connect_button_elem = client.driver.get_element_by_id('connectButton')
#     login_elem.send_keys(helper_functions.generate_random_string(5))
#     chat_elem.send_keys(client.chat_room)
#     connect_button_elem.click()
#
#     # wait.until(
#     #     lambda d: messages[10:] == [m.text for m in received_messages_box.get_elements_by_class_name('messageText')],
#     #     f"Message not found - wait 2, {[m.text for m in received_messages_box.get_elements_by_class_name('messageText')]}"
#     # )
#     await asyncio.sleep(10)
#
#     previous_messages_loaded_on_connection = received_messages_box.get_elements_by_class_name('messageText')
#     assert messages[10:] == [m.text for m in previous_messages_loaded_on_connection]
#
#     client.driver.execute_script("receivedMessages.scrollTo(0, -receivedMessages.offsetHeight)")
#     # wait.until(
#     #     lambda d: messages == [m.text for m in received_messages_box.get_elements_by_class_name('messageText')],
#     #     f"Message not found, wait 3 {[m.text for m in received_messages_box.get_elements_by_class_name('messageText')]}"
#     # )
#     await asyncio.sleep(10)
#     more_previous_messages_loaded_after_scoll = received_messages_box.get_elements_by_class_name('messageText')
#
#     assert messages == [m.text for m in more_previous_messages_loaded_after_scoll]

@pytest.mark.asyncio
async def test_adjust_number_of_displayed_messages(server, user):
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
