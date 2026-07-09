import getpass
import select
import socket
import threading

import paramiko

SSH_HOST = '192.168.0.46'
SSH_PORT = 22
SSH_USER = 'selina'

REMOTE_BIND_PORT = 9092
LOCAL_HOST = 'localhost'
LOCAL_PORT = 8088

def forward_data(chan, local_sock):
    while True:
        r, _, _ = select.select([chan, local_sock], [], [])
        if chan in r:
            data = chan.recv(4096)
            if not data:
                break;
            local_sock.sendall(data)

        if local_sock in r:
            data = local_sock.recv(4096)
            if not data:
                break;
            chan.sendall(data)
    chan.close()
    local_sock.close()

def handle_channel(chan):
    try:
        local_sock = socket.create_connection((LOCAL_HOST, LOCAL_PORT))
    except Exception as e:
        print(f"[-] Cannot connect to local service {LOCAL_HOST}:{LOCAL_PORT}: {e}")
        chan.close()
        return
    
    print(f"[+] Forwarding Linux:{REMOTE_BIND_PORT} -> Windows:{LOCAL_HOST}:{LOCAL_PORT}")
    forward_data(chan, local_sock)

def main():
    password = getpass.getpass(f'Password for {SSH_USER}@{SSH_HOST}: ')

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=password)
    transport = client.get_transport()

    # Ensure transport is alive before requesting
    if not transport.is_active():
        raise RuntimeError("Transport is not active")

    # remote_bind_host = 'localhost'
    # transport.request_port_forward(remote_bind_host, REMOTE_BIND_PORT)

    print(f"[+] Reverse tunnel open:")
    print(f"    Linux box localhost:{REMOTE_BIND_PORT} -> Windows {LOCAL_HOST}:{LOCAL_PORT}")

    try:
        while True:
            chan = transport.accept(1000)
            if chan is None:
                continue
            t = threading.Thread(target=handle_channel, args=(chan,))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print('[+n] Closing tunnel')
        client.close()


if __name__ == "__main__":
    main()
