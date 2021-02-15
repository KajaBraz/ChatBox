from sqlalchemy import *
from datetime import datetime


def my_database(name, action):
    """action - parameter that may be one of the following two strings: 'CREATE', 'DROP', or 'INSERT'"""

    # TODO connect to specific database and create the tables in it
    with create_engine('postgresql://postgres:000@localhost', isolation_level='AUTOCOMMIT').connect() as connection:
        if action in ['CREATE', 'DROP']:
            query = text(f'{action} DATABASE {name}')
            connection.execute(query)

            metadata = MetaData(bind=connection)

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
                                   # Column('date_time', DateTime),
                                   )
            metadata.create_all()

        if action == 'INSERT':

            query = connection.execute(text('SELECT * FROM users'))
            print(query.fetchall())
            print()
            data_users = (
            {'login': 'user1', 'encoded_password': '111', 'salt': 'aaa', 'registration_date': datetime(2020, 4, 15)},
            {'login': 'user2', 'encoded_password': '222', 'salt': 'bbb', 'registration_date': datetime(2020, 4, 15)},
            {'login': 'user3', 'encoded_password': '333', 'salt': 'ccc', 'registration_date': datetime(2020, 4, 15)},
            {'login': 'user4', 'encoded_password': '444', 'salt': 'ddd', 'registration_date': datetime(2020, 4, 15)},
            )
            data_messages = ({'sender_id': 1, 'recipient': 'user2', 'message': 'hello user1 here'},
                             {'sender_id': 4, 'recipient': 'user3', 'message': 'hello user4 here'})

            for line in data_users:
                connection.execute(text(
                    f'{action} INTO users(login, encoded_password, salt, registration_date) VALUES(:login, :encoded_password, :salt, :registration_date)'),
                                   **line)
            for line in data_messages:
                connection.execute(text(
                    f'{action} INTO messages(sender_id, recipient, message) VALUES(:sender_id, :recipient, :message)'),
                                   **line)


def create_my_database(db_name):
    my_database(db_name, 'CREATE')


def drop_my_database(db_name):
    my_database(db_name, 'DROP')


def fill_with_examples(db_name):
    my_database(db_name, 'INSERT')


if __name__ == '__main__':
    pass
    # create_my_database('chatbox_test_1')
    # drop_my_database('chatbox_test_1')
    # fill_with_examples('chatbox_test_1')
