from sqlalchemy import *
from datetime import datetime
import random


def create_my_database(db_name, login, password):
    action = 'CREATE'
    with create_engine(f'postgresql://{login}:{password}@localhost',
                       isolation_level='AUTOCOMMIT').connect() as connection:
        if action in ['CREATE', 'DROP']:
            query = text(f'{action} DATABASE {db_name}')
            connection.execute(query)
    with create_engine(f'postgresql://{login}:{password}@localhost/{db_name}',
                       isolation_level='AUTOCOMMIT').connect() as connection:
        metadata = MetaData(bind=connection)

        # RAW SQL QUERIES
        # connection.execute(text("""
        # CREATE TABLE users(
        # id INTEGER PRIMARY KEY,
        # login TEXT,
        # encoded_password TEXT,
        # salt TEXT
        # )"""))

        users_table = Table('users', metadata,
                            Column('id', Integer, primary_key=True),
                            Column('login', String(40)),
                            Column('encoded_password', String),
                            Column('salt', String(3)),
                            Column('registration_date', DateTime),
                            )

        messages_table = Table('messages', metadata,
                               Column('id', Integer, primary_key=True),
                               Column('sender_id', None, ForeignKey('users.id')),
                               Column('recipient', String),
                               Column('message', String),
                               Column('date_time', DateTime),
                               )
        metadata.create_all()


def drop_my_database(db_name, login, password):
    action = 'DROP'
    with create_engine(f'postgresql://{login}:{password}@localhost',
                       isolation_level='AUTOCOMMIT').connect() as connection:
        if action in ['CREATE', 'DROP']:
            query = text(f'{action} DATABASE {db_name}')
            connection.execute(query)


def fill_with_examples(db_name, login, password):
    action = 'INSERT'
    with create_engine(f'postgresql://{login}:{password}@localhost/{db_name}',
                       isolation_level='AUTOCOMMIT').connect() as connection:
        data_users = (
            {'login': 'user1', 'encoded_password': '111', 'salt': 'aaa',
             'registration_date': datetime.now()},
            {'login': 'user2', 'encoded_password': '222', 'salt': 'bbb',
             'registration_date': datetime.now()},
            {'login': 'user3', 'encoded_password': '333', 'salt': 'ccc',
             'registration_date': datetime.now()},
            {'login': 'user4', 'encoded_password': '444', 'salt': 'ddd',
             'registration_date': datetime.now()},
        )
        data_messages = (
            {'sender_id': 1, 'recipient': 'user2', 'message': 'hello user1 here', 'date_time': datetime.now()},
            {'sender_id': 4, 'recipient': 'user3', 'message': 'hello user4 here', 'date_time': datetime.now()})

        for line in data_users:
            connection.execute(text(
                f'{action} INTO users(login, encoded_password, salt, registration_date) VALUES(:login,'
                f':encoded_password, :salt, :registration_date)'),
                **line)
        for line in data_messages:
            connection.execute(text(
                f'{action} INTO messages(sender_id, recipient, message, date_time) VALUES(:sender_id, :recipient,'
                f':message, :date_time)'),
                **line)


def add_user(db,table_name, username, my_password, new_login, new_password):
    chrs_ranges = list(range(48,58))+list(range(65,91))+list(range(97,123))
    new_salt = ''.join([chr(random.choice(chrs_ranges)) for i in range(3)])
    reg_date = datetime.now()
    # new_user = {'login': login, 'encoded_password': password, 'salt':chr(random.choices(chrs_ranges, 3)),
    #      'registration_date': datetime.now()}

    with create_engine(f'postgresql://{username}:{my_password}@localhost/{db}', isolation_level='AUTOCOMMIT').connect() as connection:
        # stm = f'INSERT INTO users(login, encoded_password, salt, registration_date) VALUES ({new_login}, {new_password}, {new_salt}, {reg_date})'

        stm = table_name.insert().values(login=new_login, encoded_password=new_password, salt=new_salt,
                                          registration_date=datetime.now())
        connection.execute(stm)


if __name__ == '__main__':
    login = "postgres"
    password = 1861
    # drop_my_database('chatbox_test_12', login, password)
    users, messages = create_my_database('chatbox_test_17', login, password)
    # fill_with_examples('chatbox_test_12', login, password)
    add_user('chatbox_test_16',Table('users'), login,password,'new_user','new_password')
    pass
