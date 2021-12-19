import dis
import logging
import select
import socket
import subprocess
import time
from socket import *

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import sessionmaker

from common.utils import read_message_from_sock, write_message_to_sock, get_socket_params
from common.vars import *
from logs.system_logger import SystemLogger
from model import ChatClientModel, ClientHistory, Contacts
from logs import server_conf_log


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

    def start_listen(self, port_num=None):
        self.sock = socket(AF_INET, SOCK_STREAM)
        addr, self.port, _ = get_socket_params()
        if port_num:
            self.port = port_num
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

    def store_contact_to_db(self, client_login, contact_login):
        client = self.db_session.query(ChatClientModel).filter_by(login=client_login).first()
        contact = self.db_session.query(ChatClientModel).filter_by(login=contact_login).first()
        if not (contact and client):
            raise Exception('Fail to store contact to DB client login and contact login should be in database')
        try:
            record = self.db_session.query(Contacts).filter_by(client_id=client.id, contact_id=contact.id).first()
            if record:
                raise Exception('The record, you are tryimg to add, already exists in database')
            self.db_session.add(Contacts(client.id, contact.id))
        except DBAPIError as err:
            self.logger.error('Fail to store contact to DB. Transaction rolling back', err)
            self.db_session.rollback()
        else:
            self.db_session.commit()

    def store_clients_to_db(self, login: str, info: str):
        # проверка есть ли в базе такой клиент
        client_id = self.db_session.query(ChatClientModel).filter_by(login=login).first()
        try:
            if not client_id:
                self.db_session.add(ChatClientModel(login, info))
        except Exception as err:
            self.logger.error(err)
            print(err)
            self.db_session.rollback()
        else:
            self.db_session.commit()

    def store_history_to_db(self, login: str, time_: str, message_text: str):
        client = self.db_session.query(ChatClientModel).filter_by(login=login).first()
        if client:
            try:
                self.db_session.add(ClientHistory(client.id, time_, message_text))
            except Exception as err:
                self.logger.error(err)
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
                try:
                    self.store_clients_to_db(message[ACCOUNT_NAME], message[TIME])
                except DBAPIError as err:
                    print(err)

                return message[ACCOUNT_NAME], {RESPONSE: 200}

            elif ACTION in message and message[ACTION] == MESSAGE and MESSAGE_TEXT in message and TIME in message \
                    and SENDER in message and RECEIVER in message:
                self.store_history_to_db(message[SENDER], message[TIME], message[MESSAGE_TEXT])
                self.logger.info(f'received valid message "{message}"')
                return message[RECEIVER], message

            elif ACTION in message and message[ACTION] == GET_CONTACTS and TIME in message and ACCOUNT_NAME in message:
                client = self.db_session.query(ChatClientModel).filter_by(login=message[ACCOUNT_NAME]).first()
                contacts = self.db_session.query(Contacts).filter_by(client_id=client.id).all()
                result = []
                for contact in contacts:
                    contact_login = self.db_session.query(ChatClientModel).filter_by(id=contact.contact_id).first()
                    result.append(contact_login.login)
                return message[ACCOUNT_NAME], {RESPONSE: '202', CLIENTS_LOGINS: result}

            elif ACTION in message and message[
                ACTION] == ADD_CONTACT and TIME in message and ACCOUNT_NAME in message and CONTACT_NAME in message:
                try:
                    self.store_contact_to_db(message[ACCOUNT_NAME], message[CONTACT_NAME])
                except Exception as err:
                    self.logger.error(err)
                    return message[ACCOUNT_NAME], {RESPONSE: err.args[0]}
                return message[ACCOUNT_NAME], {RESPONSE: '202'}

            elif ACTION in message and message[
                ACTION] == DEL_CONTACT and TIME in message and ACCOUNT_NAME in message and CONTACT_NAME in message:
                try:
                    self.del_contact_from_db(message[ACCOUNT_NAME], message[CONTACT_NAME])
                except Exception as err:
                    self.logger.error(err)
                    return message[ACCOUNT_NAME], {RESPONSE: err.args[0]}
                return message[ACCOUNT_NAME], {RESPONSE: '202'}

            self.logger.info(f'received invalid message "{message}"')
            return message[ACCOUNT_NAME], {
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

    def del_contact_from_db(self, client_login, contact_login):
        client = self.db_session.query(ChatClientModel).filter_by(login=client_login).first()
        contact = self.db_session.query(ChatClientModel).filter_by(login=contact_login).first()
        if not (contact and client):
            raise Exception('Fail to find such contact in database')
        try:
            query = self.db_session.query(Contacts).filter_by(client_id=client.id, contact_id=contact.id)
            if not query.first():
                raise Exception('The record, you are trying to delete, does not exists in your contacts.')
            query.delete()
        except DBAPIError as err:
            self.logger.error('Fail to store contact to DB. Transaction rolling back', err)
            self.db_session.rollback()
        else:
            self.db_session.commit()

    def stop(self):
        print('stopping server')
        del self


if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.start_listen()
