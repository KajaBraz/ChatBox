import tkinter as tk


class Gui(tk.Frame):
    def __init__(self):
        self.window = tk.Tk()
        super().__init__(self.window)
        self.v = 0
        self.window.bind("<Return>", self.enter_action)
        self.window.bind("<KeyPress-Escape>", self.exit_program)
        self.label = tk.Label(text="my label", width=10, height=10, bg="red", fg="yellow")
        self.label.pack()
        self.button = tk.Button(text="button", bg="blue", fg="red", command=self.button_command)
        self.button.pack()

        # why width, height dont work in this situation?
        # self.frm_users = tk.Frame(master=self.window, borderwidth=5, relief='ridge', width=1000, height=600)
        self.frm_users = tk.Frame(borderwidth=5, relief='ridge')
        self.btn_refresh = tk.Button(text='refresh', master=self.frm_users)
        print(str(self.btn_refresh.keys()))
        print(str(self.frm_users.keys()))
        self.btn_refresh.pack()
        self.users = self.create_users()
        self.frm_users.pack()
        f1 = tk.Frame(width=300, height=300, bg="#332211")
        f1.pack(side=tk.LEFT)
        f2 = tk.Frame(width=100, height=100, bg="#112233")
        f2.pack()
        f3 = tk.Frame(width=50, height=50, bg="#221133")
        f3.pack()

    def create_users(self):
        users = ['user1', 'user2', 'tony_stark', 'iron man']
        d = {}
        for user in users:
            b = tk.Button(text=user, master=self.frm_users, borderwidth=0)
            d[user] = b
            b.pack()
        return d

    def button_command(self):
        self.v = self.v + 1
        self.label['text'] = self.v

    def enter_action(self, event):
        self.v = self.v + 2
        self.label['text'] = self.v

    def exit_program(self, event):
        self.window.destroy()

    def start(self):
        self.window.mainloop()


if __name__ == '__main__':
    gui = Gui()
    gui.start()
