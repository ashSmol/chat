import dis
import socket


class ClientVerifierMeta(type):
    def __init__(self, clsname, bases, clsdict):
        for key, value in clsdict.items():
            if isinstance(value, socket.socket):
                raise ValueError
            if callable(value):
                dis_str = dis.code_info(value)
                if (dis_str.find('socket') > 0) & (dis_str.find('accept') > 0):
                    raise ValueError('ACCEPT!!!')
        type.__init__(self, clsname, bases, clsdict)


class Client(metaclass=ClientVerifierMeta):
    sock = 'socket.socket(socket.AF_INET, socket.SOCK_STREAM)'

    def __init__(self):
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM).accept()
        pass

    def create_sock(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM).accept()


if __name__ == '__main__':
    client = Client()
