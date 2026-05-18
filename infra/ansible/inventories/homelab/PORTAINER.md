# Portainer

Portainer runs from `/opt/stacks/portainer` using Docker Compose.

## Access

- URL: `https://192.168.0.46:9443`
- Container: `portainer`
- Image: `portainer/portainer-ce:lts`
- Compose file: `/opt/stacks/portainer/docker-compose.yml`
- Persistent data: `/opt/stacks/portainer/data`

## Initial Setup

After the first deployment, open the Portainer URL and create the initial admin
user in the web UI.

The deployment bind-mounts `/var/run/docker.sock`, so Portainer can manage the
local Docker engine after the admin account is created.

## Useful Commands

```bash
cd /opt/stacks/portainer
docker compose ps
docker compose logs -f
docker compose up -d
```
