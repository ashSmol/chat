import ipaddress
from task_1 import host_ping


def host_range_ping(ip_1: ipaddress, ip_2: ipaddress):
    net = ipaddress.ip_network(ip_1)
    net.add(ip_2)
    host_ping(net)


host_range_ping('10.0.0.1', '10.0.0.2')
