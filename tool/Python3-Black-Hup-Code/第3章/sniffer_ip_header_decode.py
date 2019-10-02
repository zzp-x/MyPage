"""
    与书中的代码有些不同，但功能是类似的
    一个解析IP数据包的工具
"""

import socket
import os
import traceback
import time
from struct import *

host = "192.168.0.104"


# IP 解析
class IP:
    def __init__(self, socket_buffer=None):
        # 协议字段与协议名称对应
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # print(socket_buffer)

        packet = socket_buffer[0]
        ip_header = packet[0:20]
        iph = unpack('!BBHHHBBH4s4s',ip_header)
        version = iph[0] >> 4   # Version
        ihl = iph[0] * 0xF      # IHL
        iph_length = ihl * 4    # Total Length
        ttl = iph[5]
        protocol = iph[6]
        s_addr = socket.inet_ntoa(iph[8])
        d_addr = socket.inet_ntoa(iph[9])
        print(time.ctime())
        protocol_name = self.protocol_map.get(protocol)
        if not protocol_name:
            protocol_name = protocol
        print('Protocol : ' + str(protocol_name) + ' Version : ' + str(version) + ' IHL : ' + str(ihl) + ' Total Length: '+str(iph_length) + ' TTL : ' + str(ttl) + ' Src : ' + str(s_addr) + ' Dst : ' + str(d_addr))
        if protocol == 6:
            tcp_header = packet[20:40]
            tcph = unpack('!HHLLBBHHH' , tcp_header)
            source_port = tcph[0]
            dest_port = tcph[1]
            sequence = tcph[2]
            acknowledgement = tcph[3]
            doff_reserved = tcph[4]
            tcph_length = doff_reserved >> 4
            print('Source Port : ' + str(source_port) + ' Dest Port : ' + str(dest_port) + ' Sequence Number : ' + str(sequence) + ' Acknowledgement : ' + str(acknowledgement) + ' TCP header length : ' + str(tcph_length))
            data = packet[40:len(packet)]
            # print('Data : ' + str(data))

if os.name == "nt":   # posix ,nt ,java，对应linux/windows/java虚拟机
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host, 0))

# 设置在捕获的数据包中包含IP头
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# 在window平台上，我们需要设置IOCGTL以启用混杂模式
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

try:
    while True:
        # 读取单个数据包
        raw_buffer = sniffer.recvfrom(65565)
        # print(raw_buffer)
        ip_header = IP(raw_buffer)
        # print(ip_header)

        # 输出协议和通信双方IP地址
        # print("Protocol: %s %s -> %s " % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))
except Exception as e:
    # print(e)
    print(traceback.print_exc())
finally:
    # 在windows平台上关闭混杂模式
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

    print("program end!!!")

