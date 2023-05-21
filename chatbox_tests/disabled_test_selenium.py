import asyncio
import os
from datetime import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src import helper_functions, chatbox_websocket_server


def create_driver():
    options = Options()
    options.add_argument('--headless')  # don't use when you want to actually open and see the browser window
    driver = webdriver.Firefox(options=options)
    relative_path = os.path.join(os.pardir, 'javascript', 'index.html')
    absolute_path = os.path.abspath(relative_path)
    driver.get(f'file:///{absolute_path}')
    driver.implicitly_wait(10)
    return driver


class TestState:
    def __init__(self):
        self.chat_room = helper_functions.generate_random_string(10)
        self.user_name = helper_functions.generate_random_string(10)
        self.driver: webdriver.Firefox = None


client = TestState()


@pytest.fixture
async def server():
    # config_path = '../chatbox_tests_config.json'
    # await chatbox_websocket_server.main(config_path, True)
    # yield

    config_path = '../chatbox_tests_config.json'
    data = helper_functions.read_config(config_path)
    address = data['address']['name']
    port = data['address']['port']
    chatbox_server = chatbox_websocket_server.Server(data)
    await chatbox_server.start(address, port)
    yield
    chatbox_server.stop()
    await chatbox_server.wait_stop()


@pytest.fixture
async def user():
    client.driver = create_driver()
    login_elem = client.driver.find_element_by_id('login')
    chat_elem = client.driver.find_element_by_id('findChat')
    connect_button_elem = client.driver.find_element_by_id('connectButton')
    login_elem.send_keys(client.user_name)
    chat_elem.send_keys(client.chat_room)
    connect_button_elem.click()
    login_elem.clear()
    chat_elem.clear()

    yield
    screenshot_path = os.path.abspath(os.path.join(os.pardir, 'test_results', 'selenium_screenshots',
                                                   f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'))
    client.driver.get_screenshot_as_file(screenshot_path)
    client.driver.quit()


@pytest.mark.asyncio
async def test_first_connection(server, user):
    header_elem = client.driver.find_element_by_id('chatNameHeader')
    chat_list_elem = client.driver.find_element_by_id('recentlyUsedChats')
    user_list_elem = client.driver.find_element_by_id('activeUsers')
    await asyncio.sleep(2)
    # WebDriverWait(client.driver, timeout=10).until(lambda d: d.find_element(By.CLASS_NAME, 'chatUser').text != 'User 1')
    # WebDriverWait(client.driver, timeout=10).until(EC.text_to_be_present_in_element_value((By.CLASS_NAME, 'chatUser'), client.user_name))
    assert header_elem.text == client.chat_room
    assert chat_list_elem.find_element_by_id(client.chat_room).text == client.chat_room
    assert user_list_elem.find_element_by_class_name('chatUser').text == client.user_name


@pytest.mark.asyncio
async def test_sending_and_displaying_messages(server, user):
    new_message_box = client.driver.find_element_by_id('newMessage')
    send_button = client.driver.find_element_by_id('sendMessageButton')
    await asyncio.sleep(2)

    # SEND MESSAGES
    messages = [helper_functions.generate_random_string(15) for i in range(5)]
    for message in messages:
        new_message_box.send_keys(message)
        send_button.click()
        await asyncio.sleep(2)

    # CHECK RECEIVED MESSAGES
    received_messages_box = client.driver.find_element_by_id('receivedMessages')
    received_messages = [m.text for m in received_messages_box.find_elements_by_class_name('messageText')]
    assert messages == received_messages


@pytest.mark.asyncio
async def test_recent_chats_display(server, user):
    chat_rooms = [helper_functions.generate_random_string(10) for _ in range(4)]
    chat_elem = client.driver.find_element_by_id('findChat')
    connect_button_elem = client.driver.find_element_by_id('connectButton')
    await asyncio.sleep(2)
    for chat_room in chat_rooms:
        chat_elem.send_keys(chat_room)
        connect_button_elem.click()
        chat_elem.clear()
    resulting_chat_names = [elem.text for elem in client.driver.find_elements_by_class_name('availableChat')]
    assert chat_rooms[::-1] + [client.chat_room] == resulting_chat_names
    # todo fix: test passes and then hangs indefinitely


@pytest.mark.asyncio
async def test_active_users_display(server, user):
    def make_drivers(username):
        # todo move to a general function (connection) and use in other tests
        # todo fix the below version to open tabs instead of new windows
        # state.driver.execute_script("window.open('');")
        # state.driver.execute_script(f"window.open('file:///{state.absolute_path}', '_blank');")
        # state.driver.switch_to.window(state.driver.window_handles[-1])
        # state.driver.get(f'file:///{state.absolute_path}')

        new_dr = create_driver()

        login_elem = new_dr.find_element_by_id('login')
        chat_elem = new_dr.find_element_by_id('findChat')
        connect_button_elem = new_dr.find_element_by_id('connectButton')
        login_elem.send_keys(username)
        chat_elem.send_keys(client.chat_room)
        connect_button_elem.click()
        return new_dr

    await asyncio.sleep(2)
    activer_users = client.driver.find_elements_by_class_name('chatUser')
    assert {client.user_name} == {active_user.text for active_user in activer_users}

    new_users = {helper_functions.generate_random_string(10) for _ in range(4)}
    new_drivers = set()
    temp_users = {client.user_name}
    temp_drivers = {client.driver}

    for new_user in new_users:
        new_driver = make_drivers(new_user)
        new_drivers.add(new_driver)
        temp_users.add(new_user)
        temp_drivers.add(new_driver)
        await asyncio.sleep(2)
        temp_active_users = [{u.text for u in dr.find_elements_by_class_name('chatUser')} for dr in temp_drivers]
        assert all(temp_users == displayed for displayed in temp_active_users)

    # todo, temporary to remove, use separate windows instead, not drivers
    for d in new_drivers:
        d.quit()


@pytest.mark.asyncio
async def test_messages_position(server, user):
    # CONNECT USER 2
    new_driver = create_driver()
    user2_login = helper_functions.generate_random_string(10)
    login_elem = new_driver.find_element_by_id('login')
    chat_elem = new_driver.find_element_by_id('findChat')
    connect_button_elem = new_driver.find_element_by_id('connectButton')
    login_elem.send_keys(user2_login)
    chat_elem.send_keys(client.chat_room)
    connect_button_elem.click()
    await asyncio.sleep(2)
    # todo move into a connection function

    # PREPARE MESSAGES USER1
    messages_user1 = [helper_functions.generate_random_string(15) for i in range(2)]
    new_message_box_user1 = client.driver.find_element_by_id('newMessage')
    send_button_user1 = client.driver.find_element_by_id('sendMessageButton')

    # PREPARE MESSAGES USER2
    messages_user2 = [helper_functions.generate_random_string(15) for i in range(2)]
    new_message_box_user2 = new_driver.find_element_by_id('newMessage')
    send_button_user2 = new_driver.find_element_by_id('sendMessageButton')

    # SEND MESSAGES
    new_message_box_user1.send_keys(messages_user1[0])
    send_button_user1.click()
    await asyncio.sleep(2)

    new_message_box_user2.send_keys(messages_user2[0])
    send_button_user2.click()
    await asyncio.sleep(2)

    new_message_box_user1.send_keys(messages_user1[1])
    send_button_user1.click()
    await asyncio.sleep(2)

    new_message_box_user2.send_keys(messages_user2[1])
    send_button_user2.click()
    await asyncio.sleep(2)

    # GATHER MESSAGES
    new_message_box_user1.click()
    new_message_box_user2.click()
    received_messages_user1 = client.driver.find_elements_by_class_name('message')
    received_messages_user2 = new_driver.find_elements_by_class_name('message')

    # CHECK MESSAGES STYLE
    messages_style_user1 = [m.get_attribute('style') for m in received_messages_user1]
    messages_style_user2 = [m.get_attribute('style') for m in received_messages_user2]

    assert all(['right' in messages_style_user1[i] for i in range(len(messages_style_user1)) if i % 2 == 0])
    assert all(['right' in messages_style_user2[i] for i in range(len(messages_style_user2)) if i % 2 == 1])
    assert all(['left' in messages_style_user1[i] for i in range(len(messages_style_user1)) if i % 2 == 1])
    assert all(['left' in messages_style_user2[i] for i in range(len(messages_style_user2)) if i % 2 == 0])

    # todo temporary, to remove, make seperate windows not drivers
    new_driver.quit()


# @pytest.mark.asyncio
# async def test_previous_messages(server,user):
#     # todo enable to work without database
#     # works for displaying 10 messages on the client's connection
#
#     received_messages_box = client.driver.find_element_by_id('receivedMessages')
#
#     # USER 1 SENDS MESSAGES
#     messages = [helper_functions.generate_random_string(5) for i in range(20)]
#     new_msg_box = client.driver.find_element_by_id('newMessage')
#     send_button = client.driver.find_element_by_id('sendMessageButton')
#     for message in messages:
#         new_msg_box.send_keys(message)
#         send_button.click()
#         new_msg_box.clear()
#
#     # wait = WebDriverWait(client.driver, 10)
#     # wait.until(
#     #     lambda d: [m.text for m in received_messages_box.find_elements_by_class_name('messageText')] == messages,
#     #     f"Message not found - wait 1, {[m.text for m in received_messages_box.find_elements_by_class_name('messageText')]}"
#     # )
#     await asyncio.sleep(10)
#
#     # USER 2 CONNECTS
#     login_elem = client.driver.find_element_by_id('login')
#     chat_elem = client.driver.find_element_by_id('findChat')
#     connect_button_elem = client.driver.find_element_by_id('connectButton')
#     login_elem.send_keys(helper_functions.generate_random_string(5))
#     chat_elem.send_keys(client.chat_room)
#     connect_button_elem.click()
#
#     # wait.until(
#     #     lambda d: messages[10:] == [m.text for m in received_messages_box.find_elements_by_class_name('messageText')],
#     #     f"Message not found - wait 2, {[m.text for m in received_messages_box.find_elements_by_class_name('messageText')]}"
#     # )
#     await asyncio.sleep(10)
#
#     previous_messages_loaded_on_connection = received_messages_box.find_elements_by_class_name('messageText')
#     assert messages[10:] == [m.text for m in previous_messages_loaded_on_connection]
#
#     client.driver.execute_script("receivedMessages.scrollTo(0, -receivedMessages.offsetHeight)")
#     # wait.until(
#     #     lambda d: messages == [m.text for m in received_messages_box.find_elements_by_class_name('messageText')],
#     #     f"Message not found, wait 3 {[m.text for m in received_messages_box.find_elements_by_class_name('messageText')]}"
#     # )
#     await asyncio.sleep(10)
#     more_previous_messages_loaded_after_scoll = received_messages_box.find_elements_by_class_name('messageText')
#
#     assert messages == [m.text for m in more_previous_messages_loaded_after_scoll]

@pytest.mark.asyncio
async def test_adjust_number_of_displayed_messages(server, user):
    # works for max num of messgaes in messages box set to 20
    max_msgs_on_page_num = 20

    received_messages_box = client.driver.find_element_by_id('receivedMessages')
    new_message_box = client.driver.find_element_by_id('newMessage')
    send_button = client.driver.find_element_by_id('sendMessageButton')
    await asyncio.sleep(2)

    messages = [helper_functions.generate_random_string(5) for _ in range(25)]
    for message in messages[:max_msgs_on_page_num]:
        new_message_box.send_keys(message)
        send_button.click()
        await asyncio.sleep(2)

    await asyncio.sleep(2)
    displayed_messages = received_messages_box.find_elements_by_class_name('messageText')
    assert len(displayed_messages) == max_msgs_on_page_num
    assert messages[:max_msgs_on_page_num] == [m.text for m in displayed_messages]

    i_start = 1
    for message in messages[max_msgs_on_page_num:]:
        new_message_box.send_keys(message)
        send_button.click()
        await asyncio.sleep(2)
        displayed_messages = received_messages_box.find_elements_by_class_name('messageText')
        assert len(displayed_messages) == max_msgs_on_page_num
        assert messages[i_start:i_start + max_msgs_on_page_num] == [m.text for m in displayed_messages]
        i_start += 1
