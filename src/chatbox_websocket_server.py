import asyncio
import logging
from sys import argv

import websockets

import src.my_json as my_json
from src.enums import JsonFields, MessageTypes


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


async def receive(websocket, path):
    print("start")
    global logged_users
    print("czekam")
    data = await websocket.recv()
    print("data ", data)
    try:
        print("try")
        logging.info(f'raw socket: {data}')
        # if not data:
        #     logging.warning('Empty data, connection is probably lost, break')
        #     logged_users.pop(present_user, None)
        #     break
        print("message")
        message = my_json.from_json(data)
        logging.info(f'data received: {message}')
        print("if")
        if message[JsonFields.MESSAGE_TYPE] == MessageTypes.USER_LOGIN:
            print("przed loguje")
            login = message[JsonFields.MESSAGE_VALUE]
            print("loguje")
            log_in_done = await log_in(websocket, login, logged_users)
            print("po logowaniu")
            logging.info(f'login: {login}')

        elif message[JsonFields.MESSAGE_TYPE] == MessageTypes.ALL_USERS:
            logged_users_message = {JsonFields.MESSAGE_TYPE: MessageTypes.ALL_USERS,
                                    JsonFields.MESSAGE_VALUE: list(logged_users.keys())}
            # sock.sendall(my_json.to_json(logged_users_message))
            await websocket.send(my_json.to_json(logged_users_message))
            logging.info('get all logged')
        elif message[JsonFields.MESSAGE_TYPE] == MessageTypes.MESSAGE:
            receiver_sock = logged_users.get(message[JsonFields.MESSAGE_RECEIVER], None)
            if receiver_sock:
                await receiver_sock.send(data)
            else:
                logging.warning('socket not found')
        print("tu?")
        await receive(websocket, path)
    except KeyError:
        print("error 1")
        logging.error(f'KeyError; improper json: {data}')
    except Exception as e:
        print("error 2: ", e)
        logging.error(f"Unexpected error: {e}")
    # todo handle disconnecting user
    # todo answer with an error json


logged_users = {}


async def main(address, port):
    print("1")
    server = await websockets.serve(receive, address, port)
    print("2")
    # todo set webosckets.serve logger
    await server.wait_closed()
    print("3")


if __name__ == '__main__':
    f = '%(asctime)s - %(levelname)s - %(thread)d - %(threadName)s - %(filename)s - %(lineno)d. - %(message)s'
    logging.basicConfig(filename='logs.log', filemode='a', format=f, level=logging.DEBUG)
    if len(argv) > 1:
        asyncio.run(main(argv[1], int(argv[2])))
    else:
        print('start')
        asyncio.run(main('localhost', 11000))
