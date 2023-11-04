import websockets

from src import helper_functions
from src.enums import JsonFields, MessageTypes, Constants
from src.my_json import to_json, from_json


class VirtualClient:
    def __init__(self, address, port, chat_name, user_name):
        self.ws = None
        self.sent_messages = []
        self.received_messages = []
        self.received_jsons = []
        self.address = address
        self.port = port
        self.chat_name = chat_name
        self.user_name = user_name + helper_functions.generate_random_string(Constants.LOGIN_ID_SUFFIX_LENGTH)

    async def connect(self):
        url = f'ws://{self.address}:{self.port}/{self.chat_name}/{self.user_name}'
        self.ws = await websockets.connect(url)
        # self.ws = websockets.connect(url)

    async def send(self, message):
        # TODO hardcoded data, even if the function is used also for previous messages type
        json_mess = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                     JsonFields.MESSAGE_VALUE: message,
                     JsonFields.MESSAGE_DESTINATION: self.chat_name,
                     JsonFields.MESSAGE_SENDER: self.user_name}
        self.sent_messages.append(message)
        json = to_json(json_mess)
        await self.ws.send(json)
        # self.ws.send(to_json(json_mess))

    async def send_wrong_message(self, message):
        json_mess = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                     JsonFields.MESSAGE_VALUE: message,
                     JsonFields.MESSAGE_SENDER: self.user_name}
        self.sent_messages.append(message)
        await self.ws.send(to_json(json_mess))

    async def send_not_a_json(self, message):
        self.sent_messages.append(message)
        await self.ws.send(message)

    async def start_receiving(self):
        async for data in self.ws:
            msg = from_json(data)
            if msg[JsonFields.MESSAGE_TYPE] == MessageTypes.MESSAGE:
                self.received_messages.append(msg[JsonFields.MESSAGE_VALUE]['message'])
                self.received_jsons.append(msg)
            elif msg[JsonFields.MESSAGE_TYPE] in [MessageTypes.PREVIOUS_MESSAGES, MessageTypes.MORE_PREVIOUS_MESSAGES]:
                self.received_messages.extend(m['message'] for m in msg[JsonFields.MULTIPLE_MESSAGES])
                self.received_jsons.append(msg)
            else:
                self.received_jsons.append(msg)

    async def request_last_messages(self):
        json_message = {JsonFields.MESSAGE_TYPE: MessageTypes.PREVIOUS_MESSAGES, JsonFields.MESSAGE_VALUE: -1,
                        JsonFields.MESSAGE_SENDER: 'sender1', JsonFields.MESSAGE_DESTINATION: 'room1'}
        await self.ws.send(to_json(json_message))

    async def scroll_and_request_more_messages(self):
        json_message = {JsonFields.MESSAGE_TYPE: MessageTypes.MORE_PREVIOUS_MESSAGES, JsonFields.MESSAGE_VALUE: 1,
                        JsonFields.MESSAGE_SENDER: 'sender1', JsonFields.MESSAGE_DESTINATION: 'room1'}
        await self.ws.send(to_json(json_message))

    async def disconnect(self):
        await self.ws.close()
