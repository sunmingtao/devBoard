# DevBoard

DevBoard is a full-stack task board application with a Spring Boot backend, a Vue 3 frontend, an event-service, and deployment assets for Docker Compose, Jenkins, Terraform, Kubernetes, and Argo CD.

## Tech stack

- **Frontend:** Vue 3 + Vite + Vue Router (`apps/frontend`)
- **Backend:** Spring Boot 3.3 (Java 25), Spring Security, JWT, JPA (`apps/backend`)
- **Eventing:** Kafka-backed event-service (`apps/event-service`)
- **Data stores:** H2 (dev/test), MySQL/RDS, Redis-ready config
- **Infra/Deploy:** Docker Compose, Kubernetes/Kustomize, Terraform, Jenkins, Trivy, Argo CD, AWS EKS/ALB/RDS

## Repository layout

```text
.
├── apps/
│   ├── backend/        # Spring Boot API
│   ├── event-service/  # Kafka consumer service
│   └── frontend/       # Vue SPA
├── deploy/
│   ├── docker-compose/single-vm/
│   ├── gitops/
│   └── k8s/
├── ci/jenkins/
├── infra/terraform/
└── docs/
```

## EKS GitOps delivery

The EKS delivery path now follows a GitOps ownership model:

1. A commit to `main` is detected by the Jenkins EKS build job through SCM polling.
2. Jenkins builds backend, frontend, event-service, and event-frontend Docker images tagged with the Git short SHA.
3. Jenkins scans the images with Trivy and fails the build before push if HIGH or CRITICAL vulnerabilities are detected.
4. Jenkins pushes the verified images, updates `deploy/k8s/overlays/eks/kustomization.yaml` with the new immutable image tag, and pushes a `[skip ci]` GitOps commit.
5. Argo CD watches the EKS overlay and reconciles the cluster to the new desired state.

In short: Jenkins produces and verifies artifacts; Argo CD owns deployment reconciliation.

## Observability and alerting

DevBoard includes a Kubernetes observability stack under `deploy/observability`:

- Prometheus and Grafana from `kube-prometheus-stack`
- Kafka exporter metrics and a Kafka lag dashboard
- ServiceMonitors for backend and event-service Spring Boot Actuator metrics
- Alertmanager with a local/demo `demo-null` receiver
- DevBoard-specific PrometheusRule alerts for app availability, pod restarts, resource pressure, Kafka health, backend HTTP errors, latency, actuator scraping, and service health failures
- Optional Gmail SMTP notifications for `DevBoard.*` alerts using a Kubernetes Secret-mounted Google App Password

The alert routing is intentionally split: default kube-prometheus-stack platform alerts stay on `demo-null`, while DevBoard application alerts can be routed to email. This keeps interview demos focused on application signals instead of noisy control-plane scrape alerts.

Useful docs:

- Local observability: `deploy/observability/local/README.md`
- EKS observability: `deploy/observability/eks/README.md`
- Incident runbooks: `docs/runbooks/README.md`

## Quick start (local development)

### 1) Start the backend (H2 profile)

```bash
cd apps/backend
./mvnw spring-boot:run -Dspring-boot.run.profiles=dev
```

Backend runs on `http://localhost:8080`.

Helpful local URLs:

- Swagger UI: `http://localhost:8080/swagger-ui.html`
- H2 Console: `http://localhost:8080/h2-console`

### 2) Start the frontend

```bash
cd apps/frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` by default.

## Running tests

### Backend tests

```bash
cd apps/backend
./mvnw test
```

### Frontend tests

```bash
cd apps/frontend
npm test
# or single-run mode
npm run test:run
```

## Docker Compose deployment (single VM)

The Compose files in `deploy/docker-compose/single-vm` are intended for containerized deployment.

```bash
cd deploy/docker-compose/single-vm
cp ../../../apps/backend/.env.example .env
# edit .env values as needed
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

Notes:

- Base compose file runs `mysql`, `backend`, and `frontend` containers.
- Images are expected as `sunmingtao/devboard-backend:${IMAGE_TAG}` and `sunmingtao/devboard-frontend:${IMAGE_TAG}`.
- Backend container uses the `mysql` Spring profile in this mode.

## Useful docs

- Backend details: `apps/backend/README.md`
- Frontend details: `apps/frontend/README.md`
- Deployment docs: `docs/CONTAINER_DEPLOYMENT.md`, `docs/DEPLOYMENT_ENVIRONMENTS.md`, `docs/EKS_GITOPS_TODO.md`
- DevOps interview checklist: `docs/DEVOPS_INTERVIEW_TODO.md`
- Incident runbooks: `docs/runbooks/README.md`

## Current status

This README was updated to reflect the current monorepo structure and run flow. Legacy instructions that generated a fresh Spring project from Spring Initializr are no longer used for this repository.
