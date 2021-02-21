class JsonFields(object):
    MESSAGE_TYPE = "message_type"
    MESSAGE_VALUE = "message_value"
    MESSAGE_RECEIVER = "message_receiver" # to drop; changed to receiver chat name
    MESSAGE_SENDER = "message_sender"
    MESSAGE_DESTINATION = "message_destination"


class MessageTypes(object):
    MESSAGE = "message"
    USER_LOGIN = "user_login"
    ALL_USERS = "all_users"
    USER_NAME_RESPONSE = "user_name_response"
    LOGIN_ACCEPTED = "login_accepted"
    LOGIN_ALREADY_USED = "login_already_used"
