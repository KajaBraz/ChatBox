import asyncio
import logging
from sys import argv, stdout

import websockets

import src.my_json as my_json
from src.enums import JsonFields, MessageTypes

chat_participants = {}  # 'example_chat_name':[("user1", websocket_object1), ("user2", websocket_object2), ("userN", websocket_object_N)]


async def join_chat(user_name, chat_name, user_websocket):
    logging.info('joining')
    global chat_participants
    if chat_name in chat_participants:
        chat_participants[chat_name].append((user_name, user_websocket))
    else:
        chat_participants[chat_name] = [(user_name, user_websocket)]
    logging.info(f'chat participants {chat_participants}')


async def receive(websocket: websockets.WebSocketServerProtocol, path: str):
    logging.info('waiting for messages')
    global logged_users
    global chat_participants

    logging.info(f'PATH {path}')

    path_items = path.split('/')
    login, chat_name = path_items[-1], path_items[-2]

    logging.info(f'connecting {login}')
    await join_chat(login, chat_name, websocket)
    logging.info(f'{login} joined chat {chat_name}')

    async for data in websocket:
        try:
            message = my_json.from_json(data)
            logging.info(f'raw data received: {data}')
            logging.info(f'message: {message}')

            if message[JsonFields.MESSAGE_TYPE] == MessageTypes.ALL_USERS:
                logged_users_message = {JsonFields.MESSAGE_TYPE: MessageTypes.ALL_USERS,
                                        JsonFields.MESSAGE_VALUE: list(logged_users.keys())}
                await websocket.send(my_json.to_json(logged_users_message))
                logging.info(f'get all logged: {logged_users.keys()}')

            elif message[JsonFields.MESSAGE_TYPE] == MessageTypes.MESSAGE:
                destination_chat_participants = chat_participants.get(message[JsonFields.MESSAGE_DESTINATION], [])
                for participant_sock in destination_chat_participants:
                    await participant_sock[1].send(data)

        except KeyError:
            logging.error(f'KeyError; improper json: {data}')
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        # todo handle disconnecting user
        # todo answer with an error json


async def main(address, port):
    server = await websockets.serve(receive, address, port)
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
