import asyncio
import os

import arsenic
import pytest

from src import helper_functions, chatbox_websocket_server, database


class TestState:
    def __init__(self):
        self.chat_room = ''
        self.user_name = ''
        self.chat_elem = None
        self.connect_button_elem = None
        self.login_elem = None
        self.server: chatbox_websocket_server.Server = None
        self.session: arsenic.Session = None


@pytest.fixture
async def state():
    state = TestState()
    yield state


@pytest.fixture
async def server(state):
    config_path = '../chatbox_tests_config.json'
    data = helper_functions.read_config(config_path)
    # state = TestState()
    state.address = data['address']['name']
    state.port = data['address']['port']
    state.server = chatbox_websocket_server.Server(data)
    await state.server.start(state.address, state.port)
    # yield state.server
    try:
        yield state.server
    finally:
        state.server.stop()
        await state.server.wait_stop()


@pytest.fixture
async def session(state):
    relative_path = os.path.join(os.pardir, 'javascript', 'index.html')
    absolute_path = os.path.abspath(relative_path)
    state.session = await arsenic.start_session(arsenic.services.Geckodriver(),
                                                arsenic.browsers.Firefox())
    await state.session.get(absolute_path)
    state.user_name = helper_functions.generate_random_string(10)
    state.chat_room = helper_functions.generate_random_string(10)
    state.login_elem = await state.session.get_element('#login')
    state.chat_elem = await state.session.get_element('#findChat')
    state.connect_button_elem = await state.session.get_element('#connectButton')
    await state.login_elem.send_keys(state.user_name)
    await state.chat_elem.send_keys(state.chat_room)
    await state.connect_button_elem.click()
    await state.login_elem.clear()
    await state.chat_elem.clear()
    # yield state.session
    try:
        yield state.session
    finally:
        await arsenic.stop_session(state.session)


@pytest.mark.asyncio
async def test_first_connection(state: TestState, session):
    header_elem = await state.session.get_element('#chatNameHeader')
    chat_list_elem = await state.session.get_element('#recentlyUsedChats')
    displayed_chat = await chat_list_elem.get_element(f'#{state.chat_room}')
    displayed_user = await state.session.get_element('#activeUsers')
    # displayed_user = await user_list_elem.get_element('#activeUsers')
    await asyncio.sleep(10)
    assert await header_elem.get_text() == state.chat_room
    assert await displayed_chat.get_text() == state.chat_room
    assert await displayed_user.get_text() == state.user_name
    # await asyncio.sleep(0.5)
