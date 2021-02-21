import asyncio
import logging
from sys import argv, stdout

import websockets

import src.my_json as my_json
from src.enums import JsonFields, MessageTypes

logged_users = {}
chat_participants = {}  # 'example_chat_name':[logged_users['user1'],logged_users['user2'],logged_users['userN']]


async def log_in(websocket, user_name, clients):
    # todo add lock/mutex to prevent thread race condition
    if user_name not in clients:
        clients[user_name] = websocket
        await websocket.send(my_json.to_json({JsonFields.MESSAGE_TYPE: MessageTypes.USER_NAME_RESPONSE,
                                              JsonFields.MESSAGE_VALUE: MessageTypes.LOGIN_ACCEPTED}))
        return True
    else:
        logging.info(f'client ({websocket}) entered already existing login: {user_name}')
        await websocket.send(my_json.to_json({JsonFields.MESSAGE_TYPE: MessageTypes.USER_NAME_RESPONSE,
                                              JsonFields.MESSAGE_VALUE: MessageTypes.LOGIN_ALREADY_USED}))
        return False


async def join_chat(user_name, chat_name):
    logging.info('joining')
    global logged_users
    global chat_participants
    user_websocket = logged_users[user_name]
    if chat_name in chat_participants:
        chat_participants[chat_name].append(user_websocket)
    else:
        chat_participants[chat_name] = [user_websocket]
    logging.info(f'chat participants {chat_participants}')


async def receive(websocket, path):
    logging.info('waiting for messages')
    global logged_users
    global chat_participants
    data = await websocket.recv()

    try:
        message = my_json.from_json(data)
        logging.info(f'raw data received: {data}')
        logging.info(f'message: {message}')

        if message[JsonFields.MESSAGE_TYPE] == MessageTypes.USER_LOGIN:
            login = message[JsonFields.MESSAGE_VALUE]
            await log_in(websocket, login, logged_users)
            logging.info(f'logging {login}')
            await join_chat(login, path[1:])
            logging.info(f'{login} joined chat {path[1:]}')

        elif message[JsonFields.MESSAGE_TYPE] == MessageTypes.ALL_USERS:
            logged_users_message = {JsonFields.MESSAGE_TYPE: MessageTypes.ALL_USERS,
                                    JsonFields.MESSAGE_VALUE: list(logged_users.keys())}
            await websocket.send(my_json.to_json(logged_users_message))
            logging.info(f'get all logged: {logged_users.keys()}')


        elif message[JsonFields.MESSAGE_TYPE] == MessageTypes.MESSAGE:
            destination_chat_participants = chat_participants.get(message[JsonFields.MESSAGE_DESTINATION], [])
            for participant_sock in destination_chat_participants:
                await participant_sock.send(data)

        await receive(websocket, path)

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
