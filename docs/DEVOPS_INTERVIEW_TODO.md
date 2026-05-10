# DevBoard DevOps Interview TODO List

## Goal

Add high-value DevOps features that make DevBoard look closer to a production platform and create strong interview talking points around deployment, security, observability, and operations.

---

## Phase 1 - Argo CD GitOps

### Repository Structure

- [x] Create GitOps directory:
  - [x] `deploy/gitops/`
  - [x] `deploy/gitops/argocd/`
  - [x] `deploy/gitops/apps/`
- [x] Decide GitOps source path for Kubernetes manifests:
  - [x] EKS overlay
  - [ ] future dev/prod overlays

---

### Argo CD Installation

- [x] Create `argocd` namespace
- [x] Install Argo CD on EKS
- [x] Expose Argo CD UI securely:
  - [x] port-forward option for local demo
  - [ ] optional ingress option for interview demo
- [x] Document initial admin login flow

---

### Argo CD Application

* [x] Create Argo CD `Application` manifest for DevBoard
* [x] Point app to this repository
* [x] Point app to Kubernetes overlay path
* [x] Configure destination namespace:

  * [x] `devboard`
* [x] Enable automated sync:

  * [x] prune
  * [x] self-heal
* [x] Add manual sync instructions for safer demos

---

### GitOps Workflow Documentation

* [ ] Add README explaining:

  * [ ] Git commit triggers desired state change
  * [ ] Argo CD detects drift
  * [ ] Argo CD syncs manifests into EKS
  * [ ] rollback using Git history
* [x] Add screenshots or command output examples:

  * [x] app healthy
  * [x] app synced
  * [x] app out-of-sync demo

---

## Phase 2 - Trivy and Security Scanning in CI

### Container Image Scanning

* [x] Add Trivy scan for backend image
* [x] Add Trivy scan for frontend image
* [x] Add Trivy scan for event-service image
* [x] Add Trivy scan for event-frontend image
* [x] Fail CI on critical vulnerabilities
* [x] Decide threshold for high vulnerabilities:

  * [x] fail build
  * [ ] warn only

---

### Filesystem and Dependency Scanning

* [ ] Add Trivy filesystem scan for repository
* [ ] Scan Maven dependencies
* [ ] Scan npm dependencies
* [ ] Generate readable CI output
* [x] Store image scan reports as build artifacts

---

### Infrastructure and Manifest Scanning

* [ ] Scan Kubernetes manifests
* [ ] Scan Terraform code
* [ ] Add checks for common issues:

  * [ ] privileged containers
  * [ ] missing resource limits
  * [ ] plaintext secrets
  * [ ] overly permissive security groups
* [ ] Document accepted risks and false positives

---

### CI Integration

* [x] Add Trivy stage to Jenkins EKS build pipeline
* [x] Add clear pass/fail logs
* [x] Prevent deploy when scan fails
* [x] Add local command examples for running scans manually
* [x] Update CI documentation with security gate behavior

---

## Phase 3 - Alertmanager Alerts and Runbooks

### Alertmanager Setup

* [x] Enable or configure Alertmanager in kube-prometheus-stack
* [x] Add notification route:

  * [x] local/demo route
  * [x] optional Slack webhook
  * [x] optional email receiver
* [x] Document how to view active alerts
* [x] Document how to silence alerts during demos

---

### Application Alerts

* [x] Add backend availability alert
* [x] Add event-service availability alert
* [x] Add frontend availability alert
* [x] Add pod restart alert
* [x] Add high CPU alert
* [x] Add high memory alert

---

### Kafka Alerts

* [x] Add Kafka consumer lag alert
* [x] Add no messages consumed alert
* [x] Add Kafka exporter down alert
* [x] Add event-service Kafka listener error alert
* [x] Validate alert delivery with `DevBoardKafkaNoMessagesConsumed` Gmail notification

---

### HTTP and Latency Alerts

* [x] Add high backend error rate alert
* [x] Add high backend latency alert
* [x] Add actuator scrape failure alert
* [x] Add service unavailable alert

---

### Runbooks

* [ ] Create `docs/runbooks/` directory
* [ ] Add runbook for Kafka consumer lag
* [ ] Add runbook for pod crash loops
* [ ] Add runbook for failed Kubernetes rollout
* [ ] Add runbook for backend high error rate
* [ ] Add runbook for database connectivity issues
* [ ] Add runbook for rollback procedure

---

### Demo Scenario

* [x] Break event-service intentionally
* [x] Show Alertmanager firing Kafka consumer alert
* [ ] Show Grafana panel confirming the issue
* [ ] Follow runbook steps to diagnose
* [x] Restore service
* [ ] Show alert resolves

---

## Final Interview Outcome

* [ ] GitOps deployment workflow with Argo CD
* [ ] Security scanning gate in CI
* [ ] Alerting for real operational failures
* [ ] Runbooks showing production support thinking
* [ ] Demo story that covers deploy, detect, diagnose, and recover
