import json


def from_json(arg: bytes) -> dict:
    try:
        decoded = arg.decode("utf-8")
        return json.loads(decoded)
    except json.decoder.JSONDecodeError:
        return {}


def to_json(arg: dict) -> bytes:
    pack = json.dumps(arg)
    return pack.encode("utf-8")


def is_proper_json(arg):
    if "message_type" in arg:
        return True
    return False
