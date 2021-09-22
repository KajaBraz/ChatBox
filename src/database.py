import pprint
import random
from datetime import datetime

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, MetaData, select

from src import helper_functions


class ChatBoxDatabase:
    def __init__(self, config_data: dict):
        self.db_login = config_data['database']['db_login']
        self.db_password = config_data['database']['db_password']
        self.db_name = config_data['database']['db_name']
        self.connection = self.connect()
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.connection)
        self.log = helper_functions.set_logger(config_data['logs']['log_file_name'], config_data['logs']['to_console'])

    def connect(self) -> sqlalchemy.engine.Engine:
        try:
            return create_engine(f'postgresql://{self.db_login}:{self.db_password}@localhost/{self.db_name}').connect()
        except Exception as e:
            self.log.exception(f'Database connection error: {e}')
            return None

    def add_user(self, new_login, new_password):
        chrs_ranges = list(range(48, 58)) + list(range(65, 91)) + list(range(97, 123))
        new_salt = ''.join([chr(random.choice(chrs_ranges)) for i in range(3)])

        users_table = self.metadata.tables['users']
        stm = users_table.insert().values(login=new_login, encoded_password=hash(new_password + new_salt),
                                          salt=new_salt, registration_date=datetime.now())
        self.connection.execute(stm)

    def add_message(self, login, chat, message, date_time):
        if self.connection:
            messages = self.metadata.tables['messages']
            stm = messages.insert().values(sender_login=login, chat_name=chat, message=message, date_time=date_time)
            self.connection.execute(stm)
            self.log.debug(f'adding message "{message}" to the database, sent by {login} in chat {chat}')
        else:
            self.log.error('cannot add message to database')

    def show_entries(self, table_name, with_pandas=True):
        table = self.metadata.tables[table_name]
        stm = table.select()
        entries = self.connection.execute(stm)
        if with_pandas:
            df = pd.DataFrame(entries)
            pd.set_option('max_columns', None)
            print(df)
        else:
            for entry in entries:
                print(entry)

    def get_historic_messages(self, start_period: str, end_period: str, str_to_search: str):
        """
        :param start_period: '%d/%m/%y' ex. '01/03/21 00:00:00'
        :param end_period: '%d/%m/%y' ex. '01/03/21 23:59:59'
        :param str_to_search: substring that must be present in messages
        :return:
        """
        message_table = self.metadata.tables['messages']
        date_from = datetime.strptime(start_period, '%d/%m/%y %H:%M:%S')
        date_to = datetime.strptime(end_period, '%d/%m/%y %H:%M:%S')
        entries = self.connection.execute(message_table.select().where(message_table.c.date_time >= date_from).where(
            message_table.c.date_time <= date_to).where(message_table.c.message.contains(str_to_search)))
        return entries.fetchall()

    def fetch_last_messages(self, chat_name, n=100):
        message_table = self.metadata.tables['messages']
        inner_query = (select([message_table])
                       .where(message_table.c.chat_name == chat_name)
                       .order_by(message_table.c.id.desc())
                       .limit(n)
                       .alias('inner_query'))
        n_entries = self.connection.execute(select([inner_query]).order_by(inner_query.c.id))
        return n_entries.fetchall()

    def print_df(self, data_list, column_names):
        df = pd.DataFrame(data_list, columns=column_names)
        pd.set_option('max_columns', None)
        print(df)


if __name__ == '__main__':
    data = helper_functions.read_config('../chatbox_config.json')
    chatbox_database = ChatBoxDatabase(data)
    chatbox_database.show_entries('users')
    chatbox_database.show_entries('messages')
    chatbox_database.add_user('anna_magnani', 'roma_citta_aperta')
    chatbox_database.add_message('giordano_bruno', 'sapienza', 'il sapere e\' il potere', datetime.now())
    mess = chatbox_database.get_historic_messages('07/03/21 00:00:00', '08/06/21 23:59:59', 'ciao')
    pprint.pprint(mess)
    pprint.pprint(chatbox_database.fetch_last_messages('zwierzaki', 10))
    past_mess = chatbox_database.fetch_last_messages('zwierzogrod')
    chatbox_database.print_df(past_mess, ['login', 'message', 'chat', 'data_time'])
    pass
