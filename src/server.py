import socket
import src.my_json as my_json

if __name__ == '__main__':

    all_clients = []

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 9999
    s.bind((host, port))
    s.listen(5)  # queue up to 5 requests

    while True:
        client_socket, client_address = s.accept()
        client_socket2, client_address2 = s.accept()
        try:
            while True:
                data = client_socket.recv(16)
                data_str = data.decode("utf-8")
                data_json = my_json.to_json(data_str)
                if my_json.is_proper_json(data_json):
                    if data_json["message_type"]=="user"
                        login = data_json["message_value"]
                        logged_in(login)
                    if data_json["message_type"]=="get_all_logged":
                        s.sendto(all_clients, login)
                    if data_json["message_type"]=="message":
                        message = data_json["message_value"]
                        s.sendto(message,data_json["message_receiver"])


        finally:
            client_socket.close()

def logged_in(login, all_clients):
    if login not in all_clients:
        all_clients.add(login)
        # for c in clients:
            #