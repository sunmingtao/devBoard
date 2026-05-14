# DevBoard Kubernetes / AWS Learning TODO List

## Goal

Build practical, demo-ready, and operations-friendly cloud-native features in the existing DevBoard project to deepen hands-on Kubernetes and AWS skills.

## Current Foundation

DevBoard already has a strong base:

- [ ] Multi-service architecture: backend, event-service, and frontend
- [ ] Kubernetes base and overlays for local and EKS environments
- [ ] Observability stack with Prometheus, Grafana, and alerting rules
- [ ] EKS and GitOps documentation plus early pipeline structure

The next stage should focus on platform engineering skills and production-grade reliability.

## Priority Features

### 1. External Secrets + AWS Secrets Manager

Learning goals:

- [ ] Learn IAM Roles for Service Accounts (IRSA)
- [ ] Learn how AWS Secrets Manager syncs into Kubernetes Secrets
- [ ] Learn secret management best practices in a GitOps workflow

Implementation tasks:

- [x] Install External Secrets Operator in local minikube
- [x] Add a local Argo CD Helm Application for External Secrets Operator
- [x] Replace the local `devboard-backend-secret` Secret manifest with an `ExternalSecret`
- [x] Install External Secrets Operator in EKS
  - [x] Add an EKS Argo CD Helm Application for External Secrets Operator
  - [x] Sync and verify the EKS `external-secrets-eks` Application
- [x] Replace the manually created EKS `devboard-backend-secret` with an `ExternalSecret`
- [x] Store the database password in AWS Secrets Manager
- [x] Store the JWT secret in AWS Secrets Manager
- [ ] Store Kafka credentials in AWS Secrets Manager if Kafka authentication is enabled later

Acceptance criteria:

- [x] Local Argo CD app `external-secrets-local` is `Synced` and `Healthy`
- [x] Local External Secrets pods are running in the `external-secrets` namespace
- [x] Local `devboard-backend-secret` is owned by `ExternalSecret/devboard-backend-secret`
- [ ] EKS `kubectl get externalsecret -n devboard` shows `Ready=True`
- [ ] Recreated pods can automatically load the latest secrets
- [ ] The Git repository no longer needs plaintext secrets or manual secret injection steps

### 2. Progressive Delivery with Argo Rollouts + ALB/Nginx

Learning goals:

- [ ] Learn canary and blue-green deployment strategies
- [ ] Learn metric-driven automatic rollback
- [ ] Learn release risk control and SLO-based thinking

Implementation tasks:

- [ ] Convert the backend deployment to an Argo Rollouts `Rollout` resource
- [ ] Configure a canary traffic strategy: 10% -> 30% -> 100%
- [ ] Add Prometheus metric gates for 5xx errors and p95 latency

Acceptance criteria:

- [ ] A new backend release shows staged traffic shifting
- [ ] The rollout automatically aborts when metrics exceed thresholds
- [ ] A reusable release runbook exists

### 3. Event-Driven Autoscaling with KEDA + Kafka Lag

Learning goals:

- [ ] Learn autoscaling based on business workload, not only CPU
- [ ] Learn Kafka lag semantics and consumer capacity modeling
- [ ] Learn the stability tradeoffs between HPA, KEDA, and workload behavior

Implementation tasks:

- [ ] Add a KEDA `ScaledObject` for `event-service`
- [ ] Use Kafka lag as the scaling signal
- [ ] Configure cooldown period, minimum replicas, and anti-thrashing settings

Acceptance criteria:

- [ ] `event-service` replicas increase when Kafka backlog is created
- [ ] Replicas decrease after the backlog drains
- [ ] Scaling does not thrash under normal load changes

### 4. Multi-Environment GitOps Promotion: Dev -> Stage -> Prod

Learning goals:

- [ ] Learn environment layering and configuration drift control
- [ ] Learn image promotion instead of rebuilding separately for each environment
- [ ] Learn approval gates and release traceability

Implementation tasks:

- [ ] Add `deploy/k8s/overlays/stage`
- [ ] Add `deploy/k8s/overlays/prod`
- [ ] Define an image tag or digest promotion process, such as commit SHA-based promotion
- [ ] Add a promotion job in Jenkins or GitHub Actions

Acceptance criteria:

- [ ] The same image digest can be promoted from dev to prod
- [ ] Each release can be traced to a commit, tag, and change owner
- [ ] Rollback only requires reverting the referenced version in an overlay

### 5. SLO + Error Budget + Alert Tuning

Learning goals:

- [ ] Move from basic monitoring to explicit reliability targets
- [ ] Reduce alert noise and false positives
- [ ] Define system health from the user's experience

Implementation tasks:

- [ ] Define a measurable backend SLO, such as 99.5% availability
- [ ] Create multi-window burn-rate alerts
- [ ] Add a Grafana SLO dashboard

Acceptance criteria:

- [ ] The dashboard shows 7-day and 30-day SLO performance
- [ ] Each alert maps to a runbook
- [ ] During a drill, release decisions can be made using the error budget

### 6. Cost-Aware Platform: Cost Observability + Resource Governance

Learning goals:

- [ ] Learn how requests and limits affect cost and stability
- [ ] Learn cluster cost attribution by namespace and workload
- [ ] Learn basic FinOps practices

Implementation tasks:

- [ ] Add requests and limits for all services
- [ ] Install Kubecost or OpenCost
- [ ] Create a cost dashboard for the `devboard` namespace

Acceptance criteria:

- [ ] High-cost workloads can be identified
- [ ] At least two cost-saving recommendations are documented with performance impact analysis
- [ ] Cost data can be included in weekly reports or retrospectives

## 12-Week Delivery Plan

### Phase 1: Weeks 1-4, Foundation and Governance

- [ ] Implement External Secrets
- [ ] Add multi-environment overlay layering
- [ ] Create the first SLO version and clean up alerts

### Phase 2: Weeks 5-8, Release Safety and Elasticity

- [ ] Implement Argo Rollouts canary delivery
- [ ] Implement KEDA autoscaling based on Kafka lag
- [ ] Run failure drills for rollback, rate limiting, and graceful degradation

### Phase 3: Weeks 9-12, Platform Maturity and Review

- [ ] Build the cost governance dashboard
- [ ] Complete platform runbooks
- [ ] Prepare interview or presentation material, including architecture diagrams and metric improvements

## Recommended Starting Order

To improve AWS and Kubernetes interview readiness quickly:

- [ ] Start with Feature 1: External Secrets
- [ ] Then implement Feature 2: Progressive Delivery
- [ ] Then implement Feature 3: KEDA

This sequence demonstrates security, stability, and elasticity, which are close to real production platform work.

## Deliverables for Each Feature

- [ ] Before-and-after architecture diagram
- [ ] Kubernetes manifests or Helm values
- [ ] CI/CD pipeline changes
- [ ] Monitoring dashboards and alerting rules
- [ ] One-page runbook covering diagnosis and rollback
- [ ] Five-to-ten-minute demo script

Completing each feature with these deliverables turns the work into a strong platform engineering case study, not just a code change.
