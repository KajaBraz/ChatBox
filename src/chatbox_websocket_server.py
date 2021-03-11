import asyncio
import logging
import websockets
import src.my_json as my_json
from src.enums import JsonFields, MessageTypes
from sys import argv
from src.database import connect, add_message, db_name, db_login, db_password


class Server:
    def __init__(self):
        self.chat_participants = {}
        self.logged_users = {}
        self.server = None

    def remove_from_chat(self, chat, user_name, user_websocket):
        users = self.chat_participants[chat]
        self.chat_participants[chat] = [user for user in users if user != (user_name, user_websocket)]

    def join_chat(self, user_name, chat_name, user_websocket):
        log.info(f'{user_websocket} - joining')
        if chat_name in self.chat_participants:
            self.chat_participants[chat_name].append((user_name, user_websocket))
        else:
            self.chat_participants[chat_name] = [(user_name, user_websocket)]
        log.info(f'{user_websocket} - chat participants {self.chat_participants}')

    async def receive(self, websocket: websockets.WebSocketServerProtocol, path: str):
        log.info(f'{websocket} - waiting for messages')
        log.info(f'{websocket} - PATH {path}')

        path_items = path.split('/')
        login, chat_name = path_items[-1], path_items[-2]

        conn = connect(db_name, db_login, db_password)

        log.info(f'{websocket} - connecting {login}')
        self.join_chat(login, chat_name, websocket)
        log.info(f'{websocket} - {login} joined chat {chat_name}')

        async for data in websocket:
            try:
                message = my_json.from_json(data)
                log.info(f'{websocket} - raw data received: {data}')
                log.info(f'{websocket} - message: {message}')

                if message[JsonFields.MESSAGE_TYPE] == MessageTypes.ALL_USERS:
                    logged_users_message = {JsonFields.MESSAGE_TYPE: MessageTypes.ALL_USERS,
                                            JsonFields.MESSAGE_VALUE: list(self.logged_users.keys())}
                    await websocket.send(my_json.to_json(logged_users_message))
                    log.info(f'{websocket} - get all logged: {self.logged_users.keys()}')

                elif message[JsonFields.MESSAGE_TYPE] == MessageTypes.MESSAGE:
                    destination_chat_participants = self.chat_participants.get(message[JsonFields.MESSAGE_DESTINATION],
                                                                               [])

                    for participant_sock in destination_chat_participants:
                        log.info(f'{websocket} - sending message to {participant_sock} in '
                                 f'{message[JsonFields.MESSAGE_DESTINATION]}')
                        await participant_sock[1].send(data)
                    # todo add test, when database connection is down, message is sent anyway (that is why this must be after sending)
                    add_message(login, chat_name, message[JsonFields.MESSAGE_VALUE], conn)

            except KeyError:
                log.error(f'{websocket} - KeyError; improper json: {data}')
            except Exception as e:
                log.exception(f"{websocket} - Unexpected error: {e}")
        self.remove_from_chat(chat_name, login, websocket)
        log.info(f'{websocket} - {login} left chat {chat_name}')
        # todo answer with an error json

    async def start(self, address, port):
        self.server = await websockets.serve(self.receive, address, port)
        log.info('chatbox started')
        # todo set webosckets.serve logger

    async def stop(self):
        await self.server.wait_closed()
        log.info('closed')


async def main(address, port):
    server = Server()
    await server.start(address, port)
    await server.stop()


if __name__ == '__main__':
    formatter = '%(asctime)s ; %(levelname)s ; %(filename)s ; %(lineno)d. ; %(message)s '
    logging.basicConfig(format=formatter, level=logging.INFO)

    # logging.basicConfig(filename='logs.log', filemode='a', format=formatter, level=logging.DEBUG)
    log = logging.getLogger("chatbox_logger")

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
