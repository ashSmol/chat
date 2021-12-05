import dis
import logging
import select
import socket
import time
from socket import *

from sqlalchemy.orm import sessionmaker

from common.utils import read_message_from_sock, write_message_to_sock, get_socket_params
from common.vars import *
from logs.system_logger import SystemLogger
from model import ChatClientModel


class NonNegative:
    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if value < 0:
            raise ValueError('Cannot be negative.')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class ServerVerifierMeta(type):
    def __init__(cls, clsname, bases, clsdict):
        for attr in clsdict:
            value = clsdict[attr]
            if callable(value):
                clsdict[attr] = SystemLogger()
        type.__init__(cls, clsname, bases, clsdict)

    def __new__(self, clsname, bases, clsdict):
        is_tcp_connection = False
        for key, value in clsdict.items():
            if isinstance(value, socket):
                raise ValueError
            if callable(value):
                dis_str = dis.code_info(value)
                if (dis_str.find('socket') > 0) & (dis_str.find('connect') > 0):
                    raise Exception('"Accept" operation is not allowed for ChatClient')
                if (dis_str.find('socket') > 0) & (dis_str.find('AF_INET') > 0):
                    is_tcp_connection = True
        if not is_tcp_connection:
            raise ConnectionError('Connection type shoud be TCP!!!')
        return type.__new__(self, clsname, bases, clsdict)


class ChatServer(metaclass=ServerVerifierMeta):
    # @SystemLogger()
    port = NonNegative()

    def __init__(self):
        self.contacts = dict()
        self.messages_to_send = []
        self.all_clients = []
        self.read_queue = []
        self.write_queue = []
        self.received_messages = []
        self.logger = logging.getLogger('app.server')
        self.logger.info('created server object')
        self.sock = None
        Session = sessionmaker(bind=DB_ENGINE)
        self.db_session = Session()

    def collect_all_messages(self):
        if len(self.read_queue) > 0:
            for client in self.read_queue:
                try:
                    message = read_message_from_sock(client)
                    self.contacts.update({message.get(ACCOUNT_NAME): client})
                    self.received_messages.append(message)
                except:
                    if client:
                        self.logger.info(f'Клиент {client.getpeername()} отключился.')
                        self.all_clients.remove(client)
                        self.read_queue.remove(client)

    def start_listen(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        addr, self.port, _ = get_socket_params()
        self.sock.bind((addr, self.port))
        self.sock.settimeout(0.5)
        self.logger.info(f'socket bind to addr {addr}:{self.port}')
        while True:
            self.sock.listen(MAX_CONNECTIONS)
            try:
                client, client_addr = self.sock.accept()
                self.logger.info(f'новое соединение с клиентом {client_addr}. Добавляем в общий список')
                self.all_clients.append(client)
            except OSError:
                pass

            if self.all_clients:
                self.read_queue, self.write_queue, error_queue = select.select(self.all_clients, self.all_clients,
                                                                               [])
            self.collect_all_messages()
            self.build_responses()
            self.send_all()

    def store_clients_to_db(self, login: str, info: str):
        try:
            self.db_session.add(ChatClientModel(login, info))
        except Exception as err:
            print(err)
            self.db_session.rollback()
        else:
            self.db_session.commit()

    def build_responses(self):
        if self.received_messages:  # and self.write_queue:
            for message in self.received_messages:
                self.messages_to_send.append(self.process_message(message))
                self.received_messages.remove(message)

    # @SystemLogger()
    def process_message(self, message):
        try:
            if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                    and ACCOUNT_NAME in message:
                self.logger.info(f'received valid message "{message}" from user with name: {message[ACCOUNT_NAME]}')
                self.store_clients_to_db(message[ACCOUNT_NAME], message[TIME])
                return message[ACCOUNT_NAME], {RESPONSE: 200}

            elif ACTION in message and message[ACTION] == MESSAGE and MESSAGE_TEXT in message and TIME in message \
                    and SENDER in message and RECEIVER in message:
                self.logger.info(f'received valid message "{message}"')
                return message[RECEIVER], message

            self.logger.info(f'received invalid message "{message}"')
            return {
                RESPONSE: 400,
                ERROR: 'Incorrect request'
            }
        except Exception as e:
            print('Не удалось обработать сообщение', e)
            self.logger.error(f'fail to process message: "{message}"')

    def send_all(self):
        for pair in self.messages_to_send:
            receiver_name, message = pair
            if receiver_name in self.contacts:
                receiver = self.contacts[receiver_name]
                # if receiver in self.write_queue:
            else:
                receiver = self.contacts[message[SENDER]]
                message = {
                    ACTION: MESSAGE,
                    RECEIVER: receiver_name,
                    SENDER: 'SERVER',
                    TIME: time.time(),
                    MESSAGE_TEXT: 'Ошибка!!! Клиента с таким именем не существует!!!'
                }
            try:
                write_message_to_sock(message, receiver)
            except Exception as e:
                self.logger.info(
                    f'получатель сообщения отключился.  Адрес получателя: {receiver}. Сообщение об ошибки: {e}')
            self.messages_to_send.remove(pair)


if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.start_listen()
