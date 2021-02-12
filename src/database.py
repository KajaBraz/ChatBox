from sqlalchemy import *


def my_database(name, action):
    """action - parameter that may be one of the following two strings: 'CREATE' or 'DROP'"""

    with create_engine('postgresql://postgres:1861@localhost', isolation_level='AUTOCOMMIT').connect() as connection:
        query = text(f'{action} DATABASE {name}')
        connection.execute(query)

        metadata = MetaData(bind=connection)

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
                               Column('date/time', DateTime),
                               )
        metadata.create_all()


def create_my_database(db_name):
    my_database(db_name, 'CREATE')


def drop_my_database(db_name):
    my_database(db_name, 'DROP')


if __name__ == '__main__':
# create_my_database('chatbox_test_1')
# drop_my_database('chatbox_test_4')
