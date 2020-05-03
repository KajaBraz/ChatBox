import tkinter as tk


class Gui(tk.Frame):
    def __init__(self):
        self.window = tk.Tk()
        super().__init__(self.window)
        self.v = 0
        self.window.bind("<Return>", self.enter_action)
        self.label = tk.Label(text="my label", width=10, height=10, bg="red", fg="yellow")
        self.label.pack()
        self.button = tk.Button(text="button", bg="blue", fg="red", command=self.button_command)
        self.button.pack()

    def button_command(self):
        self.v = self.v + 1
        self.label['text'] = self.v

    def enter_action(self, event):
        self.v = self.v + 2
        self.label['text'] = self.v

    def start(self):
        self.window.mainloop()


if __name__ == '__main__':
    gui = Gui()
    gui.start()
