import asyncio
import os

import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from src import chatbox_websocket_server, database, helper_functions


class TestState:
    pass


@pytest.fixture
async def state():
    config_path = '../chatbox_config.json'
    data = helper_functions.read_config(config_path)
    state = TestState()
    state.server = chatbox_websocket_server.Server(data)
    if 'database' in data:
        state.server.chatbox_database = database.ChatBoxDatabase(data)
        state.server.conn = state.server.chatbox_database.connect()
    await state.server.start(data['address']['name'], data['address']['port'])
    await asyncio.sleep(1)
    options = Options()
    # options.add_argument('--headless')
    state.driver = webdriver.Firefox(options=options)

    # to use when you want to actually open the browser window
    # state.driver = webdriver.Firefox()

    relative_path = os.path.join(os.pardir, 'javascript','index.html')
    absolute_path = os.path.abspath(relative_path)

    state.driver.get(f'file:///{absolute_path}')

    yield state
    state.driver.quit()
    state.server.stop()
    await state.server.wait_stop()


@pytest.mark.asyncio
async def test_first_connection(state):
    chat_room = 'NewChat'
    login = 'UserName'
    login_elem = state.driver.find_element_by_id('login')
    chat_elem = state.driver.find_element_by_id('findChat')
    connect_button_elem = state.driver.find_element_by_id('connectButton')
    header_elem = state.driver.find_element_by_id('chatNameHeader')
    chat_list_elem = state.driver.find_element_by_id('recentlyUsedChats')
    user_list_elem = state.driver.find_element_by_id('activeUsers')
    login_elem.send_keys(login)
    chat_elem.send_keys(chat_room)
    connect_button_elem.click()
    await asyncio.sleep(1)
    assert header_elem.text == chat_room
    assert chat_list_elem.find_element_by_id(chat_room).text == chat_room
    assert user_list_elem.find_element_by_class_name('chatUser').text == login


@pytest.mark.asyncio
async def test_sending_message(state):
    # CONNECTION
    chat_room = 'NewChat'
    login = 'UserName'
    login_elem = state.driver.find_element_by_id('login')
    chat_elem = state.driver.find_element_by_id('findChat')
    connect_button_elem = state.driver.find_element_by_id('connectButton')
    login_elem.send_keys(login)
    chat_elem.send_keys(chat_room)
    connect_button_elem.click()
    await asyncio.sleep(1)

    # MESSAGE
    message = 'This is a message'
    message_span = len(message)
    new_message = state.driver.find_element_by_id('newMessage')
    send_button = state.driver.find_element_by_id('sendMessageButton')
    message_box = state.driver.find_element_by_id('receivedMessages')
    new_message.send_keys(message)
    send_button.click()
    await asyncio.sleep(1)
    print('***')
    print(message_box.find_element_by_class_name('message').text)
    print('***')
    assert message == message_box.find_element_by_class_name('message').text[-message_span:]
