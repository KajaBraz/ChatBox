from src.enums import JsonFields, MessageTypes
from src.helper_functions import check_connection_url, check_message_json, check_previous_messages_json, check_input
from src.my_json import to_json


def test_check_url():
    correct_urls = ['/mychat/myloginqwertyuioplkjhgfdsaz', '/MyChat/MyLoginxcvbnm0987654321',
                    '/pokój/mylogin0olCnoRHyfTxvAh3TD0q', '/MyChat/MyLogin0olCnoRHyfTxvAh3TD09',
                    '/my_chat/my_login0olCnoRHyfTxvAh3TD0q']
    wrong_urls = ['/mychat/¯\\_(ツ)_/¯/0olCnoRHyfTxvAh3TD0q', '/chat_name/Login:)0olCnoRHyfTxvAh3TD0q',
                  '/chatname/MyLogin@0olCnoRHyfTxvAh3TD0q', '/chatname?/MyLogin0olCnoRHyfTxvAh3TD0q',
                  '/MyChat/my login0olCnoRHyfTxvAh3TD0q', '/my chat/my login0olCnoRHyfTxvAh3TD0q',
                  '/chat_name/MyLogin!0olCnoRHyfTxvAh3TD0q', 'mychat/mylogin0olCnoRHyfTxvAh3TD0q',
                  '/myChat/myLogin/0olCnoRHyfTxvAh3TD0q']
    assert all([check_connection_url(url) for url in correct_urls])
    assert not any([check_connection_url(url) for url in wrong_urls])


def test_check_message_json():
    message1 = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                JsonFields.MESSAGE_VALUE: 'this is a message',
                JsonFields.MESSAGE_DESTINATION: 'chat room',
                JsonFields.MESSAGE_SENDER: 'user name'
                }
    message2 = {JsonFields.MESSAGE_TYPE: 'MESSAGE',
                JsonFields.MESSAGE_VALUE: 'this is a message',
                JsonFields.MESSAGE_DESTINATION: 'chat room',
                JsonFields.MESSAGE_SENDER: 'user name'}
    message3 = {JsonFields.MESSAGE_TYPE: '',
                JsonFields.MESSAGE_VALUE: 'this is a message',
                JsonFields.MESSAGE_DESTINATION: 'chat room',
                JsonFields.MESSAGE_SENDER: 'user name'}
    message4 = {JsonFields.MESSAGE_VALUE: 'this is a message',
                JsonFields.MESSAGE_DESTINATION: 'chat room',
                JsonFields.MESSAGE_SENDER: 'user name'}
    message5 = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                JsonFields.MESSAGE_VALUE: '',
                JsonFields.MESSAGE_DESTINATION: 'chat room',
                JsonFields.MESSAGE_SENDER: 'user name'}
    message6 = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                JsonFields.MESSAGE_DESTINATION: 'chat room',
                JsonFields.MESSAGE_SENDER: 'user name'}
    message7 = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                JsonFields.MESSAGE_VALUE: 'this is a message',
                JsonFields.MESSAGE_DESTINATION: '',
                JsonFields.MESSAGE_SENDER: 'user name'}
    message8 = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                JsonFields.MESSAGE_VALUE: 'this is a message',
                JsonFields.MESSAGE_SENDER: 'user name'}
    message9 = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                JsonFields.MESSAGE_VALUE: 'this is a message',
                JsonFields.MESSAGE_DESTINATION: 'chat room',
                JsonFields.MESSAGE_SENDER: ''}
    message10 = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                 JsonFields.MESSAGE_VALUE: 'this is a message',
                 JsonFields.MESSAGE_DESTINATION: 'chat room'}
    message11 = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                 JsonFields.MESSAGE_VALUE: 'this is a message',
                 JsonFields.MESSAGE_DESTINATION: 'chat room',
                 JsonFields.MESSAGE_SENDER: 'user name',
                 'another field': 'some value'}
    message12 = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                 'MESSAGE_VALUE': 'this is a message',
                 JsonFields.MESSAGE_DESTINATION: 'chat room',
                 JsonFields.MESSAGE_SENDER: 'user name'}
    message13 = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                 JsonFields.MESSAGE_VALUE: 'this is a message',
                 'MESSAGE_DESTINATION': 'chat room',
                 JsonFields.MESSAGE_SENDER: 'user name'}
    message14 = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                 JsonFields.MESSAGE_VALUE: 'this is a message',
                 JsonFields.MESSAGE_DESTINATION: 'chat room',
                 'MESSAGE_SENDER': 'user name'}
    message15 = {'MESSAGE_TYPE': MessageTypes.MESSAGE,
                 JsonFields.MESSAGE_VALUE: 'this is a message',
                 JsonFields.MESSAGE_DESTINATION: 'chat room',
                 JsonFields.MESSAGE_SENDER: 'user name'}

    assert check_message_json(to_json(message1))
    assert check_message_json(to_json(message11))
    assert not check_message_json(to_json(message2))
    assert not check_message_json(to_json(message3))
    assert not check_message_json(to_json(message4))
    assert not check_message_json(to_json(message5))
    assert not check_message_json(to_json(message6))
    assert not check_message_json(to_json(message7))
    assert not check_message_json(to_json(message8))
    assert not check_message_json(to_json(message9))
    assert not check_message_json(to_json(message10))
    assert not check_message_json(to_json(message12))
    assert not check_message_json(to_json(message13))
    assert not check_message_json(to_json(message14))
    assert not check_message_json(to_json(message15))


def test_check_previous_messages_json():
    message1 = {JsonFields.MESSAGE_TYPE: MessageTypes.PREVIOUS_MESSAGES,
                JsonFields.MESSAGE_VALUE: -1,
                JsonFields.MESSAGE_SENDER: 'user name',
                JsonFields.MESSAGE_DESTINATION: 'chat name'}
    message2 = {JsonFields.MESSAGE_SENDER: 'user name',
                JsonFields.MESSAGE_DESTINATION: 'chat name'}
    message3 = {JsonFields.MESSAGE_TYPE: MessageTypes.PREVIOUS_MESSAGES,
                JsonFields.MESSAGE_DESTINATION: 'chat name'}
    message4 = {JsonFields.MESSAGE_TYPE: MessageTypes.PREVIOUS_MESSAGES,
                JsonFields.MESSAGE_SENDER: 'user name'}
    message5 = {JsonFields.MESSAGE_TYPE: MessageTypes.PREVIOUS_MESSAGES,
                JsonFields.MESSAGE_SENDER: '',
                JsonFields.MESSAGE_DESTINATION: 'chat name'}
    message6 = {JsonFields.MESSAGE_TYPE: MessageTypes.PREVIOUS_MESSAGES,
                JsonFields.MESSAGE_SENDER: 'user name',
                JsonFields.MESSAGE_DESTINATION: ''}
    message7 = {'MESSAGE_TYPE': MessageTypes.PREVIOUS_MESSAGES,
                JsonFields.MESSAGE_SENDER: 'user name',
                JsonFields.MESSAGE_DESTINATION: 'chat name'}
    message8 = {JsonFields.MESSAGE_TYPE: MessageTypes.MESSAGE,
                JsonFields.MESSAGE_SENDER: 'user name',
                JsonFields.MESSAGE_DESTINATION: 'chat name'}
    message9 = {JsonFields.MESSAGE_TYPE: '',
                JsonFields.MESSAGE_SENDER: 'user name',
                JsonFields.MESSAGE_DESTINATION: 'chat name'}
    message10 = {JsonFields.MESSAGE_TYPE: 'PREVIOUS_MESSAGES',
                 JsonFields.MESSAGE_SENDER: 'user name',
                 JsonFields.MESSAGE_DESTINATION: 'chat name'}
    message11 = {JsonFields.MESSAGE_TYPE: MessageTypes.PREVIOUS_MESSAGES,
                 'MESSAGE_SENDER': 'user name',
                 JsonFields.MESSAGE_DESTINATION: 'chat name'}
    message12 = {JsonFields.MESSAGE_TYPE: MessageTypes.PREVIOUS_MESSAGES,
                 JsonFields.MESSAGE_SENDER: 'user name',
                 'MESSAGE_DESTINATION': 'chat name'}
    message13 = {JsonFields.MESSAGE_TYPE: MessageTypes.PREVIOUS_MESSAGES,
                 JsonFields.MESSAGE_SENDER: 'user name',
                 JsonFields.MESSAGE_DESTINATION: 'chat name'}
    message14 = {JsonFields.MESSAGE_TYPE: MessageTypes.PREVIOUS_MESSAGES,
                 JsonFields.MESSAGE_VALUE: '10',
                 JsonFields.MESSAGE_SENDER: 'user name',
                 JsonFields.MESSAGE_DESTINATION: 'chat name'}
    message15 = {JsonFields.MESSAGE_TYPE: MessageTypes.PREVIOUS_MESSAGES,
                 JsonFields.MESSAGE_VALUE: '-1',
                 JsonFields.MESSAGE_SENDER: 'user name',
                 JsonFields.MESSAGE_DESTINATION: 'chat name'}
    assert check_previous_messages_json(to_json(message1))
    assert not check_previous_messages_json(to_json(message2))
    assert not check_previous_messages_json(to_json(message3))
    assert not check_previous_messages_json(to_json(message4))
    assert not check_previous_messages_json(to_json(message5))
    assert not check_previous_messages_json(to_json(message6))
    assert not check_previous_messages_json(to_json(message7))
    assert not check_previous_messages_json(to_json(message8))
    assert not check_previous_messages_json(to_json(message9))
    assert not check_previous_messages_json(to_json(message10))
    assert not check_previous_messages_json(to_json(message11))
    assert not check_previous_messages_json(to_json(message12))
    assert not check_previous_messages_json(to_json(message13))
    assert not check_previous_messages_json(to_json(message14))
    assert not check_previous_messages_json(to_json(message15))


def test_check_input():
    # GIVEN
    valid_inputs = ['davinci', 'DaVinci', 'da_vinci', 'Da-Vinci', 'davinci_15', '100', '2-1', '01234567890123456789',
                    'fofò', 'tribù', 'verità', 'lunedì', 'ventitré', 'ą', 'cç', 'dþ', 'nň', 'uŰ']
    invalid_inputs = ['', 'Da Vinci', 'da vinci', 'DaVinci.', 'da#vinci', 'da@vinci', 'da(vinci)', 'da&vinci',
                      'da_vinci!', 'da/vinci', 'davinci?', 'da[vinci]', 'da{vinci}', 'da|vinci', '-', '_', 'da+vinci',
                      'da*vinci', '"davinci"', "fofo'", "lunedi'", '#3', '5!', '1$', '2~3', '012345678901234567890']

    # WHEN
    check_valid = [check_input(valid) for valid in valid_inputs]
    check_invalid = [check_input(invalid) for invalid in invalid_inputs]

    # THEN
    assert all(check_valid)
    assert not any(check_invalid)
