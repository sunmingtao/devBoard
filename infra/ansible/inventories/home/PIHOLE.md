# Pi-hole

Pi-hole runs from `/opt/stacks/pihole` using Docker Compose.

## Access

- Admin URL: `http://192.168.0.46:8081/admin/`
- DNS server: `192.168.0.46`
- Container: `pihole`
- Image: `pihole/pihole:latest`
- Compose file: `/opt/stacks/pihole/docker-compose.yml`
- Persistent config: `/opt/stacks/pihole/etc-pihole`
- Dnsmasq config: `/opt/stacks/pihole/etc-dnsmasq.d`
- Web password file: `/opt/stacks/pihole/pihole-web-password.txt`

## Install

Run from the Ansible directory.

For the first install, pass a web UI password. The role writes it to a
server-local file that is not stored in Git:

```bash
cd infra/ansible
read -rsp "Pi-hole web password: " PIHOLE_WEB_PASSWORD
echo
ansible-playbook playbooks/pihole.yml \
  -e "pihole_web_password=${PIHOLE_WEB_PASSWORD}"
unset PIHOLE_WEB_PASSWORD
```

Future runs do not need `pihole_web_password` unless you want to rotate the
password:

```bash
cd infra/ansible
ansible-playbook playbooks/pihole.yml
```

## Reset Web Password

Set a new password through Ansible. When `pihole_web_password` is provided, the
role updates the local password file and runs Pi-hole's own password reset
command inside the container:

```bash
cd infra/ansible
read -rsp "New Pi-hole web password: " PIHOLE_WEB_PASSWORD
echo
ansible-playbook playbooks/pihole.yml \
  -e "pihole_web_password=${PIHOLE_WEB_PASSWORD}"
unset PIHOLE_WEB_PASSWORD
```

You can also reset it directly inside the running container:

```bash
docker exec -it pihole pihole setpassword
```

## Verify

Check the container and logs:

```bash
ssh mike@192.168.0.46
cd /opt/stacks/pihole
docker compose ps
docker compose logs -f
```

Check DNS before changing the router:

```bash
nslookup example.com 192.168.0.46
```

Open the admin UI:

```text
http://192.168.0.46:8081/admin/
```

## Enable Network-Wide DNS

After verification, update the router DHCP settings so LAN clients receive
`192.168.0.46` as their DNS server.

Keep the router's old DNS settings noted somewhere before changing them. If
anything goes wrong, set client/router DNS back to the previous resolver.

## Useful Commands

```bash
cd /opt/stacks/pihole
docker compose pull
docker compose up -d
docker compose logs -f
docker compose down
```

## Notes

- DNS binds to `192.168.0.46:53`, not `0.0.0.0:53`, to avoid fighting Ubuntu's
  local resolver on `127.0.0.53`.
- The web UI binds to `192.168.0.46:8081` to avoid port 80 conflicts.
- Pi-hole Docker v6 uses `FTLCONF_*` environment variables. This stack uses
  `WEBPASSWORD_FILE` so the web password lives in a local server file instead
  of the Compose file.

2026-05-23

Win+R certmgr.msc
