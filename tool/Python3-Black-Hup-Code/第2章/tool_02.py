"""
    一个tcp代理程序，可远程执行命令和上传文件
    该程序可充当客户端和服务器
"""

import sys
import socket
import getopt
import threading
import subprocess
import json
import platform
import os
import traceback


listen = False
command = False
upload = False
execute = ""
target_ip = ""
upload_destination = ""
port = 0
platform_version = platform.platform()
if platform_version.startswith("Windows"):
    encoding_code = "gb2312"
else:
    encoding_code = "utf-8"


def usage():
    print("Zheng Net Tool")
    print("")
    print("-t target_host -p port")
    print("-l --listen                - listen on [host]:[port] for incoming connections")
    print("-c --command               - initialize a command shell")
    print("")
    print("Examples:")
    print("python tool.py -l -t 192.168.0.108 -p 5555")
    print("python tool.py -t 192.168.0.108 -p 5555")
    sys.exit(0)


def main():
    global listen
    global port
    global target_ip

    if not len(sys.argv[1:]):
        usage()

    opts = ""
    # args = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hlt:p:",
        ["help", "listen", "target", "port"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    print(opts)
    # print(args)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-t", "--target"):
            target_ip = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            usage()
            assert False, "Unhandled Option"

    if not listen and len(target_ip) and port > 0:
        client_handler()

    if listen:
        server_loop()


def server_loop():
    global target_ip
    global port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 减少地址复用的时间
    server.bind((target_ip, port))

    server.listen(5)
    print("[*] Listening on %s:%d" % (target_ip, port))

    def handle_client(client_socket):
        try:
            system_msg = get_system_msg()
            client_socket.send(system_msg.encode("utf-8"))
            while True:
                response = client_socket.recv(1024)
                response = response.decode("utf-8")
                print("[*] Received: %s" % response)
                if 'exit' == response or 'bye' == response:
                    print("关闭连接")
                    break
                if response.startswith("file-up "):
                    print(response)
                    get_upload_file(client, response[20:20+int(response[8:10])], response[10:20], response[20+int(response[8:10]):])
                    result = (0, "upload ok!", None)
                else:
                    result = run_command(response)
                client_socket.send(json.dumps(result).encode("utf-8"))
        except Exception as e:
            print("[*] Exception! --> " + str(e))
            traceback.print_exc()
        finally:
            client_socket.close()

    while True:
        client, addr = server.accept()
        print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()


def client_handler():
    global target_ip
    global port
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target_ip, port))

        data = client.recv(4096)
        data = str(data, encoding="utf-8")
        print("system message")
        print(data)
        print("-" * 66)

        while True:
            while True:
                buffer = input(">").strip()
                if buffer != "":
                    break
                # print("can't send empty string!!")
            if buffer.startswith("file-up"):
                upload_file(client, buffer[buffer.index(" ")+1:])
            else:
                client.send(buffer.encode("utf-8"))
            if buffer == 'exit' or buffer == 'bye':
                print("关闭连接")
                client.close()
                break
            recv_len = 1
            response = b""
            while recv_len:
                # print("----loop recv----")
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            result = json.loads(str(response, encoding="utf-8"))
            # print(result)
            print("返回码：", result[0])
            print("标准输出：\n", result[1], end="")
            print("标准错误：", result[2])
            # print(result[1], end="")

    except Exception as e:
        print("[*] Exception! --> " + str(e))
        print(traceback.print_exc())
        client.close()


def run_command(command):
    # print(command)
    result = ("", "", "")
    try:
        if platform_version.startswith("Windows") and command.startswith("start "):
            os.system(command)
            print("[*] Result --> " + str(0))
            result = (str(0), str("execute command ok!\r\n"), str(None))
        else:
            res = subprocess.Popen(command.rstrip(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            sout, serr = res.communicate()
            print("[*] Result --> " + str(res.returncode))
            result = (str(res.returncode), str(sout, encoding=encoding_code), str(serr))
    except UnicodeDecodeError as e:
        result = (str(res.returncode), str(sout, encoding="utf-8"), str(serr))
    except Exception as e:
        print("Failed to execute command.\r\n" + str(e))
    finally:
        return result


def get_system_msg():
    msg = ""
    msg += "system ->    " + platform.platform() + "\n"
    msg += "bits ->      " + platform.architecture()[0] + " " + platform.architecture()[1] + "\n"
    msg += "machine ->   " + platform.machine() + "\n"
    msg += "node ->      " + platform.node() + "\n"
    msg += "processor -> " + platform.processor() + "\n"
    msg += "system ->    " + platform.system() + "\n"
    return msg


def upload_file(client, file_path):
    if os.path.exists(file_path):
        file_name = file_path[file_path.rindex("\\") + 1:]
        print(file_name)
        word = "file-up " + get_file_name_len(file_name) + get_file_size_len(file_path) + file_name
        print("word " + word)
        client.send(word.encode("utf-8"))
        with open(file_path, "rb") as f:
            while 1:
                data = f.read(4000)
                if not data:
                    break
                client.send(data)
    else:
        print("文件上传路径错误!! -> " + file_path)
        client.send("echo Error Path!".encode("utf-8"))


def get_upload_file(client, file_name, file_size, data):
    print("file_name = " + file_name)
    print("file_size = " + file_size)
    file_size = int(file_size)
    with open(file_name, "wb") as f:
        f.write(data.encode("utf-8"))
        while 1:
            if file_size > 4000:
                data = client.recv(4000)
                f.write(data)
                file_size -= 4000
            else:
                data = client.recv(file_size)
                f.write(data)
                break
    print("upload file success -> " + file_name)


def get_file_name_len(file_name):
    _len = len(file_name)
    if _len < 10:
        return "0" + str(_len)
    else:
        return str(_len)


def get_file_size_len(file_path):
    _len = os.path.getsize(file_path)
    if len(str(_len)) < 10:
        return "0"*(10-len(str(_len))) + str(_len)
    else:
        return str(_len)


if __name__ == '__main__':
    main()

    # result = run_command("start mspaint &")
    # print(result)
    # os.system("start mspaint")
    # print("-----------------")
    # get_system_msg()
    # a = get_file_size_len("C:\\Users\\libai\\PycharmProjects\\tf-learn\\black_hup\\tcp_proxy\\b.bat")
    # print(a)


