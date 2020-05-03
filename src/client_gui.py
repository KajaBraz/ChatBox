import tkinter as tk

# class Gui(tk.Frame):
#     def __init__(self):
#         self.window =

v = 0
label = None


def button_command():
    global v
    v = v + 1
    label['text'] = v


def enter_action(event):
    global v
    v = v + 2
    label['text'] = v


if __name__ == '__main__':
    window = tk.Tk()
    window.bind("<Return>", enter_action)
    label = tk.Label(text="my label", width=10, height=10, bg="red", fg="yellow")
    label.pack()
    button = tk.Button(text="button", bg="blue", fg="red", command=button_command)
    button.pack()
    window.mainloop()
