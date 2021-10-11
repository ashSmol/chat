import json
import logging
import socket
import sys
import time

from common.utils import read_message_from_sock, write_message_to_sock, get_socket_params
from common.vars import ACTION, PRESENCE, TIME, USER_ACCOUNT, RESPONSE, ERROR, ACCOUNT_NAME, CLIENT_TYPES, SENDER, \
    RECEIVER, DEFAULT_CLIENT_TYPE, MESSAGE, MESSAGE_TEXT
import logs.client_conf_log
from logs.system_logger import SystemLogger


class ChatClient:
    @SystemLogger()
    def __init__(self):
        self.logger = logging.getLogger('app.client')
        if SENDER in sys.argv:
            self.client_type = SENDER
        else:
            self.client_type = DEFAULT_CLIENT_TYPE
        self.sock = None

    @SystemLogger()
    def run_socket(self):
        self.logger.debug('running socket')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr, port = get_socket_params()
        try:
            self.sock.connect((addr, port))
            self.logger.info(f'connected to server {addr}:{port}')
        except Exception as e:
            self.logger.critical(f'fail to connect to server {addr}:{port} - {e}')

    @SystemLogger()
    def create_presence(self, account_name='Guest'):
        result = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER_ACCOUNT: {
                ACCOUNT_NAME: account_name
            }
        }
        self.logger.info(f'сформировано сообщение {result}')
        return result

    @SystemLogger()
    def process_ans(self, message):
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {message[ERROR]}'
        self.logger.error('Сервер вернул некорректный ответ')
        raise ValueError

    @SystemLogger()
    def send_message(self):
        try:
            write_message_to_sock(self.create_presence(), self.sock)
            answer = self.process_ans(read_message_from_sock(self.sock))
            self.logger.info(f'сервер вернул ответ: "{answer}"')
        except (ValueError, json.JSONDecodeError):
            self.logger.error('Не удалось декодировать сообщение сервера.')
        except TypeError as e:
            self.logger.error(f'incorrect or None message received from server. Error: {e}')

    def run_client(self):
        if self.client_type == SENDER:
            self.run_sender_client()
        if self.client_type == RECEIVER:
            self.run_receiver_client()

    def run_sender_client(self):
        while True:
            text = input('Введите сообщение для отправки слушателям: ')
            message = self.create_text_message(text)
            try:
                write_message_to_sock(message, self.sock)
            except socket.error as e:
                self.logger.error(f'потеряно соединение с сервером. {e}')

    def create_text_message(self, text):
        return {
            ACTION: MESSAGE,
            USER_ACCOUNT: {ACCOUNT_NAME: "guest"},
            TIME: time.time(),
            MESSAGE_TEXT: text
        }

    def run_receiver_client(self):
        while True:
            try:
                message = read_message_from_sock(self.sock)
                print(f'получено сообщение!!! - {message[MESSAGE_TEXT].upper()}')

            except socket.error as e:
                self.logger.error(f'потеряно соединение с сервером. {e}')


if __name__ == '__main__':
    client = ChatClient()
    client.run_socket()
    client.run_client()
    # client.send_message()
