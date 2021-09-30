import datetime
import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from src import helper_functions


class TestState:
    pass


@pytest.fixture
def state():
    state = TestState()
    state.options = Options()
    state.options.add_argument('--headless')  # don't use when you want to actually open and see the browser window
    state.driver = webdriver.Firefox(options=state.options)

    relative_path = os.path.join(os.pardir, 'javascript', 'index.html')
    state.absolute_path = os.path.abspath(relative_path)

    state.driver.get(f'file:///{state.absolute_path}')

    state.user_name = helper_functions.generate_random_string(10)
    state.chat_room = helper_functions.generate_random_string(10)

    yield state
    screenshot_path = os.path.abspath(os.path.join(os.pardir, 'test_results', 'selenium_screenshots',
                                                   f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'))
    state.driver.get_screenshot_as_file(screenshot_path)
    state.driver.quit()


def test_first_connection(state):
    login_elem = state.driver.find_element_by_id('login')
    chat_elem = state.driver.find_element_by_id('findChat')
    connect_button_elem = state.driver.find_element_by_id('connectButton')
    header_elem = state.driver.find_element_by_id('chatNameHeader')
    chat_list_elem = state.driver.find_element_by_id('recentlyUsedChats')
    user_list_elem = state.driver.find_element_by_id('activeUsers')
    login_elem.send_keys(state.user_name)
    chat_elem.send_keys(state.chat_room)
    connect_button_elem.click()
    time.sleep(1)
    assert header_elem.text == state.chat_room
    assert chat_list_elem.find_element_by_id(state.chat_room).text == state.chat_room
    assert user_list_elem.find_element_by_class_name('chatUser').text == state.user_name


def test_sending_and_displaying_messages(state):
    # CONNECTION
    login_elem = state.driver.find_element_by_id('login')
    chat_elem = state.driver.find_element_by_id('findChat')
    connect_button_elem = state.driver.find_element_by_id('connectButton')
    login_elem.send_keys(state.user_name)
    chat_elem.send_keys(state.chat_room)
    connect_button_elem.click()
    time.sleep(0.5)

    # SENDING MESSAGES
    messages = [helper_functions.generate_random_string(15) for i in range(5)]
    for message in messages:
        new_message_box = state.driver.find_element_by_id('newMessage')
        send_button = state.driver.find_element_by_id('sendMessageButton')
        new_message_box.send_keys(message)
        send_button.click()
        time.sleep(0.5)

    # CHECKING RECEIVED MESSAGES
    received_messages_box = state.driver.find_element_by_id('receivedMessages')
    received_messages = [m.text for m in received_messages_box.find_elements_by_class_name('messageText')]
    assert messages == received_messages


def test_recent_chats_display(state):
    chat_rooms = [state.chat_room] + [helper_functions.generate_random_string(10) for i in range(4)]
    login_elem = state.driver.find_element_by_id('login')
    chat_elem = state.driver.find_element_by_id('findChat')
    connect_button_elem = state.driver.find_element_by_id('connectButton')
    login_elem.send_keys(state.user_name)
    for chat_room in chat_rooms:
        chat_elem.send_keys(chat_room)
        connect_button_elem.click()
        time.sleep(1)
        chat_elem.clear()
    resulting_chat_names = [elem.text for elem in state.driver.find_elements_by_class_name('availableChat')]
    assert chat_rooms[::-1] == resulting_chat_names


def test_active_users_display(state):
    users = [state.user_name] + [helper_functions.generate_random_string(10) for i in range(4)]
    for user in users:
        # todo fix the below version to open tabs instead of new windows
        # state.driver.execute_script("window.open('');")
        # state.driver.execute_script(f"window.open('file:///{state.absolute_path}', '_blank');")
        # state.driver.switch_to.window(state.driver.window_handles[-1])
        # state.driver.get(f'file:///{state.absolute_path}')

        new_driver = webdriver.Firefox(options=state.options)
        new_driver.get(f'file:///{state.absolute_path}')

        login_elem = new_driver.find_element_by_id('login')
        chat_elem = new_driver.find_element_by_id('findChat')
        connect_button_elem = new_driver.find_element_by_id('connectButton')
        login_elem.send_keys(user)
        chat_elem.send_keys(state.chat_room)
        connect_button_elem.click()
        time.sleep(1)

    time.sleep(1)
    resulting_active_users = set([user.text for user in new_driver.find_elements_by_class_name('chatUser')])
    assert set(users) == resulting_active_users
