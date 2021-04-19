import asyncio
import unittest
from unittest.mock import patch, MagicMock, ANY

from chatbox_tests.integration.virtual_websocket_client import VirtualClient
from src import chatbox_websocket_server
from src.enums import JsonFields


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.address = 'localhost'
        self.port = 11000
        self.room = "room1"
        self.server_obj = chatbox_websocket_server.Server()
        self.client = VirtualClient(self.address, self.port, self.room, 'user1')
        self.client2 = VirtualClient(self.address, self.port, self.room, 'user2')
        self.client3 = VirtualClient(self.address, self.port, self.room, 'user3')

    def test_client1_sends_participants_receive(self):
        asyncio.run(self.clients_send_all_participants_receive())

    async def clients_send_all_participants_receive(self):
        # GIVEN
        m1 = 'message 1'
        m2 = 'message 2'
        m3 = 'message 3'
        await self.server_obj.start(self.address, self.port)
        await self.client.connect()
        await self.client2.connect()

        # WHEN
        asyncio.create_task(self.client.start_receiving())
        asyncio.create_task(self.client2.start_receiving())
        sent_task1 = asyncio.create_task(self.client.send(m1))
        sent_task2 = asyncio.create_task(self.client2.send(m2))
        sent_task3 = asyncio.create_task(self.client2.send(m3))
        wait_task = asyncio.create_task(asyncio.sleep(0.5))
        await sent_task1
        await sent_task2
        await sent_task3
        await wait_task

        # THEN
        self.assertEqual(len(self.client.sent_messages + self.client2.sent_messages),
                         len(self.client2.received_messages))
        self.assertEqual(len(self.client.sent_messages + self.client2.sent_messages),
                         len(self.client.received_messages))
        self.assertIn(m1, self.client.received_messages)
        self.assertIn(m2, self.client.received_messages)
        self.assertIn(m3, self.client.received_messages)
        self.assertIn(m1, self.client2.received_messages)
        self.assertIn(m2, self.client2.received_messages)
        self.assertIn(m3, self.client2.received_messages)
        self.server_obj.stop()

    def test_when_client_sends_message_is_added_to_database(self):
        asyncio.run(self.database_message())

    @patch('src.chatbox_websocket_server.add_message')
    async def database_message(self, add_message_mock: MagicMock):
        # GIVEN
        message = "hello darkness, my old friend"
        await self.server_obj.start(self.address, self.port)
        await self.client.connect()
        await self.client2.connect()

        # WHEN
        await self.client.send(message)
        await asyncio.sleep(0.5)

        # THEN
        add_message_mock.assert_called_once_with(self.client.user_name, self.client.chat_name, message, ANY, ANY)
        add_message_mock.reset_mock()

        await self.client.send_not_a_json(message)
        await asyncio.sleep(0.5)
        add_message_mock.assert_not_called()
        add_message_mock.reset_mock()
        
        await self.client.send_wrong_message(message)
        await asyncio.sleep(0.5)
        add_message_mock.assert_not_called()

        self.server_obj.stop()

    def test_clients_join_and_leave_chat_check_participants_num(self):
        asyncio.run(self.clients_join_and_leave_chat_check_participants_num())

    async def clients_join_and_leave_chat_check_participants_num(self):
        # GIVEN
        await self.server_obj.start(self.address, self.port)

        # WHEN
        await self.client.connect()
        await self.client2.connect()
        await self.client3.connect()
        await self.client2.disconnect()
        await asyncio.sleep(0.5)

        # THEN
        logins = [user[0] for user in self.server_obj.chat_participants[self.room]]
        self.assertEqual(2, len(self.server_obj.chat_participants[self.room]))
        self.assertIn(self.client.user_name, logins)
        self.assertNotIn(self.client2.user_name, logins)
        self.assertIn(self.client3.user_name, logins)
        self.server_obj.stop()

    def test_server_receives_and_handles_wrong_message_then_serves_correctly_proper_messages(self):
        asyncio.run(self.server_receives_and_handles_wrong_message_then_serves_correctly_proper_messages())

    async def server_receives_and_handles_wrong_message_then_serves_correctly_proper_messages(self):
        # GIVEN
        await self.server_obj.start(self.address, self.port)
        await self.client.connect()
        await self.client2.connect()
        await self.client3.connect()
        m1 = 'message 1'
        m2 = 'message 2'
        m3 = 'message 3'
        m4 = 'message 4'
        m5 = 'message 5'

        # WHEN
        asyncio.create_task(self.client.start_receiving())
        asyncio.create_task(self.client2.start_receiving())
        asyncio.create_task(self.client3.start_receiving())
        send_task1 = asyncio.create_task(self.client.send(m1))
        send_task2 = asyncio.create_task(self.client2.send_wrong_message(m2))
        send_task3 = asyncio.create_task(self.client3.send(m3))
        send_task4 = asyncio.create_task(self.client2.send_not_a_json(m4))
        send_task5 = asyncio.create_task(self.client2.send(m5))
        wait_task = asyncio.create_task(asyncio.sleep(0.5))
        await send_task1
        await send_task2
        await send_task3
        await send_task4
        await send_task5
        await wait_task

        # THEN
        self.assertEqual(3, len(self.client.received_messages))
        self.assertEqual(3, len(self.client2.received_messages))
        self.assertEqual(3, len(self.client3.received_messages))
        self.assertIn(m1, self.client.received_messages)
        self.assertIn(m1, self.client2.received_messages)
        self.assertIn(m1, self.client3.received_messages)
        self.assertNotIn(m2, self.client.received_messages)
        self.assertNotIn(m2, self.client2.received_messages)
        self.assertNotIn(m2, self.client3.received_messages)
        self.assertIn(m3, self.client.received_messages)
        self.assertIn(m3, self.client2.received_messages)
        self.assertIn(m3, self.client3.received_messages)
        self.assertIn(m5, self.client.received_messages)
        self.assertIn(m5, self.client2.received_messages)
        self.assertIn(m5, self.client3.received_messages)
        self.server_obj.stop()

    def test_server_adds_timestamp_to_message(self):
        asyncio.run(self.server_adds_timestamp_to_message())

    async def server_adds_timestamp_to_message(self):
        # GIVEN
        await self.server_obj.start(self.address, self.port)
        await self.client.connect()

        # WHEN
        asyncio.create_task(self.client.start_receiving())
        await self.client.send("message")
        await asyncio.sleep(0.5)

        # THEN
        self.assertEqual(1, len(self.client.received_jsons))
        self.assertIn(JsonFields.MESSAGE_TIMESTAMP, self.client.received_jsons[0])
