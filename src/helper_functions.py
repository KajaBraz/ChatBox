import json
import logging
from datetime import datetime

from src.enums import JsonFields, MessageTypes
from src.my_json import from_json


def date_time_to_millis(t: datetime) -> int:
    return int(t.timestamp() * 1000)


def check_url(url_input: str) -> bool:
    range1 = range(48, 58)
    range2 = range(65, 91)
    range3 = range(97, 123)
    if url_input.count('/') != 2:
        return False
    updated_input = url_input.replace('/', '')
    for ch in updated_input:
        o = ord(ch)
        if (o not in range1) and (o not in range2) and (o not in range3):
            return False
    return True


def check_message_json(json_message: str) -> bool:
    dict_message = from_json(json_message)
    if (JsonFields.MESSAGE_TYPE in dict_message and
            JsonFields.MESSAGE_VALUE in dict_message and
            JsonFields.MESSAGE_SENDER in dict_message and
            JsonFields.MESSAGE_DESTINATION in dict_message):
        if (dict_message[JsonFields.MESSAGE_TYPE] == MessageTypes.MESSAGE and
                dict_message[JsonFields.MESSAGE_VALUE] != '' and
                dict_message[JsonFields.MESSAGE_SENDER] != '' and
                dict_message[JsonFields.MESSAGE_DESTINATION] != ''):
            return True
    return False


def check_previous_messages_json(json_message: str) -> bool:
    dict_message = from_json(json_message)
    if (JsonFields.MESSAGE_TYPE in dict_message and
            JsonFields.MESSAGE_DESTINATION in dict_message and
            JsonFields.MESSAGE_SENDER in dict_message):
        if (dict_message[JsonFields.MESSAGE_TYPE] == MessageTypes.PREVIOUS_MESSAGES and
                dict_message[JsonFields.MESSAGE_DESTINATION] != '' and
                dict_message[JsonFields.MESSAGE_SENDER] != ''):
            return True
    return False


def set_logger(logger_name, to_console=True):
    # TODO add to the configuration file to_console parameter
    #  (at the moment, it must be the same in every function call - database and server)
    formatter = '%(asctime)s ; %(levelname)s ; %(filename)s ; %(lineno)d. ; %(message)s'
    if to_console:
        logging.basicConfig(format=formatter, level=logging.INFO)
    else:
        logging.basicConfig(filename='logs.log', format=formatter, level=logging.INFO)
    return logging.getLogger(logger_name)


def read_config(filename: str) -> dict:
    with open(filename) as config_data:
        data = json.load(config_data)
        return data
