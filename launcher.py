import os
import subprocess
import time

from common.vars import CLIENT_TYPES, SENDER, RECEIVER


class Launcher:
    PROCESSES = []

    def start_server(self):
        self.PROCESSES.append(
            subprocess.Popen('venv/Scripts/python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))

    def start_client(self, client_name):
        self.PROCESSES.append(subprocess.Popen(f'venv/Scripts/python client.py -n {client_name}',
                                               creationflags=subprocess.CREATE_NEW_CONSOLE))

    def start_win(self):
        self.start_server()
        time.sleep(1)
        self.start_client('user_1')
        self.start_client('user_2')
        self.start_client('user_3')

    def close_all(self):
        for process in self.PROCESSES:
            process.kill()
            # TODO FIX closing all processes, as now they do not kelled in MacOs

    def start_posix(self):
        self.PROCESSES.append(subprocess.Popen('open -W -a Terminal server.command'.split()))
        time.sleep(1)
        self.PROCESSES.append(subprocess.Popen('open -W -a Terminal client1.command'.split()))
        self.PROCESSES.append(subprocess.Popen('open -W -a Terminal client2.command'.split()))


if __name__ == '__main__':
    launcher = Launcher()
    if not os.name == 'posix':
        launcher.start_win()
    else:
        launcher.start_posix()
    command = ''
    while command != 'close':
        command = input('Enter "close" to close all windows:')
    launcher.close_all()
