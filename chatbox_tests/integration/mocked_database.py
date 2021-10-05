from src import helper_functions, message
from src.enums import Constants


class MockedDatabase:
    def __init__(self):
        self.messages = []
        self.fetched_messages = None

    def add_message(self, login, chat_name, msg, date_time):
        self.messages.append(msg)
        return message.Message(Constants.DEFAULT_NO_DATABASE_MESSAGE_ID, login, msg, chat_name,
                               helper_functions.date_time_to_millis(date_time))

    def set_return_value(self, method, return_value):
        if method == 'fetch_last_messages':
            self.fetched_messages = return_value

    def fetch_last_messages(self, _chat_name):
        return self.fetched_messages
