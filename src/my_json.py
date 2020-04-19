import json


def from_json(arg):
    try:
        unpack = json.loads(arg)
        return unpack
    except json.decoder.JSONDecodeError:
        return {}


def to_json(arg):
    return json.dumps(arg)


def is_proper_json(arg):
    if "message_type" in arg:
        return True
    return False
