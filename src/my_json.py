import json

from src.enums import JsonFields


def from_json(arg: bytes) -> dict:
    try:
        decoded = arg.decode("utf-8") if type(arg)==bytes else arg
        return json.loads(decoded)
    except json.decoder.JSONDecodeError:
        return {}


def to_json(arg: dict) -> bytes:
    pack = json.dumps(arg)
    return pack.encode("utf-8")


def is_proper_json(arg):
    if JsonFields.MESSAGE_TYPE in arg:
        return True
    return False


def join_json_len(j: bytes) -> bytes:
    j_len = len(j)
    j_len_b = j_len.to_bytes(2, 'big')
    return j_len_b + j


def count_jsons(j: bytes) -> list:
    j_list = []
    j_copy = j[:]
    while j_copy:
        j_len = int.from_bytes(j_copy[:2], 'big')
        single_j = j_copy[2:j_len + 2]
        j_list.append(single_j)
        j_copy = j_copy[j_len + 2:]
    return j_list
