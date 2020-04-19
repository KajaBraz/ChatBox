import socket

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)
    s.connect(server_address)
    print('connected')
    while True:
        # try:
        data = s.recv(1024)
        data = data.decode()
        print(data)
        # finally:
        #     print('closing')
            # s.close()