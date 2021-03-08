import websockets

from src.enums import JsonFields, MessageTypes
from src.my_json import to_json, from_json


class VirtualClient:
    def __init__(self, address, port, chat_name, user_name):
        self.ws = None
        self.sent_messages = []
        self.received_messages = []
        self.address = address
        self.port = port
        self.chat_name = chat_name
        self.user_name = user_name

    async def connect(self):
        url = f'ws://{self.address}:{self.port}/{self.chat_name}/{self.user_name}'
        self.ws = await websockets.connect(url)
        # self.ws = websockets.connect(url)

    async def sent(self, message):
        json_mess = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                     JsonFields.MESSAGE_VALUE: message,
                     JsonFields.MESSAGE_DESTINATION: self.chat_name,
                     JsonFields.MESSAGE_SENDER: self.user_name}
        print('sent', json_mess)
        self.sent_messages.append(message)
        await self.ws.send(to_json(json_mess))
        # self.ws.send(to_json(json_mess))

    async def start_receiving(self):
        async for data in self.ws:
            print('received', data)
            msg = from_json(data)
            self.received_messages.append(msg[JsonFields.MESSAGE_VALUE])
        # r = await self.ws.recv()

    async def disconnect(self):
        await self.ws.close()
