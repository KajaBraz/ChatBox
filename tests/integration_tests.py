import asyncio
import unittest
import websockets
from src.chatbox_websocket_server import Server, main
from src.virtual_websocket_client import client


class MyTestCase(unittest.TestCase):
    def __init__(self):
        super().__init__()
        self.address = 'localhost'
        self.port = 11000

    def test_server_client_send_mess(self):
        # server_obj = Server()
        # server = await websockets.serve(server_obj.receive, self.address,self.port)
        # await server.wait_closed()

        res = asyncio.run(main(self.address,self.port))

        await client(self.address,self.port,'ciao belli!','psiaki','flavia')
        await asyncio.sleep(10)
        await client(self.address,self.port,'ciao ciao ciao', 'psiaki', 'pino')