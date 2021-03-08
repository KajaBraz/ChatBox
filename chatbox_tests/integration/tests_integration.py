import asyncio
import unittest

from src.chatbox_websocket_server import Server
from chatbox_tests.integration.virtual_websocket_client import VirtualClient


class MyTestCase(unittest.TestCase):
    # def __init__(self):
    #     super().__init__()
    #     self.address = 'localhost'
    #     self.port = 11000
    #     self.room = 'room1'

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
        address = 'localhost'
        port = 11000
        room = 'room1'
        server_obj = Server()
        client1 = VirtualClient(address, port, room, 'user1')
        client2 = VirtualClient(address, port, room, 'user2')
        await server_obj.start(address, port)
        await client1.connect()
        await client2.connect()

        # WHEN
        asyncio.create_task(client2.start_receiving())
        sent_task = asyncio.create_task(client1.sent("message 1"))
        wait_task = asyncio.create_task(asyncio.sleep(0.5))
        await sent_task
        await wait_task

        # THEN
        self.assertEqual(client1.sent_messages, client2.received_messages)
