import ipaddress
from task_1 import host_ping


def host_range_ping(net):
    network = ipaddress.ip_network(net)
    host_ping(network)


if __name__ == '__main__':
    host_range_ping('10.0.0.0/25')
