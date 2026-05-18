# DevBoard Homelab Ansible

Ansible control node: your laptop or workstation.

Managed node: the headless Ubuntu server at `192.168.0.46`.

Inventory alias: `homelab01`.

Inventory group: `homelab`.

## Prerequisites

- SSH access to `mike@192.168.0.46`
- `mike` can use `sudo`
- Passwordless SSH key login works
- Python 3 is installed on the Ubuntu server
- Ansible is installed on the control node
- Private key exists at `~/.ssh/homelab`

On Ubuntu control nodes:

```bash
sudo apt-get update
sudo apt-get install -y ansible
```

## Install Collections

Run from this directory:

```bash
cd infra/ansible
ansible-galaxy collection install -r collections/requirements.yml
```

From the repository root:

```bash
cd infra/ansible
ansible-galaxy collection install -r collections/requirements.yml
```

## Smoke Test

Run from this directory:

```bash
cd infra/ansible
ansible homelab -m ping
```

From the repository root:

```bash
cd infra/ansible
ansible homelab -m ping
```

## Playbooks

Ansible privilege escalation uses the remote `mike` sudo password, not a root password.

If `mike` still requires a sudo password, run the sudoers playbook once and enter `mike`'s remote sudo password:

```bash
cd infra/ansible
ansible-playbook playbooks/sudoers.yml --ask-become-pass
```

After that, the normal playbooks can escalate automatically:

```bash
cd infra/ansible
ansible-playbook playbooks/bootstrap.yml
ansible-playbook playbooks/ssh.yml
ansible-playbook playbooks/docker.yml
ansible-playbook playbooks/sysctl.yml
ansible-playbook playbooks/netplan.yml
ansible-playbook playbooks/stacks.yml
```

The Docker playbook configures Docker's official Ubuntu apt repository, installs
Docker Engine and the Compose v2 plugin, adds `mike` to the `docker` group, and
starts/enables the Docker service. A new SSH login session is required before
the updated Docker group membership applies to shell commands.

The sysctl playbook renders `/etc/sysctl.d/99-homelab.conf`, applies pending
kernel tuning, and validates the expected values.

The netplan playbook records the current network allocation and validates SSH
connectivity. The homelab server currently keeps Ubuntu netplan on DHCP, with a
router DHCP reservation for `192.168.0.46`, so Ansible does not overwrite or
apply netplan while `homelab_manage_netplan` is `false`.

The stacks playbook creates `/opt/stacks`, per-service Compose directories, and
`/opt/stacks/<service>/data` persistent data directories. Local backup staging
is `/var/backups/homelab-stacks`; S3 is the intended offsite target once backup
automation, encryption, bucket lifecycle, and least-privilege credentials are
configured.

The same stacks playbook deploys Portainer at `https://192.168.0.46:9443` using
`/opt/stacks/portainer/docker-compose.yml` and `/opt/stacks/portainer/data`.
Create the initial admin user in the Portainer web UI after the first deploy.

It also deploys Home Assistant at `http://192.168.0.46:8123` using host
networking for LAN discovery. Persistent Home Assistant config and state live in
`/opt/stacks/home-assistant/data`.

Run the full flow:

```bash
cd infra/ansible
ansible-playbook playbooks/site.yml
```
