# Homelab Network Allocation

The homelab server keeps Ubuntu netplan on DHCP. The stable server address is
managed by a router DHCP reservation, so Ansible should not overwrite netplan
unless `homelab_manage_netplan` is explicitly changed to `true`.

## Current Allocation

- Host: `homelab01`
- Reserved IPv4: `192.168.0.46/24`
- Gateway: `192.168.0.1`
- DNS: `192.168.0.1`
- Primary interface: `wlp2s0`
- Wi-Fi MAC address: `a8:a0:92:de:ad:ad`
- Ethernet interface: `enp1s0`
- Ethernet MAC address: `68:1d:ef:5e:98:37`
- Current netplan source: `/etc/netplan/50-cloud-init.yaml`

## Operating Notes

- Keep the router reservation for `a8:a0:92:de:ad:ad` mapped to
  `192.168.0.46`.
- Leave `/etc/netplan/50-cloud-init.yaml` as the active netplan source while
  using router-managed DHCP reservation.
- Do not commit Wi-Fi credentials from the live netplan file into this
  repository.
