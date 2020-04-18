import socket
import my_json


if __name__ == '__main__':

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 9999
    s.bind((host, port))
    s.listen(5) # queue up to 5 requests

    while True:
        client_socket, client_address = s.accept()
        client_socket2, client_address2 = s.accept()
        try:
            while True:
                data = client_socket.recv(16)
                data_str = data.decode("utf-8")
                data_json = my_json.to_json(data_str)
                if my_json.is_proper_json(data_json):
                    if data_json["message_type"]=="message":
                        s.sendto(data_json,client_socket2)

        finally:
            client_socket.close()

    # def logged_in():
        # for c in clients:
            #