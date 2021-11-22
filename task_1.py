import ipaddress
import re
import socket
import subprocess

import chardet as chardet


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
        process = subprocess.Popen(f'ping {ip}', stdout=subprocess.PIPE)
        out = process.stdout.read()
        encoding = chardet.detect(out)['encoding']
        decoded_out = out.decode(encoding)
        if re.findall('.*потерь', decoded_out)[0].find('100') > 0:
            print(f'host {host} not available')
        else:
            print(f'host {host} available')


if __name__ == '__main__':
    host_ping(['1111.eqw', 'ya.ru', '1.0.0.1', 'localhost', '192.168.1.2'])
