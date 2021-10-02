"""Программа-клиент"""

import json
import socket
import time

from common.utils import read_message_from_sock, write_message_to_sock, get_socket_params
from common.vars import ACTION, PRESENCE, TIME, USER_ACCOUNT, ACCOUNT_NAME, \
    RESPONSE, ERROR


class ChatClient:

    def __init__(self):
        self.sock = None

    def run_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(get_socket_params())

    def create_presence(self, account_name='Guest'):
        result = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER_ACCOUNT: {
                ACCOUNT_NAME: account_name
            }
        }
        return result

    def process_ans(self, message):
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {message[ERROR]}'
        raise ValueError

    def send_message(self):
        write_message_to_sock(self.create_presence(), self.sock)
        try:
            answer = self.process_ans(read_message_from_sock(self.sock))
            print(answer)
        except (ValueError, json.JSONDecodeError):
            print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    client = ChatClient()
    client.run_socket()
    client.send_message()
