# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-04-11

### Added
- Introduced environment separation for infrastructure and deployment:
  - Created dedicated Terraform environments (`envs/dev`, `envs/prod`)
  - Enabled independent provisioning and deployment workflows per environment
- Added support for environment-specific Docker Compose overrides:
  - `docker-compose.dev.yml` and `docker-compose.prod.yml`
  - Enabled flexible configuration for ports, services, and runtime behavior
- Implemented deployment mode control in Jenkins pipeline:
  - `build_and_push` mode for development environment
  - `pull_only` mode for production environment
- Enabled artifact promotion workflow:
  - Reused Docker images built and validated in dev for production deployment
  - Eliminated redundant builds in production

### Changed
- Refactored deployment architecture to use a single public entry point via Nginx:
  - Exposed only port 80 in security groups
  - Removed direct public access to backend (8080) and frontend (3000)
- Updated Nginx configuration to act as reverse proxy:
  - Routed `/` to Vue frontend
  - Routed `/api` to backend service
- Standardized deployment structure on VM:
  - Centralized application files under `/opt/devboard`
  - Unified `.env`-based configuration for runtime variables
- Enhanced Jenkins pipeline to support multi-environment deployments:
  - Dynamically passed `ENVIRONMENT`, `DEPLOY_MODE`, and `DOCKER_IMAGE_TAG`
  - Introduced validation for production deployments (mandatory image tag)

### Improved
- Improved security posture:
  - Reduced attack surface by exposing only port 80
  - Enforced internal service communication via Docker network
- Increased deployment consistency and reliability:
  - Ensured production uses the exact same Docker images validated in dev
- Improved system design clarity:
  - Established clear separation of responsibilities:
    - Terraform → infrastructure
    - Docker Compose → runtime
    - Nginx → traffic routing
    - Jenkins → orchestration
    
## [0.2.0] - 2026-04-02

### Added
- Provisioned AWS infrastructure using Terraform, including VPC, public subnet, security groups, and EC2 instance
- Configured remote Terraform state using Amazon S3 for centralized state management
- Enabled state locking and concurrency control using DynamoDB to prevent parallel apply conflicts

### Changed
- Introduced Terraform-based infrastructure provisioning pipeline in Jenkins:
  - Automated `terraform init`, `plan`, and `apply` within CI/CD
  - Integrated AWS credentials securely via Jenkins credentials store
- Implemented pipeline chaining between infrastructure and application deployment:
  - Captured Terraform outputs (e.g., EC2 public IP)
  - Passed dynamic infrastructure data into downstream deployment pipeline
- Refactored deployment workflow to support dynamic target environments (e.g., AWS EC2 instead of static VM IP)

### Improved
- Enhanced deployment flexibility by externalizing infrastructure-dependent parameters (e.g., VM IP, SSH credentials)
- Improved overall CI/CD automation by enabling end-to-end flow:
  - Infrastructure provisioning → Application build → Deployment
- Increased reliability and scalability by adopting infrastructure-as-code and remote state management

---

## [Unreleased] - 2026-03-29

### Changed
- Reorganized repository structure to improve separation of concerns across application, deployment, infrastructure, and CI/CD components
- Introduced a layered project structure:
  - `apps/` for backend and frontend source code
  - `deploy/` for Docker Compose and deployment scripts
  - `infra/` for Terraform-based infrastructure provisioning
  - `ci/` for Jenkins pipeline definitions
- Improved maintainability and prepared the project for multi-cloud deployment support (AWS, Azure, GCP)

---

## [0.1.0] - 2026-03-28

### Added
- Initial production deployment of DevBoard on Vultr
- Implemented CI/CD pipeline using Jenkins for automated build, Docker image push, and deployment
- Provisioned infrastructure using Terraform
- Deployed full-stack application (Spring Boot backend, Vue 3 frontend, MySQL) using Docker Compose on a VM
