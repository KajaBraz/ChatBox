import asyncio
import logging
import websockets
import src.my_json as my_json
from src.enums import JsonFields, MessageTypes
from sys import argv


class Server():
    def __init__(self):
        self.chat_participants = {}
        self.logged_users = {}

    def remove_from_chat(self, chat, user_name, user_websocket):
        users = self.chat_participants[chat]
        self.chat_participants[chat] = [user for user in users if user != (user_name, user_websocket)]

    def join_chat(self, user_name, chat_name, user_websocket):
        logging.info(f'{user_websocket} - joining')
        if chat_name in self.chat_participants:
            self.chat_participants[chat_name].append((user_name, user_websocket))
        else:
            self.chat_participants[chat_name] = [(user_name, user_websocket)]
        logging.info(f'{user_websocket} - chat participants {self.chat_participants}')

    async def receive(self, websocket: websockets.WebSocketServerProtocol, path: str):
        logging.info(f'{websocket} - waiting for messages')
        logging.info(f'{websocket} - PATH {path}')

        path_items = path.split('/')
        login, chat_name = path_items[-1], path_items[-2]

        logging.info(f'{websocket} - connecting {login}')
        self.join_chat(login, chat_name, websocket)
        logging.info(f'{websocket} - {login} joined chat {chat_name}')

        async for data in websocket:
            try:
                message = my_json.from_json(data)
                logging.info(f'{websocket} - raw data received: {data}')
                logging.info(f'{websocket} - message: {message}')

                if message[JsonFields.MESSAGE_TYPE] == MessageTypes.ALL_USERS:
                    logged_users_message = {JsonFields.MESSAGE_TYPE: MessageTypes.ALL_USERS,
                                            JsonFields.MESSAGE_VALUE: list(self.logged_users.keys())}
                    await websocket.send(my_json.to_json(logged_users_message))
                    logging.info(f'{websocket} - get all logged: {self.logged_users.keys()}')

                elif message[JsonFields.MESSAGE_TYPE] == MessageTypes.MESSAGE:
                    destination_chat_participants = self.chat_participants.get(message[JsonFields.MESSAGE_DESTINATION],
                                                                               [])
                    for participant_sock in destination_chat_participants:
                        logging.info(
                            f'{websocket} - sending message to {participant_sock} in '
                            f'{message[JsonFields.MESSAGE_DESTINATION]}')
                        await participant_sock[1].send(data)

            except KeyError:
                logging.error(f'{websocket} - KeyError; improper json: {data}')
            except Exception as e:
                logging.error(f"{websocket} - Unexpected error: {e}")
        self.remove_from_chat(chat_name, login, websocket)
        logging.info(f'{websocket} - {login} left chat {chat_name}')
        # todo answer with an error json


async def main(address, port):
    my_server = Server()
    server = await websockets.serve(my_server.receive, address, port)
    logging.info('awaiting')
    # todo set webosckets.serve logger
    await server.wait_closed()
    logging.info('closed')


if __name__ == '__main__':
    formatter = '%(asctime)s ; %(levelname)s ; %(filename)s ; %(lineno)d. ; %(message)s '
    logging.basicConfig(format=formatter, level=logging.INFO)

    # logging.basicConfig(filename='logs.log', filemode='a', format=formatter, level=logging.DEBUG)

    if len(argv) > 1:
        asyncio.run(main(argv[1], int(argv[2])))
    else:
        asyncio.run(main('localhost', 11000))
    # TODO reconsider logging handlers
    # logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)
    #
    # output_file_handler = logging.FileHandler('logs.log')
    # stdout_handler = logging.StreamHandler(stdout)
    #
    # output_file_handler.setFormatter(formatter)
    # stdout_handler.setFormatter(formatter)
    #
    # logger.addHandler(output_file_handler)
    # logger.addHandler(stdout_handler)
