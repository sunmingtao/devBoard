import socket

target_host = "0.0.0.0"
target_port = 9997

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((target_host, target_port))

print(f"listening on {target_port} in host {target_host}")
while True:
    data, addr = server.recvfrom(4096)
    print(data, addr)
    server.sendto(b"ok", addr)