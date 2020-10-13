from sys import argv
import threading
import tkinter as tk

import src.client as client
from src.enums import JsonFields, MessageTypes


class Message:
    MAX_MESSAGES = 15

    def __init__(self, master_element, text, author_me=True):
        if author_me:
            color = 'skyblue'
            justice = tk.LEFT
        else:
            color = 'lightblue'
            justice = tk.RIGHT

        self.text = text
        self.author_me = author_me
        self.frame = tk.Frame(master=master_element, bg=color, bd=2)
        self.pack()
        self.label = tk.Label(master=self.frame, text=text, bg=color)
        self.label.pack(side=justice)

    def set_visible(self):
        self.pack()

    def set_invisible(self):
        self.frame.pack_forget()

    def pack(self):
        self.frame.pack(fill=tk.X)

    def destroy(self):
        self.label.destroy()
        self.frame.destroy()


class Gui(tk.Frame):
    def __init__(self):
        self.client_api = client.ChatBoxClient()
        self.my_login = ""

        # todo refactor init method, there is big mess
        self.window = tk.Tk()
        self.window.geometry("500x500")
        super().__init__(self.window)
        self.v = 0
        self.window.bind("<Return>", self.send_message)
        self.window.bind("<KeyPress-Escape>", self.exit_program)

        self.frm_users = tk.Frame(borderwidth=5, relief='ridge')
        self.btn_refresh = tk.Button(text='refresh', master=self.frm_users,
                                     command=lambda: self.client_api.send_get_users_list())
        self.btn_refresh.pack()
        self.frm_users.pack(fill=tk.Y, side=tk.RIGHT)
        self.frm_text = tk.Frame(borderwidth=5, relief='ridge')
        self.frm_text.pack(fill=tk.BOTH, expand=True)
        self.frm_send = tk.Frame(master=self.frm_text)
        self.frm_send.pack(fill=tk.X, side=tk.BOTTOM)
        self.frm_messages = tk.Frame(master=self.frm_text)
        self.frm_messages.pack(fill=tk.X, side=tk.BOTTOM)
        self.text_input = tk.Entry(master=self.frm_send, borderwidth=3)
        self.text_input.focus()
        self.text_input.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.btn_send = tk.Button(master=self.frm_send, text="send", command=lambda: self.send_message(None))
        self.btn_send.pack(side=tk.RIGHT)
        self.messages = {}  # todo rethink message per user memoization
        self.logged_users = {}
        self.active_user = ""

    def refresh_logged(self, user_list):
        for user_name, user_button in self.logged_users.items():
            user_button.destroy()
        self.logged_users = {}
        for user in user_list:
            b = tk.Button(text=user, master=self.frm_users, borderwidth=0,
                          command=lambda u=user: self.change_active_user(u))
            self.logged_users[user] = b
            b.pack()

    def send_message(self, event):
        text = self.text_input.get()
        if text:
            self.text_input.delete(0, tk.END)
            msg_gui = Message(self.frm_messages, text, True)
            self.client_api.send_message(text, self.active_user, self.my_login)
            self.add_message(text, msg_gui)

    def add_message(self, text, msg):
        if text and self.active_user:
            self.messages[self.active_user].append(msg)
            if len(self.messages[self.active_user]) > Message.MAX_MESSAGES:
                self.messages[self.active_user][0].destroy()
                self.messages[self.active_user].pop(0)

    def change_active_user(self, user):
        # todo this should clear message list and show messages memoized for 'active user'
        self.active_user = user
        if user not in self.messages:
            self.messages[user] = []

    def exit_program(self, event):
        self.client_api.close()
        self.window.destroy()

    def start(self, my_login, server_address, server_port):
        self.client_api.connect(server_address, server_port)
        self.client_api.send_login(my_login)
        self.my_login = my_login

        t = threading.Thread(target=self.thread_receive, daemon=True)
        t.start()

        self.client_api.send_get_users_list()
        self.window.mainloop()


    def receive(self, message, from_who):
        # todo again the same, rethink memoization
        if from_who not in self.messages:
            self.messages[from_who] = []
        self.add_message(message, Message(self.frm_messages, message, False))

    def thread_receive(self):
        while True:
            m = self.client_api.wait_for_message()
            if m[JsonFields.MESSAGE_TYPE] == MessageTypes.MESSAGE:
                self.receive(m[JsonFields.MESSAGE_VALUE], m[JsonFields.MESSAGE_SENDER])
            if m[JsonFields.MESSAGE_TYPE] == MessageTypes.USER_NAME_RESPONSE:
                print("login response: ", m)
            if m[JsonFields.MESSAGE_TYPE] == MessageTypes.ALL_USERS:
                users = m[JsonFields.MESSAGE_VALUE]
                self.refresh_logged(users)


if __name__ == '__main__':
    gui = Gui()
    if len(argv) > 1:
        gui.start("iron_man", argv[1], int(argv[2]))
    else:
        gui.start("iron_man", "localhost", 10000)
    # gui.start("iron_man", "192.168.1.10", 10000)
