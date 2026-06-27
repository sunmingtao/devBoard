import sys
import socket
import threading

HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)]
)

def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()
    
    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])
        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f'{ord(c):02x}' for c in word])
        hexwidth = length * 3
        results.append(f'{i:04} {hexa:<{hexwidth}} {printable}')
    
    if show:
        for line in results:
            print(line)
    else:
        return results
    
def receive_from(connection):
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer

def request_handler(buffer):
    return buffer

def response_handler(buffer):
    return buffer

def forward(src, dst, direction, handler):
    while True:
        try:
            data = src.recv(4096)
            if not data:
                break

            print(f"[{direction}] {len(data)} bytes")
            hexdump(data)

            data = handler(data)

            if data:
                dst.sendall(data)

        except Exception as e:
            print(f"[{direction}] error: {e}")
            break

    try:
        src.close()
    except:
        pass

    try:
        dst.close()
    except:
        pass

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        data = remote_socket.recv(4096)
        if data:
            print(f"[<==] {len(data)} bytes from remote")
            hexdump(data)
            client_socket.sendall(response_handler(data))

    t1 = threading.Thread(
        target=forward,
        args=(client_socket, remote_socket, "client -> remote", request_handler)
    )

    t2 = threading.Thread(
        target=forward,
        args=(remote_socket, client_socket, "remote -> client", response_handler)
    )

    t1.start()
    t2.start()

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f'Problem on bind {e}')
        sys.exit(0)

    print(f"[*] Listening on {local_host}:{local_port}")
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        line = f'> Received incoming connection from {addr[0]}:{addr[1]}'
        print(line)
        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first)
        )
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: python proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive_first]")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
    
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()