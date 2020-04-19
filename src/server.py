import socket
# import src.my_json as my_json
import my_json


def logged_in(user_name, clients):
    if user_name not in clients:
        clients.append(user_name)


if __name__ == '__main__':

    all_clients = []

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'localhost'
    port = 10000
    s.bind((host, port))
    s.listen(5)  # queue up to 5 requests

    while True:
        client_socket, client_address = s.accept()
        client_socket2, client_address2 = s.accept()
        try:
            while True:
                data = client_socket.recv(1024)
                data_str = data.decode("utf-8")
                data_json = my_json.from_json(data_str)
                print('data received', data_json)
                if my_json.is_proper_json(data_json):
                    if data_json["message_type"] == "user":
                        login = data_json["message_value"]
                        logged_in(login, all_clients)
                        print(login)
                    elif data_json["message_type"] == "get_all_logged":
                        client_socket2.sendall(str(all_clients).encode())
                        print('get all logged')
                    elif data_json["message_type"] == "message":
                        message = data_json["message_value"]
                        client_socket2.sendall(message.encode())
                        print(message)
                else:
                    print('else')
                    break
        finally:
            print('closing server')
            client_socket.close()
