import ipaddress
import socket
import subprocess


def host_ping(hosts_list):
    for host in hosts_list:
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            try:
                ip = socket.gethostbyname(host)
            except socket.gaierror:
                print(f'No such host {host}')
                continue
        response = subprocess.run("ping -n 1 -w 1000 " + str(ip), stdout=subprocess.PIPE).returncode
        if response == 0:
            print(f'{host} is up!')
        else:
            print(f'{host} is down!')


if __name__ == '__main__':
    host_ping(['1111.eqw', 'ya.ru', '1.0.0.1', 'localhost', '192.168.1.2'])
