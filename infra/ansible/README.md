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
ansible-playbook playbooks/k3s.yml
ansible-playbook playbooks/argocd.yml
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

The k3s playbook installs a single-node k3s cluster, disables bundled Traefik so
repo-managed ingress-nginx can own ingress later, keeps the default `local-path`
storage class, copies kubeconfig to `mike` at `~/.kube/config`, and validates
`kubectl get nodes`. It also sets `/etc/rancher/k3s/k3s.yaml` to `root:mike`
with mode `0640` so `mike` can run the k3s-provided `kubectl` without exporting
`KUBECONFIG`.

The Argo CD playbook installs Argo CD from `deploy/gitops/argocd`, waits for the
Argo CD CRDs and pods, and keeps UI access on port-forward for the first k3s
pass:

```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

That command binds to localhost on the machine where it runs. From a laptop,
prefer an SSH tunnel instead of exposing Argo CD on the LAN:

```bash
ssh -t -L 8080:127.0.0.1:8080 mike@192.168.0.46 \
  'kubectl -n argocd port-forward svc/argocd-server 8080:443'
```

Open `https://localhost:8080` on the laptop. Retrieve the initial admin password with:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
```

Rotate the admin password after first login. The playbook copies the k3s Argo CD
application manifests to the host, but does not apply them by default because
those applications read from GitHub `main`; enable app bootstrap only after the
k3s overlay and app manifests are available on that branch:

```bash
ansible-playbook playbooks/argocd.yml -e argocd_bootstrap_k3s_apps=true
```

Run the full flow:

```bash
cd infra/ansible
ansible-playbook playbooks/site.yml
```
