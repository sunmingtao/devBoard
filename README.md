# DevBoard

DevBoard is a full-stack task board application with a Spring Boot backend and a Vue 3 frontend, plus deployment assets for Docker Compose, Jenkins, and Terraform.

## Tech stack

- **Frontend:** Vue 3 + Vite + Vue Router (`apps/frontend`)
- **Backend:** Spring Boot 3.3 (Java 25), Spring Security, JWT, JPA (`apps/backend`)
- **Data stores:** H2 (dev/test), MySQL (container/mysql profile), Redis-ready config
- **Infra/Deploy:** Docker Compose (`deploy/docker-compose/single-vm`), Terraform (`infra/terraform`), Jenkins pipelines (`ci/jenkins`)

## Repository layout

```text
.
├── apps/
│   ├── backend/     # Spring Boot API
│   └── frontend/    # Vue SPA
├── deploy/
│   └── docker-compose/single-vm/
├── ci/jenkins/
├── infra/terraform/
└── docs/
```

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
- Deployment docs: `docs/CONTAINER_DEPLOYMENT.md`, `docs/DEPLOYMENT_ENVIRONMENTS.md`

## Current status

This README was updated to reflect the current monorepo structure and run flow. Legacy instructions that generated a fresh Spring project from Spring Initializr are no longer used for this repository.
