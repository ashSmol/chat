import os

from sqlalchemy import create_engine

DEFAULT_HOST_ADDR = '127.0.0.1'

DEFAULT_HOST_PORT = 7777
if os.name == 'posix':
    DB_ENGINE_PATH = 'sqlite:////Users/aleksejsiraev/PycharmProjects/chat/db.sqlite'
    CLIENT_DB_ENGINE_PATH = 'sqlite:////Users/aleksejsiraev/PycharmProjects/chat/client_db.sqlite'
else:
    DB_ENGINE_PATH = 'sqlite:////db.sqlite'
    CLIENT_DB_ENGINE_PATH = 'sqlite:////client_db.sqlite'
DB_ENGINE = create_engine(DB_ENGINE_PATH, echo=True)
CLIENT_DB_ENGINE = create_engine(CLIENT_DB_ENGINE_PATH, echo=True)
ENCODING = 'utf-8'

MAX_CONNECTIONS = 5

MAX_PACKAGE_LENGTH = 1024

ACTION = 'action'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
GET_CONTACTS = 'get_contacts'
DEL_CONTACT = 'del_contact'
CLIENTS_LOGINS = 'clients_logins'
ADD_CONTACT = 'add_contact'
DEL_CONTACT = 'del_contact'
CONTACT_NAME = 'contact_name'
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
