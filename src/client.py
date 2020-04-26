import socket
import threading
import time
import my_json
from enums import JsonFields, MessageTypes


class ChatBoxClient(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, server_address='localhost', server_port=10000):
        self.sock.connect((server_address, server_port))

    def wait_for_message(self) -> dict:
        bytes_message = self.sock.recv(1024)
        dict_message = my_json.from_json(bytes_message)
        return dict_message

    def receive(self) -> str:
        d = self.wait_for_message()
        return d[JsonFields.MESSAGE_VALUE]

    def receive_and_print(self):
        while True:
            received = self.receive()
            print(received)

    def login(self, login_name):
        login_data = {JsonFields.MESSAGE_TYPE: MessageTypes.USER_LOGIN, JsonFields.MESSAGE_VALUE: login_name}
        login_data_json = my_json.to_json(login_data)
        self.sock.sendall(login_data_json)
        self.receive()

    def send_message(self, message: str, receiver: str):
        data = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE, JsonFields.MESSAGE_VALUE: message,
                JsonFields.MESSAGE_RECEIVER: receiver}
        data_json = my_json.to_json(data)
        self.sock.sendall(data_json)

    def get_users_list(self) -> list:
        request = {JsonFields.MESSAGE_TYPE: MessageTypes.ALL_USERS}
        request_json = my_json.to_json(request)
        self.sock.sendall(request_json)
        users = self.wait_for_message()
        users_list = users[JsonFields.MESSAGE_VALUE]
        return users_list

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
        client.send_message(message, interlocutor_name)
