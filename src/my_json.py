import json

from src.enums import JsonFields


def from_json(arg: str) -> dict:
    try:
        return json.loads(arg)
    except json.decoder.JSONDecodeError:
        return {}


def to_json(arg: dict) -> str:
    return json.dumps(arg)


def is_proper_json(arg):
    if JsonFields.MESSAGE_TYPE in arg:
        return True
    return False
