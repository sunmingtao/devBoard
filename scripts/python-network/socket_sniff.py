import os
import socket
import ipaddress
import struct
import sys
import time
import threading

SUBNET = '192.168.0.0/24'
MESSAGE = 'PYTHONRULES!'

class IP:
    def __init__(self, buff=None):
        header = struct.unpack('!BBHHHBBH4s4s', buff)
        self.ver = header[0] >> 4
        self.ihl = header[0] & 0xF

        self.tos = header[1]
        self.len = header[2]
        self.id = header[3]
        self.offset = header[4]
        self.ttl = header[5]
        self.protocol_num = header[6]
        self.sum = header[7]
        self.src = header[8]
        self.dst = header[9]

        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)

        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except Exception as e:
            self.protocol = str(self.protocol_num)

def udp_sender():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        for ip in ipaddress.ip_network(SUBNET).hosts():
            sender.sendto(bytes(MESSAGE, 'utf-8'), (str(ip), 65212)) 

class ICMP:
    def __init__(self, buff):
        header = struct.unpack('!BBHHH', buff)
        self.type = header[0]
        self.code = header[1]
        self.sum = header[2]
        self.id = header[3]
        self.seq = header[4]

def sniff(host):
    if os.name == 'nt':
        socket_protocal = socket.IPPROTO_IP
    else:
        socket_protocal = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocal)
    sniffer.bind((host, 0))
    print('sniffer bound')
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    try:    
        while True:
            raw_bufffer = sniffer.recvfrom(65565)[0]
            ip_header = IP(raw_bufffer[0:20])
            if ip_header.protocol == "ICMP":
                print(f'Protocol: {ip_header.protocol} {ip_header.src_address} -> {ip_header.dst_address}')
                print(f'IP -> Version: {ip_header.ver} Header Length: {ip_header.ihl} TTL: {ip_header.ttl}')
                offset = ip_header.ihl * 4
                buf = raw_bufffer[offset:offset + 8]
                icmp_header = ICMP(buf)
                print(f'ICMP -> Type: {icmp_header.type} Code: {icmp_header.code}')
            
    except KeyboardInterrupt:
        if os.name == 'nt':
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)  
        sys.exit()  

class Scanner:
    def __init__(self, host):
        self.host = host
        if os.name == 'nt':
            self.socket_protocal = socket.IPPROTO_IP
        else:
            self.socket_protocal = socket.IPPROTO_ICMP

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, self.socket_protocal)
        self.socket.bind((host, 0))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        if os.name == 'nt':
            self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON) 
        
    def sniff(self):
        hosts_up = set([f'{str(self.host)} *'])
        try:
            while True:
                raw_bufffer = self.socket.recvfrom(65565)[0]
                ip_header = IP(raw_bufffer[0:20])
                if ip_header.protocol == "ICMP":
                    offset = ip_header.ihl * 4
                    buf = raw_bufffer[offset:offset + 8]
                    icmp_header = ICMP(buf)
                    if icmp_header.code == 3 and icmp_header.type == 3:
                        if ipaddress.ip_address(ip_header.src_address) in ipaddress.ip_network(SUBNET):
                            # if raw_bufffer[len(raw_bufffer) - len(MESSAGE):] == bytes(MESSAGE, 'utf-8'):
                            hosts_up.add(f'{ip_header.src_address}')
                            print(f'Host Up: {ip_header.src_address}')
        except KeyboardInterrupt:
            if os.name == 'nt':
                self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)  
            print('\n\nUser Interrupted.')
            print(f'Hosts up on {SUBNET}')
            if hosts_up:
                print(f'\n\nSummary: Hosts up on {SUBNET}')
            for host in hosts_up:
                print(f'{host}')
            sys.exit()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = '192.168.0.11'
    s = Scanner(host)
    time.sleep(5)
    t = threading.Thread(target=udp_sender)
    t.start()
    s.sniff()

# cp socket_sniff.py /mnt/c/Users/Public/Downloads
# Start cmd as administrator
# cd C:\Users\Public\Downloads
# py socket_sniff.py
