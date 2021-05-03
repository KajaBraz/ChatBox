class JsonFields(object):
    MESSAGE_TYPE = "message_type"
    MESSAGE_VALUE = "message_value"
    MESSAGE_SENDER = "message_sender"
    MESSAGE_DESTINATION = "message_destination"
    MESSAGE_TIMESTAMP = "message_timestamp"


class MessageTypes(object):
    MESSAGE = "message"
    PREVIOUS_MESSAGES = "previous_messages"
    USERS_UPDATE = "users_update"
