# Changelog

All notable changes to this project will be documented in this file.

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
