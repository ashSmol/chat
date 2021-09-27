import sys
from socket import *

from common.utils import read_message_from_sock, write_message_to_sock
from common.vars import *


class ChatServer:
    def __init__(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.start_listen()

    def start_listen(self):
        try:
            if '-a' in sys.argv:
                host_addr = sys.argv[sys.argv.index('-a') + 1]
            if '-p' in sys.argv:
                port_num = int(sys.argv[sys.argv.index('-p') + 1])

            self.sock.bind((host_addr, port_num))
        except Exception as e:
            print('Не удалось найти обязательные параметры сервера. Будут использоваться дефолтные значения')
            self.sock.bind((DEFAULT_HOST_ADDR, DEFAULT_HOST_PORT))

        while True:
            self.sock.listen(MAX_CONNECTIONS)
            client, client_addr = self.sock.accept()
            self.process_message(client)

    def process_message(self, client):
        message_from_cient = read_message_from_sock(client)
        print(f'От клиента: {client}\n Получено сообзение:\n {message_from_cient}')
        if ACTION in message_from_cient and message_from_cient[ACTION] == PRESENCE and TIME in message_from_cient \
                and USER_ACCOUNT in message_from_cient and message_from_cient[USER_ACCOUNT][ACCOUNT_NAME] == 'Guest':
            write_message_to_sock({RESPONSE: 200})
        write_message_to_sock(
            {
                RESPONSE: 400,
                ERROR: 'Incorrect request'
            }
        )


chat_server = ChatServer()
