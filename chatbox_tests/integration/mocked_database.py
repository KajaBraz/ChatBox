class MockedDatabase:
    def __init__(self):
        self.messages_added = 0
        self.messages = []

    def add_message(self, login, chat_name, message, date_time):
        self.messages_added += 1
        self.messages.append(message)
