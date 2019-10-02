import subprocess
import platform
import time
import telnetlib
import os
import hashlib


def get_md5(value):
    md5 = hashlib.md5()
    md5.update(value.encode("utf-8"))
    return md5.hexdigest()


def run_command(command):
    res = subprocess.Popen(command.rstrip(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sout, serr = res.communicate()
    return sout.decode("gbk")


def check_ip(ip):
    ip_list = ip.strip().split(".")
    if len(ip_list) != 4:
        return False
    for i in ip_list:
        try:
            i = int(i)
        except:
            return False
        if i < 0 or i > 256:
            return False
    return True


def detail_ipconfig():
    result = run_command("ipconfig /all")
    row_list = result.split("\n")
    count = len(row_list)
    ipconfig_list = []
    ka_obj = {"ip4": []}
    for num in range(count):
        value = row_list[num]
        if ". :" in value:
            if "描述" in value:
                if len(ka_obj) > 1:
                    ipconfig_list.append(ka_obj)
                    ka_obj = {"ip4": []}
                ka_obj["name"] = value.split(":")[1].rstrip("\r").strip(" ")
            elif "IPv4 地址" in value:
                ka_obj["ip4"].append(value.split(":")[1].rstrip("\r").strip(" "))
            elif "物理地址" in value:
                ka_obj["mac"] = value.split(":")[1].rstrip("\r").strip(" ")
            elif "子网掩码" in value:
                ka_obj["subnet"] = value.split(":")[1].rstrip("\r").strip(" ")
            elif "默认网关" in value:
                ka_obj["gateway"] = value.split(":")[1].rstrip("\r").strip(" ")
    ipconfig_list.append(ka_obj)
    return ipconfig_list


def platform_msg():
    message = dict()
    message["platform"] = platform.platform()           #获取操作系统名称及版本号，'Linux-3.13.0-46-generic-i686-with-Deepin-2014.2-trusty'
    message["architecture"] = platform.architecture()  #获取操作系统的位数，('32bit', 'ELF')
    message["machine"] = platform.machine()            #计算机类型，'i686'
    message["node"] = platform.node()                  #计算机的网络名称，'XF654'
    message["processor"] = platform.processor()       #计算机处理器信息，''i686'
    return message


def python_msg():
    message = dict()
    message["build"] = platform.python_build()
    message["compiler"] = platform.python_compiler()
    message["branch"] = platform.python_branch()
    message["implementation"] = platform.python_implementation()
    message["version"] = platform.python_version()
    return message


def get_system_time():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def check_port(port):
    if port.isdigit():
        port = int(port)
        if port < 1 or port > 65535:
            return False
        else:
            return True
    else:
        return False


def telnet(ip, port):
    try:
        telnetlib.Telnet(ip, port)
        return True
    except:
        return False


def arp_table():
    row_data = run_command("arp -a")
    result = []
    obj = {"ips": []}
    for i in row_data.split("\n"):
        if "接口:" in i:
            if len(obj) > 1:
                result.append(obj)
            obj["interface"] = i.split(" ")[1]
            continue
        if "Internet 地址" in i or i == "\r" or i == "":
            continue
        ip = {
            "ip": i[2:20].strip(),
            "mac": i[22:45].strip(),
            "type": i[45:50].strip(),
        }
        obj["ips"].append(ip)
    result.append(obj)
    return result


def packet_sniffer(interface, count):
    from scapy.all import sniff,wrpcap
    if interface == "any":
        packets = sniff(filter="", count=count)
    else:
        packets = sniff(filter="", iface=interface, count=count)
    file_path = os.getcwd() + "/tool/cache/"
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    wrpcap(file_path + "/sniff.pcap", packets)


def get_local_area_network_msg():
    from scapy.all import srp, Ether, ARP, conf
    ipscan = '192.168.0.1/24'
    try:
        ans, unans = srp(Ether(dst="FF:FF:FF:FF:FF:FF") / ARP(pdst=ipscan), timeout=2, verbose=False)
    except Exception as e:
        print(str(e))
    else:
        result = []
        for snd, rcv in ans:
            mac = rcv.sprintf("%Ether.src%")
            ip = rcv.sprintf("%ARP.psrc%")
            result.append({"ip": ip, "mac": mac})
        return result


def main():
    # arp_table()
    # packet_sniffer("Realtek PCIe GBE Family Controller", 2000)
    get_local_area_network_msg()


if __name__ == '__main__':
    main()


