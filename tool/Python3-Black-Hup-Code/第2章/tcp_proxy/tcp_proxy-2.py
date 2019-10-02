import socket
import threading
import re
import os
import json
import requests
import sys
import getopt
import traceback


ip = "192.168.0.105"
port = 8889


def init_ip_port():
    global ip
    global port
    data_file_path = os.getcwd() + "/ip_port.json"
    if not os.path.exists(data_file_path):
        with open(data_file_path, "w") as f:
            f.write(json.dumps({"ip": ip, "port": port}))
    else:
        with open(data_file_path, "r") as f:
            data_dict = json.loads(f.read())
            ip = data_dict["ip"]
            port = data_dict["port"] + 1
        with open(data_file_path, "w") as f:
            f.write(json.dumps({"ip": ip, "port": port}))


def get_http_addr(data):
    a = re.search("Host: (.*)\r\n", str(data, encoding="utf-8"))
    host = a.group(1)
    a = host.split(":")
    if len(a) == 1:
        return a[0], 80
    else:
        return a[0], int(a[1])


def receive_data(connection):
    receive_len = 1
    response = b""
    while receive_len:
        data = connection.recv(4096)
        receive_len = len(data)
        response += data
        if receive_len < 4096:
            break
    return response


def get_request_type(data):
    match_result = re.search("http://.*? ", str(data, encoding="utf-8"))
    # print(match_result.group())
    if match_result:
        if "mode_9=https" in match_result.group():
            return "https", match_result.group()
    return "http", ""


def client(conn, caddr):
    try:
        data = receive_data(conn)
        print('发给目的服务器数据：', data)
        if "CONNECT" in str(data, encoding="utf-8"):
            d = "no support https!!!".encode("utf-8")
        else:
            request_type = get_request_type(data)
            print("request_type = " + request_type[0])
            addr = get_http_addr(data)
            print("目的服务器：", addr)
            if request_type == "https":
                url = "https"+request_type[1][4:]
                response = requests.get(url)
                d = response.text.encode("utf-8")
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(addr)
                s.sendall(data)                 # 将请求数据发给目的服务器
                d = receive_data(s)             # 接收目的服务器发过来的数据
                s.close()                       # 断开与目的服务器的连接
        print('接收目的服务器数据:', d)
        conn.sendall(d)                 # 发送给代理的客户端
        # print("发送给客户端完成")
    except Exception as e:
        print('代理的客户端异常：%s, ERROR:%s' % (caddr, repr(e)))
        print('str(Exception):\t', str(Exception))
        print('traceback.print_exc():', traceback.print_exc())
    finally:
        print("关闭该连接 --> " + str(conn))
        conn.close()


def server():
    global ip
    global port

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(10)
    print('proxy start..., listening on %s:%d' % (ip, port))
    while True:
        conn, addr = s.accept()
        print('conn:', conn)
        print("addr:", addr)
        threading.Thread(target=client, args=(conn, addr)).start()


def proxy_server():
    global ip
    global port

    init_ip_port()

    try:
        server()
    except Exception as e:
        print('代理服务器异常', e)
        traceback.print_exc()

    print('server end!!!')


def proxy_request():
    global ip
    global port
    data_file_path = os.getcwd() + "/ip_port.json"
    if os.path.exists(data_file_path):
        with open(data_file_path, "r") as f:
            data_dict = json.loads(f.read())
            ip = data_dict["ip"]
            port = data_dict["port"]

    proxies = {
        "http": "http://" + ip + ":" + str(port),
        # "https": "https://" + ip + ":" + str(port)
    }

    # url = "http://httpbin.org/get?a=11111111111111"
    url = "http://www.baidu.com/s?ie=utf-8&wd=http&mode_9=https"
    response = requests.get(url, proxies=proxies, timeout=15)
    print(response.text)
    # print("ip = " + json.loads(response.text)["origin"])


def usage():
    print("Zheng Net Proxy")
    print("")
    print("--mode -->mode proxy_server/proxy_request")
    print("")
    print("Examples:")
    print("python tcp_proxy.py --mode=proxy_server")
    print("python tcp_proxy.py --mode=proxy_request")
    sys.exit(0)


def main():
    if not len(sys.argv[1:]):
        return usage()

    opts = ""
    args = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h",
                                   ["help", "mode=", ])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    print(opts)
    print(args)

    mode = ""

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("--mode", ):
            if a not in ("proxy_server", "proxy_request"):
                raise Exception("Mode Error! Please Select Mode in [proxy_server, proxy_request]")
            mode = a
        else:
            assert False, "Unhandled Option!"

    if len(mode) <= 0:
        usage()
        assert False, "Option Error!"

    if mode == "proxy_server":
        proxy_server()
    else:
        proxy_request()


if __name__ == '__main__':
    main()
    # a = get_request_type("GET http://httpbin.org/get?a=11111111111111&mode_9=https HTTP/1.1\r\nHost: httpbin.org\r\nUser-Agent: python-requests/2.21.0\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nConnection: keep-alive\r\n\r\n".encode("utf-8"))
    # print(a)
    # url = "http://www.baidu.com/s?ie=utf-8&wd=http&mode_9=https"
    # print()
