# Home Assistant

Home Assistant runs from `/opt/stacks/home-assistant` using Docker Compose.

## Access

- URL: `http://192.168.0.46:8123`
- Container: `homeassistant`
- Image: `ghcr.io/home-assistant/home-assistant:stable`
- Compose file: `/opt/stacks/home-assistant/docker-compose.yml`
- Persistent config/data: `/opt/stacks/home-assistant/data`

## Network Decision

Home Assistant uses `network_mode: host`.

This is intentional for smart-home discovery. Host networking gives Home
Assistant direct access to LAN discovery protocols such as mDNS, SSDP, UPnP,
HomeKit, Chromecast, and similar integrations.

## Backup

Back up `/opt/stacks/home-assistant/data`. This directory contains the Home
Assistant configuration and runtime state. It is included in the homelab stack
backup plan documented in `STACKS.md`.

## Useful Commands

```bash
cd /opt/stacks/home-assistant
docker compose ps
docker compose logs -f
docker compose up -d
```
