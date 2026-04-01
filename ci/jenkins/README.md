# Jenkins (DevOps Environment)

This directory contains the configuration to run a local Jenkins instance for the DevBoard project.

The Jenkins container is preconfigured with:

- Docker CLI
- Docker Compose (v2)
- Terraform
- AWS CLI

It is used for:
- CI/CD pipelines
- Terraform infrastructure provisioning
- Docker image build & deployment

---

## 📦 Prerequisites

Make sure the host machine has:

- Docker installed
- Docker Compose (v2) installed

Verify:

```
docker --version
docker compose version
docker compose up -d --build
```

Stop Jenkins:
```
docker compose down
```

Check tools
```
docker --version
docker compose version
terraform version
aws --version
git --version
```