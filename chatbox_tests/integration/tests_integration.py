import asyncio
import unittest
from unittest.mock import patch, MagicMock, ANY

from chatbox_tests.integration.virtual_websocket_client import VirtualClient
from src import chatbox_websocket_server


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
        add_message_mock.assert_called_once_with(self.client.user_name, self.client.chat_name, message, ANY)
        self.server_obj.stop()

    def test_clients_join_chat_check_participants_num(self):
        asyncio.run(self.clients_join_chat_check_participants_num())

    async def clients_join_chat_check_participants_num(self):
        # GIVEN
        await self.server_obj.start(self.address, self.port)

        # WHEN
        await self.client.connect()
        await self.client2.connect()
        await self.client3.connect()

        # THEN
        self.assertEqual(3, len(self.server_obj.chat_participants[self.room]))
        self.server_obj.stop()
