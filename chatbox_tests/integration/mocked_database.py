class MockedDatabase:
    def __init__(self):
        self.messages = []
        self.fetched_messages = None

    def add_message(self, _login, _chat_name, message, _date_time):
        self.messages.append(message)

    def set_return_value(self, method, return_value):
        if method == 'fetch_last_messages':
            self.fetched_messages = return_value

    def fetch_last_messages(self, _chat_name):
        return self.fetched_messages
