import os
import subprocess
import socket
import threading

def get_target_ip(mac):
    sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_udp.bind(('0.0.0.0', 1000))
    (data, addr) = sock_udp.recvfrom(1024)
    print(data)
    return addr

if __name__ == '__main__':
    the_mac = 'ec-62-60-fe-81-98'
    HOST = ''
    print(HOST)