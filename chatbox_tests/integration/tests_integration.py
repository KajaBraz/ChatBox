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

    def test_dla_Kai_zeby_zoabczyla1(self):
        self.assertEqual(1, 1)
        self.assertNotEqual(1, 2)

    def test_dla_Kai_zeby_zoabczyla2(self):
        # GIVEN
        arg = 2
        tab = [1, 3]

        # WHEN
        tab.append(arg)

        # THEN
        self.assertIn(arg, tab)

    def test_client1_sends_client2_receives(self):
        asyncio.run(self.client1_sends_client2_receives())

    async def client1_sends_client2_receives(self):
        # GIVEN
        client2 = VirtualClient(self.address, self.port, self.room, 'user2')
        await self.server_obj.start(self.address, self.port)
        await self.client.connect()
        await client2.connect()

        # WHEN
        asyncio.create_task(client2.start_receiving())
        sent_task = asyncio.create_task(self.client.sent("message 1"))
        wait_task = asyncio.create_task(asyncio.sleep(0.5))
        await sent_task
        await wait_task

        # THEN
        self.assertEqual(self.client.sent_messages, client2.received_messages)

    def test_when_client_sends_message_is_added_to_database(self):
        asyncio.run(self.database_message())

    @patch('src.chatbox_websocket_server.add_message')
    async def database_message(self, add_message_mock: MagicMock):
        # GIVEN
        message = "hello darkness, my old friend"
        await self.server_obj.start(self.address, self.port)
        await self.client.connect()

        # WHEN
        await self.client.sent(message)
        await asyncio.sleep(0.5)

        # THEN
        add_message_mock.assert_called_once_with(self.client.user_name, self.client.chat_name, message, ANY)
