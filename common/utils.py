import json
import sys
from socket import socket

from common.vars import ENCODING, MAX_PACKAGE_LENGTH, DEFAULT_HOST_ADDR, DEFAULT_HOST_PORT


def write_message_to_sock(message: dict, sock: socket):
    json_obj = json.dumps(message)
    bytes_message = json_obj.encode(ENCODING)
    sock.send(bytes_message)


def read_message_from_sock(sock: socket):
    bytes_message = sock.recv(MAX_PACKAGE_LENGTH)
    json_obj = bytes_message.decode(ENCODING)
    return json.loads(json_obj)


def get_socket_params():
    try:
        if '-a' in sys.argv:
            host_addr = sys.argv[sys.argv.index('-a') + 1]
        if '-p' in sys.argv:
            port_num = int(sys.argv[sys.argv.index('-p') + 1])

    except Exception:
        print('Не удалось найти обязательные параметры сервера. Будут использоваться дефолтные значения')
        host_addr = DEFAULT_HOST_ADDR
        port_num = DEFAULT_HOST_PORT

    return host_addr, port_num
