from collections import defaultdict

from src import helper_functions, message


class MockedDatabase:
    def __init__(self):
        self.messages = defaultdict(list)
        self.fetched_messages = None

    def add_message(self, login, chat_name, msg, date_time):
        print('adding', msg)
        msg_obj = message.Message(len(self.messages[chat_name]), login, msg, chat_name,
                                  helper_functions.date_time_to_millis(date_time))
        self.messages[chat_name].append(msg_obj)
        return msg_obj

    def set_return_value(self, method, return_value):
        if method == 'fetch_last_messages':
            self.fetched_messages = return_value

    def fetch_last_messages(self, chat_name, n=10, start_from_id=-1):
        # todo always simulate database, don't return previously set values
        if self.fetched_messages:
            return self.fetched_messages
        start_from_id = int(start_from_id)
        if start_from_id == -1:
            return self.messages[chat_name][len(self.messages[chat_name]) - n:]
        from_id = start_from_id - n
        to_id = start_from_id
        return self.messages[chat_name][from_id:to_id]
