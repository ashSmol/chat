import argparse
import json
import sys

from common.vars import ENCODING, MAX_PACKAGE_LENGTH, DEFAULT_HOST_ADDR, DEFAULT_HOST_PORT


def write_message_to_sock(message, sock):
    try:
        json_obj = json.dumps(message)
        bytes_message = json_obj.encode(ENCODING)
        sock.send(bytes_message)
    except Exception as e:
        print(f'не удалось отправить сообщение!!! \n{e}')


def read_message_from_sock(sock):
    bytes_message = sock.recv(MAX_PACKAGE_LENGTH)
    json_obj = bytes_message.decode(ENCODING)
    return json.loads(json_obj)


def get_socket_params():
    """Создаём парсер аргументов коммандной строки
    и читаем параметры, возвращаем 3 параметра
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default=DEFAULT_HOST_ADDR, nargs='?')
    parser.add_argument('-p', default=DEFAULT_HOST_PORT, type=int, nargs='?')
    parser.add_argument('-n', default='user_151', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    return namespace.a, namespace.p, namespace.n
