### 2026-05-17

```bash
sudo apt install docker.io -y

sudo usermod -aG docker $USER
newgrp docker

sudo vi /etc/sysctl.d/99-dmesg.conf
# kernel.dmesg_restrict = 0

sudo sysctl --system

dmesg -K

sudo vgdisplay
lsblk

sudo lvextend -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv
sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv
```

### 2026-05-18

```
sudo apt-get install -y ansible
cd infra/ansible
ansible-galaxy collection install -r collections/requirements.yml
ansible homelab -m ping

sudo vi /etc/sudoers.d/90-mike-ansible
  # mike ALL=(ALL) NOPASSWD:ALL

# Effective ssh config
sshd -T | egrep '^(pubkeyauthentication|permitrootlogin|passwordauthentication|kbdinteractiveauthentication)'

# Only run selected tags
ansible-playbook playbooks/bootstrap.yml --tags locale
```