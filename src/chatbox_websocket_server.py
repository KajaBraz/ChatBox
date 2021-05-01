import asyncio
import logging
import websockets
from datetime import datetime, timezone
from sys import argv

import src.my_json as my_json
from src import helper_functions
from src.database import connect, add_message, db_name, db_login, db_password, fetch_last_messages
from src.enums import JsonFields, MessageTypes

formatter = '%(asctime)s ; %(levelname)s ; %(filename)s ; %(lineno)d. ; %(message)s '
logging.basicConfig(format=formatter, level=logging.INFO)

log = logging.getLogger("chatbox_logger")


# logging.basicConfig(filename='logs.log', filemode='a', format=formatter, level=logging.DEBUG)
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

def date_time_to_millis(t: datetime) -> int:
    return int(t.timestamp() * 1000)


class Server:
    def __init__(self):
        self.chat_participants = {}
        self.logged_users = {}
        self.server: websockets.WebSocketServer = None
        self.conn = None

    def connect_to_db(self, db_name, db_login, db_password):
        self.conn = connect(db_name, db_login, db_password)
        log.info(f'server created connection to database {db_name}')

    def remove_from_chat(self, chat, user_name):
        log.info(f'number of participants in chat {len(self.chat_participants[chat])} before removing')
        del self.chat_participants[chat][user_name]
        log.info(f'number of participants in chat {len(self.chat_participants[chat])} after removing')

    def get_num_of_chat_participants(self, chat_room):
        return len(self.chat_participants[chat_room])

    def remove_chat(self, chat_room):
        del self.chat_participants[chat_room]

    async def join_chat(self, user_name, chat_name, user_websocket):
        log.info(f'{user_websocket} - joining')
        if chat_name in self.chat_participants:
            self.chat_participants[chat_name][user_name] = user_websocket
            await self.send_new_user_notification([user_name], list(self.chat_participants.get(chat_name, [])),
                                                  chat_name)
        else:
            self.chat_participants[chat_name] = {user_name: user_websocket}
        log.info(
            f'number of participants in chat {chat_name} - {len(self.chat_participants[chat_name])}:'
            f'{self.chat_participants[chat_name]}')

    def send_message(self):
        pass

    async def send_new_user_notification(self, user_name_list: list, receivers_logins: list, chat_name: str):
        log.info('sending new user notification')
        json_message = {JsonFields.MESSAGE_TYPE: MessageTypes.USERS_UPDATE,
                        JsonFields.MESSAGE_VALUE: user_name_list,
                        JsonFields.MESSAGE_DESTINATION: receivers_logins}
        for participant in self.chat_participants.get(chat_name, []).items():
            log.info(f'sending notification to {participant}; json: {json_message}')
            log.info(f'participant[0]: {participant[0]}, receivers_logins: {receivers_logins}')
            if participant[0] in receivers_logins:
                await participant[1].send(my_json.to_json(json_message))

    async def receive(self, websocket: websockets.WebSocketServerProtocol, path: str):
        data, chat_name, login = '', '', ''
        try:
            log.info(f'{websocket} - waiting for messages')
            log.info(f'{websocket} - PATH {path}')
            if not helper_functions.check_url(path):
                await websocket.close(code=4000, reason='wrong login or chat name')
                log.info(f'websocket closed, wrong login or chat name')
                return

            path_items = path.split('/')
            login, chat_name = path_items[-1], path_items[-2]

            await self.join_chat(login, chat_name, websocket)
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

                    elif message[JsonFields.MESSAGE_TYPE] == MessageTypes.PREVIOUS_MESSAGES:
                        chat = message[JsonFields.MESSAGE_DESTINATION]
                        participants = list(self.chat_participants.get(chat, []).keys())
                        past_messages = (fetch_last_messages(chat, self.conn))
                        for message in past_messages:
                            json_message = {JsonFields.MESSAGE_TYPE: MessageTypes.PREVIOUS_MESSAGES,
                                            JsonFields.MESSAGE_SENDER: message[0],
                                            JsonFields.MESSAGE_VALUE: message[1],
                                            JsonFields.MESSAGE_DESTINATION: message[2],
                                            JsonFields.MESSAGE_TIMESTAMP: date_time_to_millis(message[3])}
                            await websocket.send(my_json.to_json(json_message))
                        log.info(f'{websocket} - past messages sent')
                        await self.send_new_user_notification(participants, [login], chat)

                    elif message[JsonFields.MESSAGE_TYPE] == MessageTypes.MESSAGE:
                        destination_chat_participants = self.chat_participants.get(
                            message[JsonFields.MESSAGE_DESTINATION], [])

                        date_time = datetime.now(timezone.utc)
                        time_millis = date_time_to_millis(date_time)
                        add_message(login, chat_name, message[JsonFields.MESSAGE_VALUE], self.conn, date_time)
                        log.info(f'{websocket} - message {message} added to db, room {chat_name}')
                        message[JsonFields.MESSAGE_TIMESTAMP] = time_millis
                        for participant_sock in destination_chat_participants.items():
                            log.info(f'{websocket} - sending message to {participant_sock} in '
                                     f'{message[JsonFields.MESSAGE_DESTINATION]}')
                            await participant_sock[1].send(my_json.to_json(message))
                            # todo add test, when database connection is down, message is sent anyway (that is why this must be after sending)
                except KeyError:
                    log.error(f'{websocket} - KeyError; improper json: {data}')
                except Exception as e:
                    log.exception(f"{websocket} - Unexpected error: {e}")
                # todo answer with an error json
        except Exception as e:
            log.exception(f"{websocket} - Unexpected error 2: {e}")
        if chat_name and login:
            self.remove_from_chat(chat_name, login)
            await self.send_new_user_notification([login], list(self.chat_participants[chat_name].keys()), chat_name)
            log.info(f'{websocket} - {login} left chat {chat_name}')
        if self.get_num_of_chat_participants(chat_name) == 0:
            self.remove_chat(chat_name)
            log.info(f'{chat_name} removed from the dictionary')
            log.info(f'remaining chat rooms: {self.chat_participants.keys()}')

    async def start(self, address, port):
        self.server = await websockets.serve(self.receive, address, port)
        log.info('chatbox started')
        # todo set webosckets.serve logger

    async def wait_stop(self):
        await self.server.wait_closed()
        log.info('closed')

    def stop(self):
        log.info("closing chatbox")
        self.server.close()


async def main(address, port):
    server = Server()
    server.conn = connect(db_name, db_login, db_password)
    await server.start(address, port)
    await server.wait_stop()


if __name__ == '__main__':
    if len(argv) > 1:
        asyncio.run(main(argv[1], int(argv[2])))
    else:
        asyncio.run(main('localhost', 11000))
