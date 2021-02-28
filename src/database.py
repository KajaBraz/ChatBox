from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, text
from datetime import datetime
import random
import pandas as pd


db_login = "postgres"
db_password = 000
db_name = 'chatbox2'


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


def connect(db, login, password):
    return create_engine(f'postgresql://{login}:{password}@localhost/{db}').connect()


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

    metedata = MetaData(bind=connection, reflect=True)
    users_table = metedata.tables['users']
    stm = users_table.insert().values(login=new_login, encoded_password=hash(new_password + new_salt),
                                      salt=new_salt, registration_date=datetime.now())
    connection.execute(stm)


def add_message(login, chat, message, db_connection):
    metadata = MetaData(bind=db_connection, reflect=True)
    messages = metadata.tables['messages']
    stm = messages.insert().values(sender_login=login, chat_name=chat, message=message, date_time=datetime.now())
    db_connection.execute(stm)


def show_entries(table_name, db_connection, with_pandas=True):
    metadata = MetaData(bind=db_connection, reflect=True)
    table = metadata.tables[table_name]
    stm = table.select()
    entries = db_connection.execute(stm)
    if with_pandas == True:
        df = pd.DataFrame(entries)
        print(df)
    else:
        for entry in entries:
            print(entry)


if __name__ == '__main__':
    # create_my_database(db_login, db_password)
    # drop_my_database(db_name, db_login, db_password)
    # conn = connect(db_name, db_login, db_password)
    # fill_with_examples(conn)
    # add_user('anna_magnani', 'roma_citta_aperta', conn)
    # add_message('giordano_bruno', 'sapienza', "il sapere e' il potere", conn)
    # show_entries('users', conn)
    pass
