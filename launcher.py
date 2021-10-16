import subprocess

from common.vars import CLIENT_TYPES, SENDER, RECEIVER


class Launcher:
    PROCESSES = []

    def start_server(self):
        self.PROCESSES.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))

    def start_client(self, client_name):
        self.PROCESSES.append(subprocess.Popen(f'python client.py -n {client_name}',
                                               creationflags=subprocess.CREATE_NEW_CONSOLE))

    def start_all(self):
        self.start_server()
        self.start_client('user_1')
        self.start_client('user_2')
        self.start_client('user_3')

    def close_all(self):
        for process in self.PROCESSES:
            process.kill()


launcher = Launcher()
launcher.start_all()
command = ''
while command != 'close':
    command = input('Enter "close" to close all windows:')
launcher.close_all()
