from socket import *

from common.utils import read_message_from_sock, write_message_to_sock, get_socket_params
from common.vars import *


class ChatServer:
    def __init__(self):
        self.sock = socket(AF_INET, SOCK_STREAM)

    def start_listen(self):
        self.sock.bind(get_socket_params())
        while True:
            self.sock.listen(MAX_CONNECTIONS)
            client, client_addr = self.sock.accept()
            self.process_message(client)

    def process_message(self, client):
        try:
            message_from_cient = read_message_from_sock(client)
            print(f'От клиента: {client}\n Получено сообзение:\n {message_from_cient}')
            if ACTION in message_from_cient and message_from_cient[ACTION] == PRESENCE and TIME in message_from_cient \
                    and USER_ACCOUNT in message_from_cient and message_from_cient[USER_ACCOUNT][
                ACCOUNT_NAME] == 'Guest':
                write_message_to_sock({RESPONSE: 200}, client)
            write_message_to_sock(
                {
                    RESPONSE: 400,
                    ERROR: 'Incorrect request'
                }, client
            )
        except Exception as e:
            print('Не удалось обработать сообщение', e)


chat_server = ChatServer()
chat_server.start_listen()
