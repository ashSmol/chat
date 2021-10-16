import json
import logging
import socket

import time
from threading import Thread

from common.utils import read_message_from_sock, write_message_to_sock, get_socket_params
from common.vars import ACTION, PRESENCE, TIME, RESPONSE, ERROR, ACCOUNT_NAME, MESSAGE, MESSAGE_TEXT, \
    SENDER, RECEIVER
import logs.client_conf_log
from logs.system_logger import SystemLogger


class ChatClient:
    @SystemLogger()
    def __init__(self):
        self.logger = logging.getLogger('app.client')
        self.host_addr, self.host_port, self.client_name = get_socket_params()

    @SystemLogger()
    def run_socket(self):
        self.logger.debug('running socket')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # addr, port = get_socket_params()
        try:
            self.sock.connect((self.host_addr, self.host_port))
            self.logger.info(f'connected to server {self.host_addr}:{self.host_port}')
        except Exception as e:
            self.logger.critical(f'fail to connect to server {self.host_addr}:{self.host_port} - {e}')

    @SystemLogger()
    def create_presence(self):
        result = {
            ACTION: PRESENCE,
            TIME: time.time(),
            ACCOUNT_NAME: self.client_name
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

    # @SystemLogger()
    # def send_message(self):
    #     try:
    #         write_message_to_sock(self.create_presence(), self.sock)
    #         answer = self.process_ans(read_message_from_sock(self.sock))
    #         self.logger.info(f'сервер вернул ответ: "{answer}"')
    #     except (ValueError, json.JSONDecodeError):
    #         self.logger.error('Не удалось декодировать сообщение сервера.')
    #     except TypeError as e:
    #         self.logger.error(f'incorrect or None message received from server. Error: {e}')

    def run_client(self):
        print(self.client_name)
        write_message_to_sock(self.create_presence(), self.sock)
        print(self.process_ans(read_message_from_sock(self.sock)))

        sending_thread = Thread(target=self.send_message)
        sending_thread.daemon = True
        sending_thread.start()
        # sending_thread.join()

        receiving_thread = Thread(target=self.receive_message)
        receiving_thread.daemon = True
        receiving_thread.start()
        # receiving_thread.join()
        while True:
            time.sleep(1)
            if receiving_thread.is_alive() and sending_thread.is_alive():
                continue
            break

    def send_message(self):
        while True:
            message_receiver = input('Введите адресата сообщения: ')
            text = input('Введите текст сообщение: ')
            message = self.create_text_message(message_receiver, text)
            try:
                write_message_to_sock(message, self.sock)
            except socket.error as e:
                self.logger.error(f'потеряно соединение с сервером. {e}')

    def create_text_message(self, receiver, text):
        return {
            ACTION: MESSAGE,
            RECEIVER: receiver,
            SENDER: self.client_name,
            TIME: time.time(),
            MESSAGE_TEXT: text
        }

    def receive_message(self):
        while True:
            try:
                message = read_message_from_sock(self.sock)
                if message:
                    print(
                        f'От пользователя {message[SENDER]} получено сообщение!!!\n - {message[MESSAGE_TEXT].upper()}')
            except socket.error as e:
                self.logger.error(f'потеряно соединение с сервером. {e}')


if __name__ == '__main__':
    client = ChatClient()
    client.run_socket()
    client.run_client()
