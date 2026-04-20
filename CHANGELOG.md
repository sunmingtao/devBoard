# Changelog

All notable changes to this project will be documented in this file.

## [0.6.1] - 2026-04-21

### Added

- AWS ALB Ingress integration with domain routing via Route 53
- HTTPS support using AWS ACM with automatic HTTP → HTTPS redirection

## [0.6.0] - 2026-04-20

### Added 

- Local Kubernetes deployment using Minikube for development and testing
- Kubernetes manifests (Deployment, Service, ConfigMap, Secret) for full-stack application
- Ingress-based routing in local environment with Nginx Ingress Controller
- AWS EKS deployment for cloud environment
- Public access via AWS LoadBalancer (ELB) for frontend service
- Integration with Amazon RDS (MySQL) in private subnets
- Secure network configuration using AWS Security Groups for EKS ↔ RDS connectivity
- Domain mapping via Route 53 to expose application through custom domain

### Improved

- Migration from Docker Compose to Kubernetes architecture
- Separation of environments using Kustomize overlays (local vs EKS)
- Reverse proxy setup (Nginx) to unify frontend and backend access and avoid CORS issues

## [0.5.1] - 2026-04-17

### Added
- Introduced Elastic IP for EC2 instance:
  - Ensures stable public IP across stop/start cycles
  - Updated Route 53 A record to point to Elastic IP

- Introduced application monitoring and alerting:
  - Implemented Route 53 health check for `/api/health`
  - Configured CloudWatch alarms for application availability and EC2 CPU usage
  - Integrated SNS email notifications for incident alerts

## [0.5.0] - 2026-04-15

### Added
- Integrated Route 53 DNS management into Terraform:
  - Managed A record for `smtdevboard.com` via infrastructure as code
  - Automatically updated DNS records based on EC2 public IP changes
  - Eliminated manual DNS updates during VM recreation
- Automated EC2 start/stop scheduling using AWS EventBridge and Lambda:
  - Implemented a reusable Terraform module (`modules/scheduler`) for infrastructure scheduling
  - Created Lambda functions to start and stop EC2 instances based on tags
  - Configured EventBridge rules with cron expressions for daily scheduling

### Changed
- Migrated database from containerised MySQL to AWS RDS:
  - Removed MySQL service from Docker Compose configuration
  - Updated backend to connect to external RDS instance via environment variables
  - Improved data persistence and decoupled application from infrastructure lifecycle
- Refactored application configuration to support external database:
  - Introduced `DATABASE_URL`, `DATABASE_USERNAME`, and `DATABASE_PASSWORD`
  - Standardised environment-based configuration for runtime flexibility
- Updated Terraform architecture to support multi-tier infrastructure:
  - Added RDS module deployed in private subnets
  - Configured security group rules to allow EC2-to-RDS connectivity only

### Improved
- Strengthened security posture:
  - Isolated database in private subnets
  - Restricted database access to application layer only

### Cost Optimisation
- Reduced compute costs by automatically stopping EC2 instances during idle hours

## [0.4.0] - 2026-04-12

### Added
- Enabled HTTPS for production deployment using Let's Encrypt:
  - Integrated Certbot with Nginx using webroot challenge
  - Provisioned TLS certificates for `smtdevboard.com`
  - Exposed secure public endpoint: https://smtdevboard.com/
- Implemented automated TLS lifecycle management in Jenkins pipeline:
  - Added conditional certificate provisioning based on existence and expiry
  - Introduced `AUTO_MANAGE_TLS` flag to control TLS automation behavior
- Added dynamic Nginx configuration switching:
  - `nginx.http.conf` for ACME challenge during certificate issuance
  - `nginx.https.template.conf` for HTTPS runtime configuration
  - Introduced `active.nginx.conf` as runtime-mounted configuration
- Extended deployment pipeline to support TLS-aware deployments:
  - Automatically falls back to HTTP mode for initial certificate provisioning
  - Switches to HTTPS configuration post certificate issuance

### Changed
- Updated Docker Compose configuration for frontend service:
  - Replaced static Nginx config mount with dynamic `active.nginx.conf`
  - Enabled seamless switching between HTTP and HTTPS without modifying Compose files
- Refactored deployment flow to be TLS-aware and idempotent:
  - Avoided repeated certificate requests by validating existing certificates
  - Ensured safe re-deployments without breaking HTTPS setup
- Updated environment configuration:
  - Included domain-based origins in CORS settings
  - Aligned runtime configuration with public domain access

### Improved
- Improved security posture:
  - Enabled encrypted traffic over HTTPS
  - Reduced risk of certificate misconfiguration through automated checks
- Increased deployment reliability:
  - Ensured TLS setup is executed only when required (missing or expiring certificates)
  - Eliminated manual steps for certificate provisioning
- Enhanced production readiness:
  - Established a repeatable and automated HTTPS deployment workflow
  - Prepared the system for future scaling behind domain-based routing (e.g., ALB, CloudFront)

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
