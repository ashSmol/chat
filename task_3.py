import ipaddress
import socket
import subprocess

import tabulate


def host_range_ping_tab(net):
    available_hosts = []
    not_available_hosts = []
    network = ipaddress.ip_network(net)
    for host in network:
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
            available_hosts.append({'available': host})
        else:
            not_available_hosts.append({'not available': host})
    print(tabulate.tabulate(available_hosts, headers='keys', tablefmt="grid"))
    print(tabulate.tabulate(not_available_hosts, headers='keys', tablefmt="grid"))


if __name__ == '__main__':
    host_range_ping_tab('10.0.0.0/30')
