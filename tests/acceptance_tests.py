import time
import unittest

import client
import server


class MyTestCase(unittest.TestCase):
    def test_send_receive(self):
        server_name, port = 'localhost', 10000
        client1 = client.ChatBoxClient()
        client2 = client.ChatBoxClient()
        name1 = 'bolognese'
        name2 = 'maltipoo'
        message1 = 'baubau'

        server.start_server(server_name, port)
        client1.connect(server_name, port)
        client2.connect(server_name, port)
        client1.login(name1)
        users = client2.get_users_list()
        self.assertEqual([name1], users, 'wrong users list')
        client2.login(name2)
        client1.send_message(message1, name2, name1)
        read_message1 = client2.receive()
        self.assertEqual(message1, read_message1, 'wrong message received')
        client2.send_message('baubaubau', name1, name2)
        client1.close()
        client2.close()


if __name__ == '__main__':
    unittest.main()
