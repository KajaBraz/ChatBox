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

    async def join_chat(self, user_name, chat_name, user_websocket):
        logging.info('joining')
        if chat_name in self.chat_participants:
            self.chat_participants[chat_name].append((user_name, user_websocket))
        else:
            self.chat_participants[chat_name] = [(user_name, user_websocket)]
        logging.info(f'chat participants {self.chat_participants}')

    async def receive(self, websocket: websockets.WebSocketServerProtocol, path: str):
        logging.info('waiting for messages')
        logging.info(f'PATH {path}')

        path_items = path.split('/')
        login, chat_name = path_items[-1], path_items[-2]

        logging.info(f'connecting {login}')
        await self.join_chat(login, chat_name, websocket)
        logging.info(f'{login} joined chat {chat_name}')

        async for data in websocket:
            try:
                message = my_json.from_json(data)
                logging.info(f'raw data received: {data}')
                logging.info(f'message: {message}')

                if message[JsonFields.MESSAGE_TYPE] == MessageTypes.ALL_USERS:
                    logged_users_message = {JsonFields.MESSAGE_TYPE: MessageTypes.ALL_USERS,
                                            JsonFields.MESSAGE_VALUE: list(self.logged_users.keys())}
                    await websocket.send(my_json.to_json(logged_users_message))
                    logging.info(f'get all logged: {self.logged_users.keys()}')

                elif message[JsonFields.MESSAGE_TYPE] == MessageTypes.MESSAGE:
                    destination_chat_participants = self.chat_participants.get(message[JsonFields.MESSAGE_DESTINATION],
                                                                               [])
                    for participant_sock in destination_chat_participants:
                        await participant_sock[1].send(data)

            except KeyError:
                logging.error(f'KeyError; improper json: {data}')
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
            # todo handle disconnecting user
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
