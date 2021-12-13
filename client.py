import json
import logging
import socket

import time
from logging import Logger
from threading import Thread

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
    def __init__(self):
        self.logger = logging.getLogger('app.client')
        self.host_addr, self.host_port, self.client_name = get_socket_params()

    # @SystemLogger()
    def run_socket(self):
        self.logger.debug('running socket')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host_addr, self.host_port))
            self.logger.info(f'connected to server {self.host_addr}:{self.host_port}')
        except Exception as e:
            self.logger.critical(f'fail to connect to server {self.host_addr}:{self.host_port} - {e}')

    # @SystemLogger()
    def create_presence(self):
        result = {
            ACTION: PRESENCE,
            TIME: time.time(),
            ACCOUNT_NAME: self.client_name
        }
        self.logger.info(f'сформировано сообщение {result}')
        return result

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
            return f'400 : {message[ERROR]}'
        self.logger.error('Сервер вернул некорректный ответ')
        raise ValueError

    def handle_get_contacts_response(self, message):
        if message[RESPONSE] == '202' and message[CLIENTS_LOGINS]:
            return message[CLIENTS_LOGINS]

    # @SystemLogger()
    def run_client(self):
        print(f'Имя клиента: {self.client_name}')
        write_message_to_sock(self.create_presence(), self.sock)
        presence_answer = self.process_ans(read_message_from_sock(self.sock))
        if presence_answer == '200 : OK':
            print('Соединение с сервером успешно установлено.')
        else:
            print(f'Сервер вернул ошибку: {presence_answer}')
        # добавление контакта
        print('Adding contact "alex"')
        write_message_to_sock(self.add_contact_request('alex'), self.sock)
        add_contacts_response = read_message_from_sock(self.sock)
        self.handle_add_contact_response(add_contacts_response)
        time.sleep(1)
        #  получение контактов
        write_message_to_sock(self.get_contacts(), self.sock)
        get_contacts_response = read_message_from_sock(self.sock)
        contacts = self.handle_get_contacts_response(get_contacts_response)
        print(f'С Сервера загружены контакты: {contacts}')
        # удаление контакта
        print('remove contact "alex"')
        write_message_to_sock(self.del_contact_request('alex'), self.sock)
        add_contacts_response = read_message_from_sock(self.sock)
        self.handle_add_contact_response(add_contacts_response)
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

    def handle_add_contact_response(self, response):
        print(response[RESPONSE])

    def del_contact_request(self, contact_name):
        return {
            ACTION: DEL_CONTACT,
            ACCOUNT_NAME: self.client_name,
            TIME: time.time(),
            CONTACT_NAME: contact_name
        }

    def handle_del_contact_response(self, response):
        print(response[RESPONSE])


if __name__ == '__main__':
    client = ChatClient()
    client.run_socket()
    client.run_client()
