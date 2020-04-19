import socket
import time
import my_json

if __name__ == "__main__":

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)
    s.connect(server_address)

    try:
        d = {"message_type": "user", "message_value": "froggy"}
        print(d)
        d_json = my_json.to_json(d)
        time.sleep(5)
        s.sendall(d_json.encode())
        print('all sent')

        d = {"message_type": "message", "message_value": "alpacas"}
        print(d)
        d_json = my_json.to_json(d)
        time.sleep(5)
        s.sendall(d_json.encode())
        print('all sent')

        d = {"message_type": "message", "message_value": "sheep"}
        print(d)
        d_json = my_json.to_json(d)
        time.sleep(5)
        s.sendall(d_json.encode())
        print('all sent')

    finally:
        print('closing sender')
        s.close()