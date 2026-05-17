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
ansible-playbook playbooks/stacks.yml
```

Run the full flow:

```bash
cd infra/ansible
ansible-playbook playbooks/site.yml
```
