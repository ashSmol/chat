import subprocess

from common.vars import CLIENT_TYPES, SENDER, RECEIVER


class Launcher:
    PROCESSES = []

    def start_server(self):
        self.PROCESSES.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))

    def start_client(self, client_type):
        if client_type in CLIENT_TYPES:
            self.PROCESSES.append(subprocess.Popen(f'python client_.py -m {client_type}',
                                                   creationflags=subprocess.CREATE_NEW_CONSOLE))

    def start_all(self):
        self.start_server()
        for i in range(2):
            self.start_client(SENDER)
            self.start_client(RECEIVER)

    def close_all(self):
        for process in self.PROCESSES:
            process.kill()


launcher = Launcher()
launcher.start_all()
command = ''
while command != 'close':
    command = input('Enter "close" to close all windows:')
launcher.close_all()
