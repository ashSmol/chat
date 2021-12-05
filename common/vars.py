from sqlalchemy import create_engine

DEFAULT_HOST_ADDR = '127.0.0.1'

DEFAULT_HOST_PORT = 7777
DB_ENGINE = create_engine('sqlite:///db.sqlite', echo=True)
ENCODING = 'utf-8'

MAX_CONNECTIONS = 5

MAX_PACKAGE_LENGTH = 1024

ACTION = 'action'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
TIME = 'time'
USER_ACCOUNT = 'user_account'
ACCOUNT_NAME = 'acc_name'
SENDER = 'sender'
RECEIVER = 'receiver'
DEFAULT_CLIENT_TYPE = RECEIVER

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'

CLIENT_TYPES = [SENDER, RECEIVER]
