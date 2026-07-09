import socket
import ipaddress

SUBNET = '192.168.0.0/24'
PORTS = [22, 80, 135, 139, 445, 3389]

for ip in ipaddress.ip_network(SUBNET).hosts():
    for port in PORTS:
        s = socket.socket()
        s.settimeout(0.5)
        try:
            print(f'Scanning {ip}:{port}')
            s.connect((str(ip), port))
            print(f'Host up: {ip}, open port: {port}')
            break
        except:
            pass
        finally:
            s.close()

for port in PORTS:
    s = socket.socket()
    s.settimeout(1)
    try:
        print(f'Scanning {port}')
        s.connect(('192.168.0.46', port))
        print(f'Host up open port: {port}')
    except:
        print(f'Port {port} is closed')
    finally:
        s.close()