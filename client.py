"""Программа-клиент"""

import json
import socket
import sys
import time

from common.utils import read_message_from_sock, write_message_to_sock
from common.vars import ACTION, PRESENCE, TIME, USER_ACCOUNT, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_HOST_ADDR, DEFAULT_HOST_PORT


def create_presence(account_name='Guest'):
    '''
    Функция генерирует запрос о присутствии клиента
    :param account_name:
    :return:
    '''
    # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER_ACCOUNT: {
            ACCOUNT_NAME: account_name
        }
    }
    return out


def process_ans(message):
    '''
    Функция разбирает ответ сервера
    :param message:
    :return:
    '''
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


def main():
    '''Загружаем параметы коммандной строки'''
    # client.py 192.168.1.2 8079
    try:
        server_address = sys.argv[2]
        server_port = int(sys.argv[4])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_HOST_ADDR
        server_port = DEFAULT_HOST_PORT
    except ValueError:
        print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    # Инициализация сокета и обмен

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((server_address, server_port))
    message_to_server = create_presence()
    write_message_to_sock(message_to_server, transport)
    try:
        answer = process_ans(read_message_from_sock(transport))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
