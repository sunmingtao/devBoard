# Jenkins (DevOps Environment)

This directory contains the configuration to run a local Jenkins instance for the DevBoard project.

The Jenkins container is preconfigured with:

- Docker CLI
- Docker Compose (v2)
- Terraform
- AWS CLI
- Trivy

It is used for:
- CI/CD pipelines
- Terraform infrastructure provisioning
- Docker image build & deployment
- Container image vulnerability scanning

The EKS build pipeline scans backend, frontend, event-service, and event-frontend
images with Trivy after local image builds and before Docker Hub pushes. The
pipeline fails on HIGH or CRITICAL vulnerabilities and archives JSON reports from
`trivy-reports/*.json`.

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
trivy --version
```

Run a local image scan:

```
trivy image --scanners vuln --severity HIGH,CRITICAL --exit-code 1 <image>:<tag>
```
