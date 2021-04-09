class JsonFields(object):
    MESSAGE_TYPE = "message_type"
    MESSAGE_VALUE = "message_value"
    MESSAGE_SENDER = "message_sender"
    MESSAGE_DESTINATION = "message_destination"


class MessageTypes(object):
    MESSAGE = "message"
    ALL_USERS = "all_users"
    USER_NAME_RESPONSE = "user_name_response"
    LOGIN_ACCEPTED = "login_accepted"
    LOGIN_ALREADY_USED = "login_already_used"
    PREVIOUS_MESSAGES = "previous_messages"
