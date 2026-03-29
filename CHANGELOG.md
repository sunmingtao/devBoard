# Changelog

All notable changes to this project will be documented in this file.

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
