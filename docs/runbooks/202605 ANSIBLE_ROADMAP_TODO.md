# Homelab Ansible Roadmap

Target host:

```ini
[homelab]
homelab01 ansible_host=192.168.0.46 ansible_user=mike ansible_ssh_private_key_file=~/.ssh/homelab
```

Long-term goal: deploy DevBoard on a headless Ubuntu 22.04 server.

Short-term goal: use Ansible to provision the server foundation first, then layer Docker services on top.

## Recommended Folder Structure

Use `infra/ansible` because this is infrastructure provisioning, parallel to the existing Terraform layout.

```text
infra/ansible/
  ansible.cfg
  inventories/
    homelab/
      hosts.ini
      group_vars/
        all.yml
      host_vars/
        homelab.yml
  playbooks/
    site.yml
    bootstrap.yml
    docker.yml
    stacks.yml
    devboard.yml
  roles/
    common/
      tasks/main.yml
      handlers/main.yml
      defaults/main.yml
    hostname/
      tasks/main.yml
      defaults/main.yml
    timezone/
      tasks/main.yml
      defaults/main.yml
    locale/
      tasks/main.yml
      defaults/main.yml
    ssh/
      tasks/main.yml
      handlers/main.yml
      templates/sshd_config.j2
      defaults/main.yml
    docker/
      tasks/main.yml
      handlers/main.yml
      defaults/main.yml
    sysctl/
      tasks/main.yml
      templates/99-homelab.conf.j2
      defaults/main.yml
    netplan/
      tasks/main.yml
      templates/01-homelab.yaml.j2
      defaults/main.yml
    stacks/
      tasks/main.yml
      defaults/main.yml
    portainer/
      tasks/main.yml
      templates/docker-compose.yml.j2
      defaults/main.yml
    home_assistant/
      tasks/main.yml
      templates/docker-compose.yml.j2
      defaults/main.yml
    devboard/
      tasks/main.yml
      templates/docker-compose.yml.j2
      templates/.env.j2
      defaults/main.yml
  files/
    ssh/
      authorized_keys/
  templates/
  collections/
    requirements.yml
  requirements.yml
  README.md
```

Optional later split if this grows:

```text
infra/ansible/
  inventories/dev/
  inventories/homelab/
  inventories/prod/
```

## Execution Model

Main entry point:

```bash
cd infra/ansible
ansible-playbook playbooks/site.yml --ask-become-pass
```

Suggested playbook flow:

```yaml
# playbooks/site.yml
- import_playbook: bootstrap.yml
- import_playbook: ssh.yml
- import_playbook: docker.yml
- import_playbook: stacks.yml
- import_playbook: devboard.yml
```

Suggested first phase only:

```bash
cd infra/ansible
ansible-playbook playbooks/bootstrap.yml
ansible-playbook playbooks/ssh.yml
ansible-playbook playbooks/docker.yml
ansible-playbook playbooks/stacks.yml
```

If `mike` still uses passworded sudo, configure passwordless automation sudo once:

```bash
cd infra/ansible
ansible-playbook playbooks/sudoers.yml --ask-become-pass
```

## Comprehensive TODO

### Phase 0 - Control Machine Prep

- [x] Install Ansible on the machine that will run automation.
- [x] Confirm SSH access to `mike@192.168.0.46`.
- [x] Confirm `mike` can use `sudo`.
- [x] Add an SSH key for passwordless login.
- [x] Create `infra/ansible` folder structure.
- [x] Add `ansible.cfg`.
- [x] Add homelab inventory.
- [x] Add `group_vars/all.yml` for shared variables.
- [x] Add `host_vars/homelab01.yml` for machine-specific values.
- [x] Add `collections/requirements.yml`.
- [x] Install required collections with `ansible-galaxy collection install -r infra/ansible/collections/requirements.yml`.
- [x] Optionally configure passwordless sudo for `mike` with `playbooks/sudoers.yml`.

### Phase 1 - First Pass Server Bootstrap

- [x] Run `apt update`.
- [x] Run safe package upgrade.
- [x] Install common packages:
  - [x] `vim`
  - [x] `curl`
  - [x] `git`
  - [x] `htop`
  - [x] `net-tools`
  - [x] `ca-certificates`
  - [x] `gnupg`
  - [x] `lsb-release`
  - [x] `ufw`
  - [x] `unzip`
  - [x] `tree`
- [x] Configure hostname.
- [x] Configure timezone.
- [x] Configure locale if needed.
- [x] Configure `/etc/hosts` entry for the server hostname.
- [x] Enable unattended security upgrades if desired.
- [x] Reboot only when required.
- [x] Add a validation task that confirms the host is reachable after reboot.

### Phase 2 - SSH Hardening

- [x] Back up current SSH config before changing it.
- [x] Install authorized SSH key for `mike`.
- [x] Disable root SSH login.
- [x] Disable password SSH login after key auth is confirmed.
- [x] Set `PubkeyAuthentication yes`.
- [x] Set `PermitRootLogin no`.
- [x] Set `PasswordAuthentication no` only after key auth is tested.
- [x] Restart SSH through a handler.
- [x] Keep a rollback path or temporary console access before hardening.

### Phase 3 - Docker Foundation

- [ ] Install Docker.
- [ ] Decide package source:
  - [ ] Short-term: use Ubuntu package `docker.io`.
  - [ ] Later: switch to official Docker apt repository if newer Docker is needed.
- [ ] Install Docker Compose plugin or standalone compose package.
- [ ] Add `mike` to the `docker` group.
- [ ] Enable Docker service.
- [ ] Start Docker service.
- [ ] Configure Docker daemon defaults if needed.
- [ ] Verify `docker version`.
- [ ] Verify `docker compose version`.
- [ ] Document that group membership requires a new login session.

### Phase 4 - System Tuning

- [ ] Create `/etc/sysctl.d/99-homelab.conf`.
- [ ] Add sysctl settings required by the server.
- [ ] Include current manual setting if still wanted:
  - [ ] `kernel.dmesg_restrict = 0`
- [ ] Apply sysctl config.
- [ ] Validate expected sysctl values.
- [ ] Decide whether `dmesg` should remain readable by non-root users long term.

### Phase 5 - Network Configuration

- [ ] Collect current netplan config from the server.
- [ ] Decide static IP vs DHCP reservation.
- [ ] If static IP is managed by router DHCP reservation, do not overwrite netplan.
- [ ] If static IP is managed on Ubuntu, template netplan carefully.
- [ ] Configure DNS servers.
- [ ] Configure gateway.
- [ ] Apply netplan with a safe rollback strategy.
- [ ] Validate SSH connectivity after network changes.
- [ ] Document MAC address and IP allocation.

### Phase 6 - Filesystem and Stack Directories

- [ ] Create `/opt/stacks`.
- [ ] Create `/opt/stacks/portainer`.
- [ ] Create `/opt/stacks/home-assistant`.
- [ ] Create `/opt/stacks/devboard`.
- [ ] Set ownership and permissions.
- [ ] Decide persistent data location:
  - [ ] `/opt/stacks/<service>/data`
  - [ ] or `/var/lib/<service>`
- [ ] Decide backup location.
- [ ] Add backup TODOs for Docker volumes.

### Phase 7 - Portainer Deployment

- [ ] Create Portainer Docker volume.
- [ ] Template `/opt/stacks/portainer/docker-compose.yml`.
- [ ] Deploy Portainer using Docker Compose.
- [ ] Enable restart policy.
- [ ] Expose Portainer on a chosen port, usually `9443`.
- [ ] Verify container health.
- [ ] Verify web UI is reachable.
- [ ] Document initial admin setup.

Suggested compose shape:

```yaml
services:
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: unless-stopped
    ports:
      - "9443:9443"
      - "9000:9000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data

volumes:
  portainer_data:
```

### Phase 8 - Home Assistant Deployment

- [ ] Decide whether Home Assistant should use host networking.
- [ ] Create `/opt/stacks/home-assistant/docker-compose.yml`.
- [ ] Create persistent config directory.
- [ ] Deploy container.
- [ ] Confirm discovery/network requirements.
- [ ] Verify web UI.
- [ ] Add backup task for config directory.

### Phase 9 - DevBoard Deployment Planning

- [ ] Decide deployment target:
  - [ ] Docker Compose on the single Ubuntu server.
  - [ ] K3s/microk8s on the Ubuntu server.
  - [ ] Existing Kubernetes manifests adapted to local cluster.
- [ ] For first homelab version, prefer Docker Compose unless Kubernetes is explicitly required.
- [ ] Review existing `deploy/single-vm` compose files.
- [ ] Define required services:
  - [ ] backend
  - [ ] frontend
  - [ ] event service
  - [ ] database
  - [ ] Kafka or alternative event broker
  - [ ] observability if desired
- [ ] Define image build/pull strategy.
- [ ] Define environment variables.
- [ ] Define secrets handling.
- [ ] Define persistent data volumes.
- [ ] Define ingress/reverse proxy plan.
- [ ] Define DNS name or local hostname.
- [ ] Add health checks.
- [ ] Add backup/restore steps.

### Phase 10 - Security and Operations

- [ ] Configure firewall with UFW.
- [ ] Allow SSH.
- [ ] Allow Portainer port only from trusted LAN if possible.
- [ ] Allow Home Assistant port if deployed.
- [ ] Allow DevBoard ports or reverse proxy ports.
- [ ] Consider fail2ban.
- [ ] Add Docker log rotation.
- [ ] Add basic monitoring.
- [ ] Add disk usage alerts.
- [ ] Add backup automation.
- [ ] Add restore test checklist.
- [ ] Document how to re-run playbooks safely.

### Phase 11 - Quality Checks

- [ ] Add `ansible-lint`.
- [ ] Add YAML formatting checks.
- [ ] Make playbooks idempotent.
- [ ] Test first run on a disposable VM if possible.
- [ ] Test second run makes no unexpected changes.
- [ ] Add tags:
  - [ ] `common`
  - [ ] `ssh`
  - [ ] `docker`
  - [ ] `sysctl`
  - [ ] `netplan`
  - [ ] `portainer`
  - [ ] `home_assistant`
  - [ ] `devboard`
- [ ] Add README usage examples.

## First Phase Implementation Checklist

This is the immediate scope from the rough plan.

- [ ] Create inventory:

```ini
[homelab]
homelab01 ansible_host=192.168.0.46 ansible_user=mike ansible_ssh_private_key_file=~/.ssh/homelab
```

- [ ] Create `playbooks/bootstrap.yml`.
- [ ] Create `playbooks/docker.yml`.
- [ ] Create `playbooks/stacks.yml`.
- [ ] Implement `common` role:
  - [ ] apt update
  - [ ] apt upgrade
  - [ ] install `vim`, `curl`, `git`, `htop`, `net-tools`
- [ ] Implement `docker` role:
  - [ ] install `docker.io`
  - [ ] add `mike` to `docker` group
  - [ ] enable Docker service
  - [ ] start Docker service
- [ ] Implement `stacks` role:
  - [ ] create `/opt/stacks`
- [ ] Implement `portainer` role:
  - [ ] create `/opt/stacks/portainer`
  - [ ] render `docker-compose.yml`
  - [ ] run `docker compose up -d`
  - [ ] verify the `portainer` container is running

## Suggested Variables

```yaml
homelab_hostname: homelab
homelab_timezone: Australia/Sydney
homelab_admin_user: mike

common_packages:
  - vim
  - curl
  - git
  - htop
  - net-tools
  - ca-certificates
  - gnupg
  - lsb-release
  - ufw
  - unzip
  - tree

docker_packages:
  - docker.io

stacks_root: /opt/stacks

portainer_dir: /opt/stacks/portainer
portainer_http_port: 9000
portainer_https_port: 9443
```

## Useful Tags

```bash
cd infra/ansible
ansible-playbook playbooks/site.yml --tags common
ansible-playbook playbooks/site.yml --tags docker
ansible-playbook playbooks/site.yml --tags portainer
```
