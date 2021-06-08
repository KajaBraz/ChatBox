import asyncio
import websockets
from datetime import datetime, timezone
from sys import argv

import src.my_json as my_json
from src import helper_functions, database
from src.enums import JsonFields, MessageTypes


class Server:
    def __init__(self, config_file_path: str):
        self.chat_participants = {}
        self.server: websockets.WebSocketServer = None
        self.chatbox_database = None
        self.conn = None
        data = helper_functions.read_config(config_file_path)
        logs_file = data['logs']['log_file_name']
        self.log = helper_functions.set_logger(logs_file, data['logs']['to_console'])

    def remove_from_chat(self, chat, user_name):
        self.log.info(f'number of participants in chat {len(self.chat_participants[chat])} before removing')
        del self.chat_participants[chat][user_name]
        self.log.info(f'number of participants in chat {len(self.chat_participants[chat])} after removing')

    def get_num_of_chat_participants(self, chat_room):
        return len(self.chat_participants[chat_room])

    def remove_chat(self, chat_room):
        del self.chat_participants[chat_room]

    async def join_chat(self, user_name, chat_name, user_websocket):
        self.log.info(f'{user_websocket} - joining')
        if chat_name in self.chat_participants:
            self.chat_participants[chat_name][user_name] = user_websocket
            await self.send_new_user_notification([user_name], list(self.chat_participants.get(chat_name, [])),
                                                  chat_name)
        else:
            self.chat_participants[chat_name] = {user_name: user_websocket}
        self.log.info(
            f'number of participants in chat {chat_name} - {len(self.chat_participants[chat_name])}:'
            f'{self.chat_participants[chat_name]}')

    def update_and_save_message(self, message, chat_name, login, websocket):
        updated_message = message.copy()
        date_time = datetime.now(timezone.utc)
        time_millis = helper_functions.date_time_to_millis(date_time)
        self.chatbox_database.add_message(login, chat_name, updated_message[JsonFields.MESSAGE_VALUE], date_time)
        self.log.info(f'{websocket} - message {updated_message} added to db, room {chat_name}')
        updated_message[JsonFields.MESSAGE_TIMESTAMP] = time_millis
        return updated_message

    async def send_new_user_notification(self, user_name_list: list, receivers_logins: list, chat_name: str):
        self.log.info('sending new user notification')
        json_message = {JsonFields.MESSAGE_TYPE: MessageTypes.USERS_UPDATE,
                        JsonFields.MESSAGE_VALUE: user_name_list,
                        JsonFields.MESSAGE_DESTINATION: receivers_logins}
        for participant_login, participant_ws in self.chat_participants.get(chat_name, {}).items():
            self.log.info(f'sending notification to {participant_login}; json: {json_message}')
            self.log.info(f'participant_login: {participant_login}, receivers_logins: {receivers_logins}')
            if participant_login in receivers_logins:
                await participant_ws.send(my_json.to_json(json_message))

    async def receive(self, websocket: websockets.WebSocketServerProtocol, path: str):
        data, chat_name, login = '', '', ''
        try:
            self.log.info(f'{websocket} - waiting for messages')
            self.log.info(f'{websocket} - PATH {path}')
            if not helper_functions.check_url(path):
                await websocket.close(code=4000, reason='wrong login or chat name')
                self.log.info(f'websocket closed, wrong login or chat name')
                return

            path_items = path.split('/')
            login, chat_name = path_items[-1], path_items[-2]

            await self.join_chat(login, chat_name, websocket)
            self.log.info(f'{websocket} - {login} joined chat {chat_name}')

            async for data in websocket:
                try:
                    message = my_json.from_json(data)
                    self.log.info(f'{websocket} - raw data received: {data}')
                    self.log.info(f'{websocket} - message: {message}')

                    if message[JsonFields.MESSAGE_TYPE] == MessageTypes.PREVIOUS_MESSAGES:
                        if helper_functions.check_previous_messages_json(data):
                            self.log.info(f'{websocket} - previous messages json correct')
                            chat = message[JsonFields.MESSAGE_DESTINATION]
                            participants = list(self.chat_participants.get(chat, {}).keys())
                            past_messages = (self.chatbox_database.fetch_last_messages(chat))
                            for message in past_messages:
                                json_message = {JsonFields.MESSAGE_TYPE: MessageTypes.PREVIOUS_MESSAGES,
                                                JsonFields.MESSAGE_SENDER: message[0],
                                                JsonFields.MESSAGE_VALUE: message[1],
                                                JsonFields.MESSAGE_DESTINATION: message[2],
                                                JsonFields.MESSAGE_TIMESTAMP: helper_functions.date_time_to_millis(
                                                    message[3])}
                                await websocket.send(my_json.to_json(json_message))
                            self.log.info(f'{websocket} - past messages sent')
                            await self.send_new_user_notification(participants, [login], chat)

                    elif message[JsonFields.MESSAGE_TYPE] == MessageTypes.MESSAGE:
                        if helper_functions.check_message_json(data):
                            self.log.info(f'{websocket} - messages json correct')
                            updated_message = self.update_and_save_message(message, chat_name, login, websocket)
                            destination_chat_participants = self.chat_participants.get(
                                message[JsonFields.MESSAGE_DESTINATION], {})
                            for participant_sock in destination_chat_participants.values():
                                self.log.info(
                                    f'{websocket} - sending message to {participant_sock} in '
                                    f'{updated_message[JsonFields.MESSAGE_DESTINATION]}')
                                await participant_sock.send(my_json.to_json(updated_message))
                        # todo add test, when database connection is down, message is sent anyway
                        #  (that is why this must be after sending)
                except KeyError:
                    self.log.error(f'{websocket} - KeyError; improper json: {data}')
                except Exception as e:
                    self.log.exception(f"{websocket} - Unexpected error: {e}")
                # todo answer with an error json
        except Exception as e:
            self.log.exception(f"{websocket} - Unexpected error 2: {e}")
        if chat_name and login:
            self.remove_from_chat(chat_name, login)
            await self.send_new_user_notification([login], list(self.chat_participants[chat_name].keys()), chat_name)
            self.log.info(f'{websocket} - {login} left chat {chat_name}')
        if self.get_num_of_chat_participants(chat_name) == 0:
            self.remove_chat(chat_name)
            self.log.info(f'{chat_name} removed from the dictionary')
            self.log.info(f'remaining chat rooms: {self.chat_participants.keys()}')

    async def start(self, address, port):
        self.server = await websockets.serve(self.receive, address, port)
        self.log.info('chatbox started')
        # todo set websockets.serve logger

    async def wait_stop(self):
        await self.server.wait_closed()
        self.log.info('closed')

    def stop(self):
        self.log.info("closing chatbox")
        self.server.close()


async def main(config_file_path):
    data = helper_functions.read_config(config_file_path)
    address = data['address']['name']
    port = data['address']['port']
    server = Server(config_file_path)

    server.chatbox_database = database.ChatBoxDatabase(config_file_path)
    server.conn = server.chatbox_database.connect()
    await server.start(address, port)
    await server.wait_stop()


if __name__ == '__main__':
    if len(argv) > 1:
        asyncio.run(main(argv[1]))
    else:
        asyncio.run(main('../chatbox_config.json'))
