import socket
import threading

import src.my_json as my_json
from src.enums import JsonFields, MessageTypes


class ChatBoxClient(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, server_addr='localhost', server_port=10000):
        self.sock.connect((server_addr, server_port))

    def wait_for_message(self) -> dict:
        bytes_message = self.sock.recv(1024)
        dict_message = my_json.from_json(bytes_message)
        return dict_message

    # todo fix the error which occures when closing the client window using Esc button instead of clicking 'x' in the
    #  right corner, an error occures

    def receive(self) -> str:
        d = self.wait_for_message()
        return d[JsonFields.MESSAGE_VALUE]

    def receive_and_print(self):
        while True:
            received = self.receive()
            print(received)

    def login(self, login_name):
        # todo this method should be removed (is not asynchronous)
        self.send_login(login_name)
        self.receive()

    def send_login(self, login_name):
        login_data = {JsonFields.MESSAGE_TYPE: MessageTypes.USER_LOGIN, JsonFields.MESSAGE_VALUE: login_name}
        login_data_json = my_json.to_json(login_data)
        self.sock.sendall(login_data_json)

    def send_message(self, mess: str, receiver: str, sender: str):
        data = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE, JsonFields.MESSAGE_VALUE: mess,
                JsonFields.MESSAGE_RECEIVER: receiver,
                JsonFields.MESSAGE_SENDER: sender}
        data_json = my_json.to_json(data)
        self.sock.sendall(data_json)

    def get_users_list(self) -> list:
        self.send_get_users_list()
        # todo here is bug, if another users send us MESSAGE before we receive login response there will be crash
        #  asynchronous methods should be used, i.e. dont wait here for response! just send request (ALL KINDS of
        #  responses should be processed in 'receive method')
        users = self.wait_for_message()
        users_list = users[JsonFields.MESSAGE_VALUE]
        return users_list

    def send_get_users_list(self):
        request = {JsonFields.MESSAGE_TYPE: MessageTypes.ALL_USERS}
        request_json = my_json.to_json(request)
        self.sock.sendall(request_json)

    def close(self):
        self.sock.close()


if __name__ == "__main__":
    client = ChatBoxClient()
    my_address = 'localhost'
    server_address = input('Welcome to ChatBox. What is your server address, sir? ')
    port = 10000
    client.connect(server_address, port)
    login = input('What login would you like to use, sir? ')
    client.login(login)
    print('Nice to meet you', login)
    print(client.get_users_list())
    interlocutor_name = input('Here is the list of members who are present now. Who would you like to talk to? ')
    print(f'Your conversation with {interlocutor_name} has been started.')
    th = threading.Thread(target=client.receive_and_print, daemon=True)
    th.start()
    while True:
        message = input()
        client.send_message(message, interlocutor_name, login)
