from socket import *

from common.utils import read_message_from_sock, write_message_to_sock, get_socket_params
from common.vars import *


class ChatServer:
    def __init__(self):
        self.sock = None

    def start_listen(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind(get_socket_params())
        while True:
            self.sock.listen(MAX_CONNECTIONS)
            client, client_addr = self.sock.accept()
            message = read_message_from_sock(client)
            answer = self.process_message(message)
            write_message_to_sock(answer, client)

    def process_message(self, message):
        try:
            if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                    and USER_ACCOUNT in message and message[USER_ACCOUNT][ACCOUNT_NAME] == 'Guest':
                return {RESPONSE: 200}
            return {
                RESPONSE: 400,
                ERROR: 'Incorrect request'
            }
        except Exception as e:
            print('Не удалось обработать сообщение', e)


if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.start_listen()
