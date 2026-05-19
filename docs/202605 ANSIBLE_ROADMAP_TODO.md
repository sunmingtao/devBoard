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
    sysctl.yml
    netplan.yml
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
- import_playbook: sysctl.yml
- import_playbook: netplan.yml
- import_playbook: stacks.yml
- import_playbook: devboard.yml
```

Suggested first phase only:

```bash
cd infra/ansible
ansible-playbook playbooks/bootstrap.yml
ansible-playbook playbooks/ssh.yml
ansible-playbook playbooks/docker.yml
ansible-playbook playbooks/sysctl.yml
ansible-playbook playbooks/netplan.yml
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

- [x] Install Docker.
- [x] Decide package source:
  - [x] Use the official Docker apt repository.
  - [x] Retire the short-term Ubuntu package `docker.io` plan.
- [x] Install Docker Compose plugin or standalone compose package.
- [x] Add `mike` to the `docker` group.
- [x] Enable Docker service.
- [x] Start Docker service.
- [x] Configure Docker daemon defaults if needed.
- [x] Verify `docker version`.
- [x] Verify `docker compose version`.
- [x] Document that group membership requires a new login session.

### Phase 4 - System Tuning

- [x] Create `/etc/sysctl.d/99-homelab.conf`.
- [x] Add sysctl settings required by the server.
- [x] Include current manual setting if still wanted:
  - [x] `kernel.dmesg_restrict = 0`
- [x] Apply sysctl config.
- [x] Validate expected sysctl values.

### Phase 5 - Network Configuration

- [x] Collect current netplan config from the server.
- [x] Decide static IP vs DHCP reservation.
  - [x] Use router DHCP reservation for `192.168.0.46`.
- [x] If static IP is managed by router DHCP reservation, do not overwrite netplan.
- [x] If static IP is managed on Ubuntu, template netplan carefully.
  - [x] Keep Ubuntu-side netplan rendering gated behind `homelab_manage_netplan: false`.
- [x] Configure DNS servers.
  - [x] DNS is currently provided by router DHCP: `192.168.0.1`.
- [x] Configure gateway.
  - [x] Gateway is currently provided by router DHCP: `192.168.0.1`.
- [x] Apply netplan with a safe rollback strategy.
  - [x] Skip netplan apply while router DHCP reservation is the source of truth.
- [x] Validate SSH connectivity after network changes.
- [x] Document MAC address and IP allocation.

### Phase 6 - Filesystem and Stack Directories

- [x] Create `/opt/stacks`.
- [x] Create `/opt/stacks/portainer`.
- [x] Create `/opt/stacks/home-assistant`.
- [x] Create `/opt/stacks/devboard`.
- [x] Set ownership and permissions.
- [x] Decide persistent data location:
  - [x] `/opt/stacks/<service>/data`
  - [x] Do not use `/var/lib/<service>` for first homelab pass.
- [x] Decide backup location.
  - [x] Local staging: `/var/backups/homelab-stacks`.
  - [x] Offsite target: S3 after backup automation, encryption, bucket, and IAM are configured.
- [x] Add backup TODOs for Docker volumes.

### Phase 7 - Portainer Deployment

- [x] Create Portainer persistent data directory.
  - [x] Use `/opt/stacks/portainer/data` instead of a named Docker volume.
- [x] Template `/opt/stacks/portainer/docker-compose.yml`.
- [x] Deploy Portainer using Docker Compose.
- [x] Enable restart policy.
- [x] Expose Portainer on a chosen port, usually `9443`.
- [x] Verify container health.
- [x] Verify web UI is reachable.
- [x] Document initial admin setup.

Suggested compose shape:

```yaml
services:
  portainer:
    image: portainer/portainer-ce:lts
    container_name: portainer
    restart: unless-stopped
    ports:
      - "9443:9443"
      - "9000:9000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./data:/data
```

### Phase 8 - Home Assistant Deployment

- [x] Decide whether Home Assistant should use host networking.
  - [x] Use `network_mode: host` for LAN discovery integrations.
- [x] Create `/opt/stacks/home-assistant/docker-compose.yml`.
- [x] Create persistent config directory.
  - [x] Use `/opt/stacks/home-assistant/data`.
- [x] Deploy container.
- [x] Confirm discovery/network requirements.
  - [x] Enable host networking and `NET_ADMIN`/`NET_RAW` capabilities.
- [x] Verify web UI.
- [x] Add backup task for config directory.
  - [x] Include `/opt/stacks/home-assistant/data` in the stack backup plan.

### Phase 9 - Multi-Environment DevBoard GitOps Planning

- [x] Define target environments:
  - [x] `local`: Minikube on laptop, manual/local-only, not managed by Ansible.
  - [x] `dev`: k3s on Ubuntu homelab, managed by Ansible and Argo CD.
  - [x] `prod`: k3s on Ubuntu homelab, managed by Ansible and Argo CD.
  - [x] `cloud`: AWS EKS, managed by Terraform, not always online due to cost.
- [x] Define deployment policy:
  - [x] Push to `main` triggers dev deployment automatically through GitHub Actions.
  - [x] Prod deployment requires manual approval.
  - [x] Cloud/EKS deployment is explicit/on-demand because the cluster may be offline.
- [x] Decide branch and promotion model:
  - [x] Confirm the canonical branch is `main`.
  - [x] Dev tracks every `main` push by committing image tags to a dev overlay.
  - [x] Prod promotion uses a protected GitHub Actions `prod` environment with required manual approval.
  - [x] Prod Argo CD auto-syncs after the approved prod manifest change lands in Git.
  - [x] Configure the repository environment named `prod` in GitHub with required reviewers; the promotion job should target `environment: prod`, wait for approval, then write the already-built immutable image tag into the prod overlay.
- [x] Define Kubernetes overlay layout:
  - [x] Keep `deploy/k8s/overlays/local` for laptop Minikube.
  - [x] Add `deploy/k8s/overlays/dev-k3s`.
  - [x] Add `deploy/k8s/overlays/prod-k3s`.
  - [x] Keep `deploy/k8s/overlays/eks` for AWS EKS.
  - [x] Share common manifests from `deploy/k8s/base`.
- [x] Define Argo CD app layout:
  - [x] Keep local Minikube apps separate from Ansible-managed k3s apps.
  - [x] Add `deploy/gitops/apps/k3s/devboard-dev.yaml`.
  - [x] Add `deploy/gitops/apps/k3s/devboard-prod.yaml`.
  - [x] Add k3s-specific app manifests for Argo Rollouts, External Secrets, ingress-nginx, Kafka, and optional monitoring.
  - [x] Keep EKS app manifests for cloud deployment.
- [x] Define k3s namespace and isolation model:
  - [x] Use separate namespaces `devboard-dev` and `devboard-prod`.
  - [x] Use separate MySQL PVCs and credentials per environment.
  - [x] Use separate Kafka topics and Kafka releases per environment.
  - [x] Use separate ingress hosts for dev and prod.
- [x] Add Ansible support for k3s:
  - [x] Create `playbooks/k3s.yml`.
  - [x] Create `roles/k3s`.
  - [x] Install single-node k3s on the Ubuntu server.
  - [x] Disable bundled k3s Traefik so repo-managed ingress-nginx is the ingress controller.
  - [x] Keep k3s local-path storage as the first storage class.
  - [x] Copy kubeconfig for the `mike` user.
  - [x] Validate `kubectl get nodes`.
- [x] Add Ansible support for Argo CD bootstrap:
  - [x] Create `playbooks/argocd.yml`.
  - [x] Create `roles/argocd`.
  - [x] Install Argo CD from `deploy/gitops/argocd`.
  - [x] Wait for Argo CD pods and CRDs.
  - [x] Bootstrap the k3s dev/prod Argo CD applications after these manifests are available on GitHub `main`.
  - [x] Document initial admin password retrieval and password rotation.
  - [x] Decide whether Argo CD UI is accessed by port-forward, NodePort, or ingress.
    - [x] Use port-forward for the first k3s homelab pass; consider ingress later after TLS and access controls are decided.
- [ ] Define GitHub Actions deployment workflow:
  - [ ] Build backend, frontend, event service, and event frontend images.
  - [ ] Push images to the chosen registry.
  - [x] Update dev k3s manifests automatically after successful `main` build.
  - [ ] Add a protected `prod` GitHub Actions environment with required manual approval.
  - [ ] Promote an already-built image tag to prod instead of rebuilding a different artifact.
  - [ ] Keep cloud/EKS deploy as a separate manual workflow.
- [ ] Define image registry and tag strategy:
  - [ ] Decide between Docker Hub and GHCR for homelab images.
  - [ ] Use immutable image tags for dev/prod promotion.
  - [ ] Avoid deploying `latest` to prod.
  - [ ] Decide how image tags are written back into GitOps overlays.
- [ ] Define secrets handling by environment:
  - [ ] Use External Secrets local Fake generator only for local/dev demos.
  - [ ] Choose real k3s dev/prod secret management: SOPS, Ansible Vault, sealed-secrets, or External Secrets provider.
  - [ ] Keep prod secrets separate from dev secrets.
  - [ ] Remove or avoid committing real credentials.
- [ ] Define ingress and DNS:
  - [ ] Decide local laptop hostname for Minikube, such as `devboard.local`.
  - [ ] Decide k3s dev hostname, such as `dev.devboard.local`.
  - [ ] Decide k3s prod hostname, such as `prod.devboard.local`.
  - [ ] Add LAN DNS or `/etc/hosts` entries pointing k3s hostnames to `192.168.0.46`.
  - [ ] Confirm ingress-nginx NodePorts `30080` and `30443`, or switch to host ports/LoadBalancer strategy.
  - [ ] Confirm backend CORS origins include the final dev/prod URLs.
- [ ] Define persistent data and backups:
  - [ ] MySQL PVC per environment.
  - [ ] Kafka persistence decision per environment.
  - [ ] Include k3s state and application PVCs in backup planning.
  - [ ] Document restore order: k3s, Argo CD, GitOps apps, persistent data.
- [ ] Define validation and health checks:
  - [ ] Validate Argo CD applications are `Synced` and `Healthy`.
  - [ ] Validate Rollout `devboard-backend` in dev and prod.
  - [ ] Validate frontend, backend, event service, MySQL, and Kafka pods per namespace.
  - [ ] Validate dev and prod ingress URLs.
- [ ] Plan Jenkins migration to Ubuntu:
  - [ ] Decide whether Jenkins runs as Docker Compose under `/opt/stacks/jenkins` or as a k3s workload.
  - [ ] Prefer Docker Compose for first migration unless Jenkins itself needs Kubernetes agents immediately.
  - [ ] Move Jenkins data from laptop to Ubuntu.
  - [ ] Configure Jenkins access, backup, and plugin state.
  - [ ] Decide Jenkins role after GitHub Actions becomes primary deployment automation.

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
  - [x] `sysctl`
  - [x] `netplan`
  - [x] `stacks`
  - [x] `portainer`
  - [x] `home_assistant`
  - [x] `k3s`
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
- [x] Implement `docker` role:
  - [x] configure the official Docker apt repository
  - [x] install `docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin`, `docker-compose-plugin`
  - [x] add `mike` to `docker` group
  - [x] enable Docker service
  - [x] start Docker service
- [x] Implement `stacks` role:
  - [x] create `/opt/stacks`
  - [x] create service directories
  - [x] create persistent data directories
  - [x] create local backup staging directory
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
  - docker-ce
  - docker-ce-cli
  - containerd.io
  - docker-buildx-plugin
  - docker-compose-plugin

homelab_sysctl_settings:
  kernel.dmesg_restrict: 0

homelab_manage_netplan: false
homelab_network_allocation_method: router_dhcp_reservation
homelab_network_primary_interface: wlp2s0
homelab_network_reserved_ipv4: 192.168.0.46
homelab_network_prefix: 24
homelab_network_gateway: 192.168.0.1
homelab_network_mac_address: a8:a0:92:de:ad:ad
homelab_network_dns_servers:
  - 192.168.0.1

stacks_root: /opt/stacks
stacks_backup_root: /var/backups/homelab-stacks
stacks_backup_offsite_provider: s3
stacks_backup_offsite_target: ""

portainer_dir: /opt/stacks/portainer
portainer_image: portainer/portainer-ce:lts
portainer_http_port: 9000
portainer_https_port: 9443
```

## Useful Tags

```bash
cd infra/ansible
ansible-playbook playbooks/site.yml --tags common
ansible-playbook playbooks/site.yml --tags docker
ansible-playbook playbooks/site.yml --tags sysctl
ansible-playbook playbooks/site.yml --tags netplan
ansible-playbook playbooks/site.yml --tags stacks
ansible-playbook playbooks/site.yml --tags portainer
ansible-playbook playbooks/site.yml --tags k3s
```
