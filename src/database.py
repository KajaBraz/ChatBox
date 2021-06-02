import json
import logging
import random
from datetime import datetime

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, text, select

from src import helper_functions

data = helper_functions.read_config('../chatbox_config.json')
db_login = data['database']['db_login']
db_password = data['database']['db_password']
db_name = data['database']['db_name']
log = helper_functions.set_logger(data['logs']['log_file_name'], data['logs']['to_console'])


def create_my_database(login, password):
    with create_engine(f'postgresql://{login}:{password}@localhost',
                       isolation_level='AUTOCOMMIT').connect() as connection:
        query = text(f'CREATE DATABASE {db_name}')
        connection.execute(query)

    with create_engine(f'postgresql://{login}:{password}@localhost/{db_name}',
                       isolation_level='AUTOCOMMIT').connect() as connection:
        metadata = MetaData(bind=connection)

        Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('login', String(40)),
              Column('encoded_password', String),
              Column('salt', String(3)),
              Column('registration_date', DateTime),
              )

        Table('messages', metadata,
              Column('id', Integer, primary_key=True),
              # Column('sender_id', None, ForeignKey('users.id')),
              Column('sender_login', String),
              Column('chat_name', String),
              Column('message', String),
              Column('date_time', DateTime),
              )

        metadata.create_all()


def connect(db: str, login: str, password: str) -> sqlalchemy.engine.Engine:
    try:
        return create_engine(f'postgresql://{login}:{password}@localhost/{db}').connect()
    except Exception as e:
        log.exception(f'Database connection error: {e}')


def drop_my_database(db, login, password):
    with create_engine(f'postgresql://{login}:{password}@localhost',
                       isolation_level='AUTOCOMMIT').connect() as connection:
        query = text(f'DROP DATABASE {db}')
        connection.execute(query)


def fill_with_examples(db_connection):
    users = [
        ("anna_magnani", "roma_citta_aperta"),
        ("luciano_pavarotti", "nessun_dorma"),
        ("giordano_bruno", "campo_de'_fiori"),
        ("giulietta_masina", "la_strada"),
        ("toto'", "napule_non_si_scorda_mai"),
        ("sophia_loren", "la_ciociara"),
        ("al_bano", "felicità"),
        ("maria_montessori", "motivazione"),
        ("federico_fellini", "la_dolce_vita"),
        ("vittorio_de_sica", "ladri_di_biciclette"),
        ("gianluigi_buffon", "juventus_campioni"),
        ("alessandro_volta", "scossa_elettrica")
    ]

    for user in users:
        user_name = user[0]
        user_pass = user[1]
        add_user(user_name, user_pass, db_connection)


def add_user(new_login, new_password, connection):
    chrs_ranges = list(range(48, 58)) + list(range(65, 91)) + list(range(97, 123))
    new_salt = ''.join([chr(random.choice(chrs_ranges)) for i in range(3)])

    metadata = MetaData()
    metadata.reflect(bind=connection)
    users_table = metadata.tables['users']
    stm = users_table.insert().values(login=new_login, encoded_password=hash(new_password + new_salt),
                                      salt=new_salt, registration_date=datetime.now())
    connection.execute(stm)


def add_message(login, chat, message, db_connection, date_time):
    if db_connection:
        metadata = MetaData()
        metadata.reflect(bind=db_connection)
        messages = metadata.tables['messages']
        stm = messages.insert().values(sender_login=login, chat_name=chat, message=message, date_time=date_time)
        db_connection.execute(stm)
        log.debug(f'adding message "{message}" to the database, sent by {login} in chat {chat}')
    else:
        log.error('cannot add message to database')


def show_entries(table_name, db_connection, with_pandas=True):
    metadata = MetaData()
    metadata.reflect(bind=db_connection)
    table = metadata.tables[table_name]
    stm = table.select()
    entries = db_connection.execute(stm)
    if with_pandas:
        df = pd.DataFrame(entries)
        pd.set_option('max_columns', None)
        print(df)
    else:
        for entry in entries:
            print(entry)


def get_historic_messages(start_period: str, end_period: str, str_to_search: str, conn):
    """
    :param start_period: '%d/%m/%y' ex. '01/03/21 00:00:00'
    :param end_period: '%d/%m/%y' ex. '01/03/21 23:59:59'
    :param str_to_search: substring that must be present in messages
    :param conn:
    :return:
    """
    metadata = MetaData()
    metadata.reflect(bind=conn)
    message_table = metadata.tables['messages']
    date_from = datetime.strptime(start_period, '%d/%m/%y %H:%M:%S')
    date_to = datetime.strptime(end_period, '%d/%m/%y %H:%M:%S')
    entries = conn.execute(message_table.select().where(message_table.c.date_time >= date_from).where(
        message_table.c.date_time <= date_to).where(message_table.c.message.contains(str_to_search)))
    return entries.fetchall()


def fetch_last_messages(chat_name, conn, n=100):
    metadata = MetaData()
    metadata.reflect(bind=conn)
    message_table = metadata.tables['messages']
    cls_to_select = [message_table.c.sender_login, message_table.c.message, message_table.c.chat_name,
                     message_table.c.date_time]
    inner_query = (select([message_table.c.id])
                   .where(message_table.c.chat_name == chat_name)
                   .order_by(message_table.c.id.desc())
                   .limit(n)
                   .alias('inner_query'))
    n_entries = conn.execute(select(cls_to_select)
                             .where(message_table.c.id == inner_query.c.id))
    return n_entries.fetchall()


def print_df(data_list, column_names):
    df = pd.DataFrame(data_list, columns=column_names)
    pd.set_option('max_columns', None)
    print(df)


if __name__ == '__main__':
    # create_my_database(db_login, db_password)
    # drop_my_database(db_name, db_login, db_password)
    # conn = connect(db_name, db_login, db_password)
    # print(fetch_last_messages('zwierzaki', conn, 10))
    # fill_with_examples(conn)
    # add_user('anna_magnani', 'roma_citta_aperta', conn)
    # add_message('giordano_bruno', 'sapienza', "il sapere e' il potere", conn)
    # show_entries('users', conn)
    # show_entries('messages', conn)
    # mess = get_historic_messages('07/03/21 00:00:00','08/03/21 23:59:59', 'bolo', conn)
    # print(mess)
    # past_mess = fetch_last_messages('zwierzogrod', conn)
    # print_df(past_mess, ['login','message','chat','data_time'])
    pass
