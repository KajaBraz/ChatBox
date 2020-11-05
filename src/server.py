from sys import argv
import socket
import threading
import logging

import src.my_json as my_json
from src.enums import JsonFields, MessageTypes


def run_server(host, port):
    all_clients = {}
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)  # queue up to 5 requests

    while True:
        client_socket, client_address = s.accept()
        t = threading.Thread(target=thread_function, args=[client_socket, client_address, all_clients])
        t.start()


def start_server(host, port, is_daemon=True):
    t = threading.Thread(target=run_server, args=[host, port], daemon=is_daemon)
    t.start()
    return t


def log_in(sock, address, user_name, clients):
    # todo add lock/mutex to prevent thread race condition
    if user_name not in clients:
        clients[user_name] = (sock, address)
        sock.sendall(my_json.to_json({JsonFields.MESSAGE_TYPE: MessageTypes.USER_NAME_RESPONSE,
                                      JsonFields.MESSAGE_VALUE: MessageTypes.LOGIN_ACCEPTED}))
        return True
    else:
        logging.info(f'client ({address}) entered already existing login: {user_name}')
        sock.sendall(my_json.to_json({JsonFields.MESSAGE_TYPE: MessageTypes.USER_NAME_RESPONSE,
                                      JsonFields.MESSAGE_VALUE: MessageTypes.LOGIN_ALREADY_USED}))
        return False


def thread_function(sock, address, logged_users):
    present_user = ''
    while True:
        data = ''
        try:
            data = sock.recv(1024)
            logging.info('raw socket', data)
            if not data:
                logging.warning('Empty data, connection is probably lost, break')
                logged_users.pop(present_user, None)
                break
            message = my_json.from_json(data)
            logging.info('data received', message)
            if message[JsonFields.MESSAGE_TYPE] == MessageTypes.USER_LOGIN:
                login = message[JsonFields.MESSAGE_VALUE]
                log_in_done = log_in(sock, address, login, logged_users)
                if log_in_done:
                    present_user = message[JsonFields.MESSAGE_VALUE]
                logging.info('login', login)
                logging.info('present user', present_user)
            elif message[JsonFields.MESSAGE_TYPE] == MessageTypes.ALL_USERS:
                logged_users_message = {JsonFields.MESSAGE_TYPE: MessageTypes.ALL_USERS,
                                        JsonFields.MESSAGE_VALUE: list(logged_users.keys())}
                sock.sendall(my_json.to_json(logged_users_message))
                logging.info('get all logged')
            elif message[JsonFields.MESSAGE_TYPE] == MessageTypes.MESSAGE:
                receiver_sock, receiver_addr = logged_users.get(message[JsonFields.MESSAGE_RECEIVER], (None, None))
                if receiver_sock:
                    receiver_sock.sendall(data)
                else:
                    logging.warning('socket not found')
        except KeyError:
            logging.error('KeyError; improper json', data)
        except ConnectionResetError:
            logged_users.pop(present_user, None)
            logging.error(f'exception ConnectionResetError, user {present_user} deleted')
            break
        # todo handle disconnecting user
        # todo answer with an error json


if __name__ == '__main__':
    logging.basicConfig(filename='logs.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%H:%M:%S', level=logging.DEBUG)
    if len(argv) > 1:
        thread_server = start_server(argv[1], int(argv[2]), False)
    else:
        thread_server = start_server('localhost', 10000, False)
    logging.info(thread_server.isDaemon())
