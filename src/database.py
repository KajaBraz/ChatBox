from sqlalchemy import *
from datetime import datetime


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


if __name__ == '__main__':
    login = "postgres"
    password = "000"
    # drop_my_database('chatbox_test_12', login, password)
    # create_my_database('chatbox_test_12', login, password)
    # fill_with_examples('chatbox_test_12', login, password)
    pass
