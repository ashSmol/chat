import logging
from socket import *

from common.utils import read_message_from_sock, write_message_to_sock, get_socket_params
from common.vars import *
import logs.server_conf_log

class ChatServer:
    def __init__(self):
        self.logger = logging.getLogger('app.server')
        self.logger.info('created server object')
        self.sock = None

    def start_listen(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        addr, port = get_socket_params()
        self.sock.bind((addr, port))
        self.logger.info(f'socket bind to addr {addr}:{port}')
        while True:
            self.sock.listen(MAX_CONNECTIONS)
            client, client_addr = self.sock.accept()
            message = read_message_from_sock(client)
            self.logger.info(f'received message: "{message}". from {client_addr}')
            answer = self.process_message(message)
            self.logger.info(f'answer  "{answer}" is sent to {client} ')
            write_message_to_sock(answer, client_addr)

    def process_message(self, message):
        try:
            if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                    and USER_ACCOUNT in message and message[USER_ACCOUNT][ACCOUNT_NAME] == 'Guest':
                self.logger.info(f'received valid message "{message}"')
                return {RESPONSE: 200}
            self.logger.info(f'received invalid message "{message}"')
            return {
                RESPONSE: 400,
                ERROR: 'Incorrect request'
            }
        except Exception as e:
            print('Не удалось обработать сообщение', e)
            self.logger.error(f'fail to process message: "{message}"')


if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.start_listen()
