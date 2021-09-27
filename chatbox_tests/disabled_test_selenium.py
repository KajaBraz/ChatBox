import datetime
import os
import random
import string
import time

import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class TestState:
    pass


@pytest.fixture
def state():
    state = TestState()
    options = Options()
    options.add_argument('--headless')  # don't use when you want to actually open and see the browser window
    state.driver = webdriver.Firefox(options=options)

    relative_path = os.path.join(os.pardir, 'javascript', 'index.html')
    absolute_path = os.path.abspath(relative_path)

    state.driver.get(f'file:///{absolute_path}')

    state.user_name = ''.join(random.sample(string.ascii_letters, 10))
    state.chat_room = ''.join(random.sample(string.ascii_letters, 10))

    yield state
    screenshot_path = os.path.join('selenium_screenshots',
                                   f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png')
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


def test_sending_message(state):
    # CONNECTION
    login_elem = state.driver.find_element_by_id('login')
    chat_elem = state.driver.find_element_by_id('findChat')
    connect_button_elem = state.driver.find_element_by_id('connectButton')
    login_elem.send_keys(state.user_name)
    chat_elem.send_keys(state.chat_room)
    connect_button_elem.click()
    time.sleep(1)

    # MESSAGE
    message = 'This is a message'
    message_span = len(message)
    new_message = state.driver.find_element_by_id('newMessage')
    send_button = state.driver.find_element_by_id('sendMessageButton')
    message_box = state.driver.find_element_by_id('receivedMessages')
    new_message.send_keys(message)
    send_button.click()
    time.sleep(1)
    assert message == message_box.find_elements_by_class_name('message')[-1].text[-message_span:]
