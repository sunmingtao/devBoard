# Homelab Docker Stacks

Docker Compose services live under `/opt/stacks`. Each service gets a dedicated
directory for its Compose file and a local `data/` directory for persistent
bind-mounted state.

## Layout

```text
/opt/stacks/
  portainer/
    data/
  home-assistant/
    data/
  devboard/
    data/
```

## Backup Plan

- Persistent data source: `/opt/stacks/<service>/data`
- Local backup staging: `/var/backups/homelab-stacks`
- Offsite target: S3, to be configured when backup automation is added

S3 is a good offsite location for this homelab because it is durable, cheap for
small backups, and separate from the server. Keep a local staging directory for
quick restores and push encrypted backup archives to S3 later.

## Backup TODOs

- Add a script or Ansible role to stop/quiet services that need consistent
  backups.
- Archive `/opt/stacks/<service>/data` into `/var/backups/homelab-stacks`.
- Encrypt archives before offsite upload.
- Create an S3 bucket, lifecycle policy, and least-privilege upload credential.
- Add restore steps and test a restore before relying on the backups.
