import json
from socket import socket

from common.vars import ENCODING, MAX_PACKAGE_LENGTH


def write_message_to_sock(message: dict, sock: socket):
    json_obj = json.dumps(message)
    bytes_message = json_obj.encode(ENCODING)
    sock.send(bytes_message)


def read_message_from_sock(sock: socket):
    bytes_message = sock.recv(MAX_PACKAGE_LENGTH)
    json_obj = bytes_message.decode(ENCODING)
    return json.loads(json_obj)
