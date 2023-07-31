class JsonFields(object):
    MESSAGE_TYPE = "message_type"
    MESSAGE_VALUE = "message_value"
    MESSAGE_SENDER = "message_sender"
    MESSAGE_DESTINATION = "message_destination"
    MESSAGE_TIMESTAMP = "message_timestamp"
    MULTIPLE_MESSAGES = "multiple_messages"


class MessageTypes(object):
    MESSAGE = "message"
    PREVIOUS_MESSAGES = "previous_messages"
    MORE_PREVIOUS_MESSAGES = "more_previous_messages"
    USERS_UPDATE = "users_update"


class Constants:
    DEFAULT_NO_DATABASE_MESSAGE_ID = -1
    DEFAULT_CHAT_NAME = 'WelcomeInChatBox'
