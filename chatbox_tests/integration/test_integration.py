import asyncio

import pytest

from chatbox_tests.integration import mocked_database
from chatbox_tests.integration.virtual_websocket_client import VirtualClient
from src import chatbox_websocket_server, helper_functions, database, message
from src.enums import JsonFields


class TestState:
    pass


@pytest.fixture
async def state():
    # setup actions
    config_path = 'chatbox_tests_config.json'
    data = helper_functions.read_config(config_path)
    state = TestState()
    state.address = data['address']['name']
    state.port = data['address']['port']
    state.room = "room1"
    state.server_obj = chatbox_websocket_server.Server(data)
    if 'database' in data:
        state.server_obj.chatbox_database = database.ChatBoxDatabase(data)
        state.server_obj.conn = state.server_obj.chatbox_database.connect()
    await state.server_obj.start(state.address, state.port)
    state.client = VirtualClient(state.address, state.port, state.room, 'user1')
    state.client2 = VirtualClient(state.address, state.port, state.room, 'user2')
    state.client3 = VirtualClient(state.address, state.port, state.room, 'user3')
    yield state
    # teardown actions
    state.server_obj.stop()
    await state.server_obj.wait_stop()


@pytest.mark.asyncio
async def test_client1_sends_participants_receive(state):
    # GIVEN
    m1 = 'message 1'
    m2 = 'message 2'
    m3 = 'message 3'
    await state.client.connect()
    await state.client2.connect()

    # WHEN
    asyncio.create_task(state.client.start_receiving())
    asyncio.create_task(state.client2.start_receiving())
    sent_task1 = asyncio.create_task(state.client.send(m1))
    sent_task2 = asyncio.create_task(state.client2.send(m2))
    sent_task3 = asyncio.create_task(state.client2.send(m3))
    wait_task = asyncio.create_task(asyncio.sleep(0.5))
    await sent_task1
    await sent_task2
    await sent_task3
    await wait_task

    # THEN
    assert len(state.client.sent_messages + state.client2.sent_messages) == len(state.client2.received_messages)
    assert (len(state.client.sent_messages + state.client2.sent_messages) == len(state.client.received_messages))
    assert (m1 in state.client.received_messages)
    assert (m2 in state.client.received_messages)
    assert (m3 in state.client.received_messages)
    assert (m1 in state.client2.received_messages)
    assert (m2 in state.client2.received_messages)
    assert (m3 in state.client2.received_messages)


@pytest.mark.asyncio
async def test_when_client_sends_message_is_added_to_database(state):
    # GIVEN
    state.server_obj.chatbox_database = mocked_database.MockedDatabase()
    messages = [helper_functions.generate_random_string(15), helper_functions.generate_random_string(15),
                helper_functions.generate_random_string(15)]
    await state.client.connect()
    await state.client2.connect()
    asyncio.create_task(state.client.start_receiving())
    asyncio.create_task(state.client2.start_receiving())

    # WHEN
    await state.client.send(messages[0])
    await state.client.send_not_a_json(messages[1])
    await state.client.send_wrong_message(messages[2])
    await asyncio.sleep(0.5)

    # THEN
    assert len(state.server_obj.chatbox_database.messages) == 1
    assert state.server_obj.chatbox_database.messages[0] == messages[0]
    assert len(state.client.sent_messages) == 3
    assert len(state.client.received_messages) == 1
    assert len(state.client2.received_messages) == 1


@pytest.mark.asyncio
async def test_clients_join_and_leave_chat_check_participants_num(state):
    # WHEN
    await state.client.connect()
    await state.client2.connect()
    await state.client3.connect()

    # THEN
    logins = state.server_obj.chat_participants[state.room].keys()
    assert 3 == len(logins)

    # WHEN
    await state.client2.disconnect()
    await asyncio.sleep(0.5)

    # THEN
    logins = state.server_obj.chat_participants[state.room].keys()
    assert 2 == len(logins)
    assert state.client.user_name in logins
    assert state.client2.user_name not in logins
    assert state.client3.user_name in logins


@pytest.mark.asyncio
async def test_server_receives_and_handles_wrong_message_then_serves_correctly_proper_messages(state):
    # GIVEN
    await state.client.connect()
    await state.client2.connect()
    await state.client3.connect()
    m1 = 'message 1'
    m2 = 'message 2'
    m3 = 'message 3'
    m4 = 'message 4'
    m5 = 'message 5'

    # WHEN
    asyncio.create_task(state.client.start_receiving())
    asyncio.create_task(state.client2.start_receiving())
    asyncio.create_task(state.client3.start_receiving())
    send_task1 = asyncio.create_task(state.client.send(m1))
    send_task2 = asyncio.create_task(state.client2.send_wrong_message(m2))
    send_task3 = asyncio.create_task(state.client3.send(m3))
    send_task4 = asyncio.create_task(state.client2.send_not_a_json(m4))
    send_task5 = asyncio.create_task(state.client2.send(m5))
    wait_task = asyncio.create_task(asyncio.sleep(0.5))
    await send_task1
    await send_task2
    await send_task3
    await send_task4
    await send_task5
    await wait_task

    # THEN
    assert 3 == len(state.client.received_messages)
    assert 3 == len(state.client2.received_messages)
    assert 3 == len(state.client3.received_messages)
    assert m1 in state.client.received_messages
    assert m1 in state.client2.received_messages
    assert m1 in state.client3.received_messages
    assert m2 not in state.client.received_messages
    assert m2 not in state.client2.received_messages
    assert m2 not in state.client3.received_messages
    assert m3 in state.client.received_messages
    assert m3 in state.client2.received_messages
    assert m3 in state.client3.received_messages
    assert m5 in state.client.received_messages
    assert m5 in state.client2.received_messages
    assert m5 in state.client3.received_messages


@pytest.mark.asyncio
async def test_server_adds_timestamp_to_message(state):
    # GIVEN
    await state.client.connect()

    # WHEN
    asyncio.create_task(state.client.start_receiving())
    await state.client.send("message")
    await asyncio.sleep(0.5)

    # THEN
    assert 1 == len(state.client.received_jsons)
    assert 'timestamp' in state.client.received_jsons[0][JsonFields.MESSAGE_VALUE]


@pytest.mark.asyncio
async def test_sending_previous_messages(state):
    # GIVEN
    database_mock = mocked_database.MockedDatabase()
    m1 = message.Message(1, 'sender', 'message1', 'room1', 123)
    m2 = message.Message(2, 'sender', 'message2', 'room1', 123)
    m3 = message.Message(3, 'sender', 'message3', 'room1', 123)
    database_mock.set_return_value('fetch_last_messages', [m1, m2, m3])
    state.server_obj.chatbox_database = database_mock
    await state.client.connect()
    asyncio.create_task(state.client.start_receiving())

    # WHEN
    await state.client.request_last_messages()
    await asyncio.sleep(1)

    # THEN
    assert state.client.received_messages == [m1.message, m2.message, m3.message]
