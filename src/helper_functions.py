import json
import logging
import random
import re
import string
from datetime import datetime

from src.enums import JsonFields, MessageTypes
from src.my_json import from_json


def date_time_to_millis(t: datetime) -> int:
    return int(t.timestamp() * 1000)


def check_url(url_input: str) -> bool:
    if url_input[0] != '/' or url_input.count('/', 1) != 1:
        return False
    used_chrs = set(url_input)
    used_chrs.remove('/')
    for char in used_chrs:
        if not (char.isalnum() or char in {'-', '_'}):
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
            JsonFields.MESSAGE_VALUE in dict_message and
            JsonFields.MESSAGE_SENDER in dict_message):
        if (dict_message[JsonFields.MESSAGE_TYPE] == MessageTypes.PREVIOUS_MESSAGES and
                dict_message[JsonFields.MESSAGE_VALUE] == -1 and
                dict_message[JsonFields.MESSAGE_DESTINATION] != '' and
                dict_message[JsonFields.MESSAGE_SENDER] != ''):
            return True
    return False


def check_more_previous_messages_json(json_message: str) -> bool:
    dict_message = from_json(json_message)
    if (JsonFields.MESSAGE_TYPE in dict_message and
            JsonFields.MESSAGE_VALUE in dict_message and
            JsonFields.MESSAGE_DESTINATION in dict_message and
            JsonFields.MESSAGE_SENDER in dict_message):
        if (dict_message[JsonFields.MESSAGE_TYPE] == MessageTypes.MORE_PREVIOUS_MESSAGES and
                dict_message[JsonFields.MESSAGE_VALUE] != '' and
                dict_message[JsonFields.MESSAGE_VALUE] != -1 and
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


def detect_hyperlink(text: str):
    # link_pattern = r'www\.\S+\.[a-z]{2,3}(\/\S*)?'
    # link_pattern = r'www\.\S+\.[a-z]{2,3}\S*'
    link_pattern = r'www\.\S+\.[a-z]{2,4}\S*|https?://\S+'
    links = re.findall(link_pattern, text)
    updated_text = text
    for link in set(links):
        if link != '':
            if 'http' in link:
                replace_link = f'<a href="{link}">{link}</a>'
                print(replace_link)
            else:
                replace_link = f'<a href="https://{link}">{link}</a>'
            updated_text = re.sub(re.escape(link), replace_link, updated_text)
    return updated_text


def generate_random_string(n: int):
    return ''.join(random.sample(string.ascii_letters, n))
