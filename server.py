import logging
import select
import socket
import time
from socket import *

from common.utils import read_message_from_sock, write_message_to_sock, get_socket_params
from common.vars import *
from logs.system_logger import SystemLogger


class ChatServer:
    @SystemLogger()
    def __init__(self):
        self.messages_to_send = []
        self.all_clients = []
        self.read_queue = []
        self.write_queue = []
        self.received_messages = []
        self.logger = logging.getLogger('app.server')
        self.logger.info('created server object')
        self.sock = None

    def collect_all_messages(self):
        if self.read_queue:
            for client in self.read_queue:
                try:
                    self.received_messages.append(read_message_from_sock(client))
                except:
                    self.logger.info(f'Клиент {client.getpeername()} отключился.')
                    # if self.all_clients:
                    #     self.all_clients.remove(client)
                    #     self.read_queue.remove(client)

    @SystemLogger()
    def start_listen(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        addr, port = get_socket_params()
        self.sock.bind((addr, port))
        self.sock.settimeout(0.5)
        self.logger.info(f'socket bind to addr {addr}:{port}')
        while True:
            self.sock.listen(MAX_CONNECTIONS)
            try:
                client, client_addr = self.sock.accept()
                self.logger.info(f'новое соединение с клиентом {client_addr}. Добавляем в общий список')
                self.all_clients.append(client)
            except OSError:
                pass

            if self.all_clients:
                self.read_queue, self.write_queue, error_queue = select.select(self.all_clients, self.all_clients,
                                                                               [])
            self.collect_all_messages()
            self.build_responses()
            self.send_all()

    def build_responses(self):
        if self.received_messages:  # and self.write_queue:
            for message in self.received_messages:
                self.messages_to_send.append(self.process_message(message))
                self.received_messages.remove(message)

    @SystemLogger()
    def process_message(self, message):
        try:
            self.logger.critical("!!! crit error process_message")
            if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                    and USER_ACCOUNT in message and message[USER_ACCOUNT][ACCOUNT_NAME] == 'Guest':
                self.logger.info(f'received valid message "{message}"')
                return {RESPONSE: 200}

            elif ACTION in message and message[ACTION] == MESSAGE and MESSAGE_TEXT in message and TIME in message \
                    and USER_ACCOUNT in message and message[USER_ACCOUNT][ACCOUNT_NAME] == 'guest':
                self.logger.info(f'received valid message "{message}"')
                return {
                    ACTION: MESSAGE,
                    SENDER: message[USER_ACCOUNT][ACCOUNT_NAME],
                    TIME: time.time(),
                    MESSAGE_TEXT: message[MESSAGE_TEXT]
                }

            self.logger.info(f'received invalid message "{message}"')
            return {
                RESPONSE: 400,
                ERROR: 'Incorrect request'
            }
        except Exception as e:
            print('Не удалось обработать сообщение', e)
            self.logger.error(f'fail to process message: "{message}"')

    def send_all(self):
        for message in self.messages_to_send:
            for receiver in self.write_queue:
                try:
                    write_message_to_sock(message, receiver)
                except Exception as e:
                    self.logger.info(
                        f'получатель сообщения отключился.  Адрес получателя: {receiver}. Сообщение об ошибки: {e}')
            self.messages_to_send.remove(message)

if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.start_listen()
