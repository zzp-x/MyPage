"""
    一个小客户端

"""

import socket
import subprocess


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        if len(buffer):
            client.send(buffer)

        while True:
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break
            print(response)

            buffer = input(">")
            buffer += "\n"

            client.send(buffer.encode("utf-8"))
    except Exception as e:
        print("[*] Exception! --> " + str(e))
        client.close()


def run_command(command):
    command = command.rstrip()
    try:

        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except Exception as e:
        print("Failed to execute command.\r\n")

    return output

