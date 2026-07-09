from scapy.all import *

print(getmacbyip("192.168.0.46"))
print(getmacbyip("192.168.0.1"))

packets = sniff(
    iface="eth6",
    filter="arp",
    count=5,
    prn=lambda p: p.summary()
)

print("done")