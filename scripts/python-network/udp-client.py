import socket
target_host = "192.168.0.46"
target_port = 9997

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto(b"AAABBBCCC", (target_host, target_port))

print(f'clinet sockname {client.getsockname()}')

data, addr = client.recvfrom(4096)

print (data.decode())
client.close()