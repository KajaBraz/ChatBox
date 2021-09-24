import dataclasses


@dataclasses.dataclass
class Message:
    id: int
    sender_login: str
    message: str
    chat_name: str
    timestamp: int
