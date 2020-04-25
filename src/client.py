import socket
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
    pass
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_addresss = ('localhost', 10000)
    # s.connect(server_address)
    #
    # try:
    #     d = {"message_type": "user", "message_value": "froggy"}
    #     print(d)
    #     d_json = my_json.to_json(d)
    #     time.sleep(5)
    #     s.sendall(d_json)
    #     print('all sent')
    #
    #     d = {"message_type": "message", "message_value": "alpacas"}
    #     print(d)
    #     d_json = my_json.to_json(d)
    #     time.sleep(5)
    #     s.sendall(d_json)
    #     print('all sent')
    #
    #     d = {"message_type": "message", "message_value": "sheep"}
    #     print(d)
    #     d_json = my_json.to_json(d)
    #     time.sleep(5)
    #     s.sendall(d_json)
    #     print('all sent')
    #
    # finally:
    #     print('closing sender')
    #     s.close()
