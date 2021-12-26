import hmac
import json
import logging
import socket

import time
from logging import Logger
from threading import Thread

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import sessionmaker

import client_db_model
import common.vars
from client_db_model import ContactModel, ContactsHistoryModel
from common.utils import read_message_from_sock, write_message_to_sock, get_socket_params
from common.vars import ACTION, PRESENCE, TIME, RESPONSE, ERROR, ACCOUNT_NAME, MESSAGE, MESSAGE_TEXT, \
    SENDER, RECEIVER, GET_CONTACTS, CLIENTS_LOGINS, ADD_CONTACT, CONTACT_NAME, DEL_CONTACT
import logs.client_conf_log
from logs.system_logger import SystemLogger

import dis
import socket


class ClientVerifierMeta(type):
    def __init__(cls, clsname, bases, clsdict):
        for attr in clsdict:
            value = clsdict[attr]
            if callable(value):
                clsdict[attr] = SystemLogger()
        type.__init__(cls, clsname, bases, clsdict)

    def __new__(self, clsname, bases, clsdict):
        is_tcp_connection = False
        for key, value in clsdict.items():
            if isinstance(value, socket.socket):
                raise ValueError
            if callable(value):
                dis_str = dis.code_info(value)
                if callable(value):
                    dis_str = dis.code_info(value)
                    if (dis_str.find('socket') > 0) & (dis_str.find('accept') > 0):
                        raise Exception('"Accept" operation is not allowed for ChatClient')
                    if (dis_str.find('socket') > 0) & (dis_str.find('listen') > 0):
                        raise Exception('"Listen" operation is not allowed for ChatClient')
                if (dis_str.find('socket') > 0) & (dis_str.find('AF_INET') > 0):
                    is_tcp_connection = True
        if not is_tcp_connection:
            raise ConnectionError('Connection type shoud be TCP!!!')
        return type.__new__(self, clsname, bases, clsdict)


class ChatClient(metaclass=ClientVerifierMeta):
    # @SystemLogger()
    def __init__(self, host_ip_addr=None, host_port=None, client_login=None, password=None):
        self.password = password
        Session = sessionmaker(bind=common.vars.CLIENT_DB_ENGINE)
        self.db_session = Session()
        self.logger = logging.getLogger('app.client')
        self.host_addr, self.host_port, self.client_name = get_socket_params()
        if host_ip_addr:
            self.host_addr = host_ip_addr
        if host_port:
            self.host_port = int(host_port)
        if client_login:
            self.client_name = client_login

    def run_socket(self):
        self.logger.debug('running socket')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host_addr, self.host_port))
            self.logger.info(f'connected to server {self.host_addr}:{self.host_port}')
        except Exception as e:
            self.logger.critical(f'fail to connect to server {self.host_addr}:{self.host_port} - {e}')
        return self.sock

    def presence_request(self):
        result = {
            ACTION: PRESENCE,
            TIME: time.time(),
            ACCOUNT_NAME: self.client_name,
            common.vars.ACCOUNT_PASSWORD: self.password
        }
        self.logger.info(f'сформировано сообщение {result}')
        return result

    def create_presence(self):
        write_message_to_sock(self.presence_request(), self.sock)
        presence_answer = self.process_ans(read_message_from_sock(self.sock))
        if presence_answer == '200 : OK':
            return {'code': 200, 'message': 'Соединение с сервером успешно установлено.'}
        else:
            return {'code': 400, 'message': f'Сервер вернул ошибку: {presence_answer}'}

    def get_contacts_from_db(self):
        contacts = self.db_session.query(ContactModel).all()
        return [contact.login for contact in contacts]

    def get_contacts(self):
        request = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            ACCOUNT_NAME: self.client_name
        }
        return request

    def process_ans(self, message):
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {message[MESSAGE]}'
        self.logger.error('Сервер вернул некорректный ответ')
        raise ValueError

    def handle_get_contacts_response(self, message):
        if message[RESPONSE] == '202' and message[CLIENTS_LOGINS]:
            return message[CLIENTS_LOGINS]

    def store_contact_to_db(self, login, info):
        # проверка есть ли в базе такой контакт
        contact_id = self.db_session.query(ContactModel).filter_by(login=login).first()
        try:
            if not contact_id:
                self.db_session.add(ContactModel(login, info))
        except Exception as err:
            self.logger.error(err)
            print(err)
            self.db_session.rollback()
        else:
            self.db_session.commit()

    # @SystemLogger()
    def run_client(self):
        print(f'Имя клиента: {self.client_name}')
        write_message_to_sock(self.presence_request(), self.sock)
        presence_answer = self.process_ans(read_message_from_sock(self.sock))
        if presence_answer == '200 : OK':
            print('Соединение с сервером успешно установлено.')
        else:
            print(f'Сервер вернул ошибку: {presence_answer}')
        # добавление контакта
        contact_login = 'alex'
        print(f'Adding contact {contact_login}')
        write_message_to_sock(self.add_contact_request(contact_login), self.sock)
        add_contacts_response = read_message_from_sock(self.sock)
        self.handle_add_contact_response(add_contacts_response, contact_login)
        time.sleep(1)
        #  получение контактов
        write_message_to_sock(self.get_contacts(), self.sock)
        get_contacts_response = read_message_from_sock(self.sock)
        contacts = self.handle_get_contacts_response(get_contacts_response)
        print(f'С Сервера загружены контакты: {contacts}')
        # удаление контакта
        print('remove contact "alex"')
        write_message_to_sock(self.del_contact_request(contact_login), self.sock)
        add_contacts_response = read_message_from_sock(self.sock)
        self.handle_del_contact_response(add_contacts_response, contact_login)
        time.sleep(1)
        # плучение списка контактов
        write_message_to_sock(self.get_contacts(), self.sock)
        get_contacts_response = read_message_from_sock(self.sock)
        contacts = self.handle_get_contacts_response(get_contacts_response)
        print(f'С Сервера загружены контакты: {contacts}')

        sending_thread = Thread(target=self.send_message)
        sending_thread.daemon = True
        sending_thread.start()

        receiving_thread = Thread(target=self.receive_message)
        receiving_thread.daemon = True
        receiving_thread.start()
        while True:
            time.sleep(1)
            if receiving_thread.is_alive() and sending_thread.is_alive():
                continue
            break

    # @SystemLogger()
    def send_message(self):
        while True:
            message_receiver = input('Введите адресата сообщения: ')
            text = input('Введите текст сообщение: ')
            message = self.create_text_message(message_receiver, text)
            try:
                write_message_to_sock(message, self.sock)
                self.store_msg_to_db(message_receiver, text)
            except socket.error as e:
                self.logger.error(f'потеряно соединение с сервером. {e}')

    # @SystemLogger()
    def create_text_message(self, receiver, text):
        return {
            ACTION: MESSAGE,
            RECEIVER: receiver,
            SENDER: self.client_name,
            TIME: time.time(),
            MESSAGE_TEXT: text
        }

    # @SystemLogger()
    def receive_message(self):
        while True:
            try:
                message = read_message_from_sock(self.sock)
                if message:
                    print(
                        f'\n От пользователя {message[SENDER]} получено сообщение:\n - {message[MESSAGE_TEXT]}')
            except socket.error as e:
                self.logger.error(f'потеряно соединение с сервером. {e}')

    def add_contact_request(self, contact_name):
        return {
            ACTION: ADD_CONTACT,
            ACCOUNT_NAME: self.client_name,
            TIME: time.time(),
            CONTACT_NAME: contact_name
        }

    def handle_add_contact_response(self, response, contact_login):
        if response[RESPONSE] == '202':
            print('Contact is added successfully')
            self.store_contact_to_db(contact_login, time.time())
        else:
            print(response[RESPONSE])

    def del_contact_request(self, contact_name):
        return {
            ACTION: DEL_CONTACT,
            ACCOUNT_NAME: self.client_name,
            TIME: time.time(),
            CONTACT_NAME: contact_name
        }

    def handle_del_contact_response(self, response, contact_login):
        if response[RESPONSE] == '202':
            print('Contact is removed successfully')
            self.del_contact_from_db(contact_login)
        else:
            print(response[RESPONSE])

    def del_contact_from_db(self, contact_login):
        try:
            self.db_session.query(ContactModel).filter_by(login=contact_login).delete()
        except Exception as err:
            self.logger.error(err)
            print(err)
            self.db_session.rollback()
        else:
            self.db_session.commit()

    def store_msg_to_db(self, message_receiver, text):
        self.store_contact_to_db(message_receiver, time.time())
        contact = self.db_session.query(ContactModel).filter_by(login=message_receiver).first()
        try:
            self.db_session.add(ContactsHistoryModel(contact_id=contact.id, timestamp=time.time(), message_text=text))
        except DBAPIError as err:
            self.logger.error(err)
            self.db_session.rollback()
        else:
            self.db_session.commit()


if __name__ == '__main__':
    client = ChatClient()
    client.run_socket()
    client.run_client()
