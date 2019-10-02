import sys
import socket
import threading
import getopt


def usage():
    print("Zheng Net Tool")
    print("")
    print("--lhost -->local_host  --lport -->local_port")
    print("--rhost -->remote_host --rport -->remote_port")
    print("")
    print("Examples:")
    print("python tcp_proxy.py --lhost=192.168.0.107 --lport=6666 --rhost=192.168.0.108 --rport=555")
    sys.exit(0)


def main():
    if not len(sys.argv[1:]):
        usage()

    opts = ""
    args = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h",
                                   ["help", "lhost=", "lport=", "rhost=", "rport=", "receive_first="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    print(opts)
    print(args)

    local_host = ""
    local_port = ""
    remote_host = ""
    remote_port = ""
    receive_first = ""

    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("--lhost", ):
            local_host = a
        elif o in ("--lport",):
            local_port = a
        elif o in ("--rhost",):
            remote_host = a
        elif o in ("--rport",):
            remote_port = a
        elif o in ("--receive_first",):
            receive_first = a
        else:
            assert False, "Unhandled Option"

    if len(local_host)<=0 or len(local_port)<=0 or len(remote_host)<=0 or len(remote_port)<=0 or len(receive_first)<=0:
        print("input option error")
        usage()
        assert False, "Option Error"

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 减少地址复用的时间
    except Exception as e:
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening socket or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" %(local_host, local_port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print("[==>] Received incoming connection from %s:%d" % (addr[0], addr[1]))
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        remote_buffer = response_handler(remote_buffer)
        if len(remote_buffer):
            print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print("[<==] Received %d bytes from localhost." % len(local_buffer))
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)

            remote_socket.send(local_buffer)
            print("[==>] Send to remote.")

        if len(remote_buffer):
            client_socket.send(remote_buffer)
            print("[==>] Send to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def hexdump(src, length=16):
    # result = []
    # digits = 4 if isinstance(src, unicode) else 2
    # for i in range(0, len(src), length):
    #     s = src[i:i+length]
    #     hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
    #     text = b''.join([x if 0x20 <= ord(x) < 0x7f else b'.' for x in s])
    #     result.append(b"%04x %-*s %s" %(i, length*(digits + 1), hexa, text))
    # print(b'\n'.join(result))
    print("hexdump function")


def receive_from(connection):
    buffer = b""
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        print(e)

    return buffer


def response_handler(buffer):
    return buffer


def request_handler(buffer):
    return buffer


if __name__ == '__main__':
    main()
