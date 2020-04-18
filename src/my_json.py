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
    if "message_type" and "message_value" and "message_receiver" in arg:
        return True
    return False