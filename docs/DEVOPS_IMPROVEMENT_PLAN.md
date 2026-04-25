# DevBoard DevOps Improvement Plan (April 2026)

## 1) Current Status Snapshot

Based on repository inspection, DevBoard already has the foundations of a modern DevOps setup:

- Monorepo structure with separated application and infrastructure concerns (`apps`, `deploy`, `infra`, `ci`).
- Multiple CI and deployment workflows under `.github/workflows/`.
- Terraform directories for AWS and legacy environments.
- Docker Compose and Kubernetes deployment assets.

### Key Gaps Observed

1. **Workflow path drift after repo restructuring**  
   Several workflows still reference legacy directories (`devboard-backend`, `devboard-frontend`) while the actual repo uses `apps/backend` and `apps/frontend`.

2. **Mixed and overlapping CI/CD patterns**  
   There are multiple backend/frontend CI and deploy workflows with overlapping responsibilities and inconsistent action versions.

3. **Risky deployment hardcoding**  
   Some deployment workflows contain environment-specific values (bucket names, CloudFront distribution IDs, regions) directly in workflow files.

4. **Quality gates are partially enforced**  
   Example: frontend lint is intentionally non-blocking (`npm run lint || true`), which can allow debt to pass through CI.

5. **No explicit platform-wide SLO/SLA + observability standard in repo docs**  
   Monitoring and alerting concepts exist in docs, but there is no single operational baseline with concrete error budget targets.

---

## 2) DevOps Target State (6-Month Vision)

By the end of this plan, DevBoard should operate with:

- **Single-source CI/CD pipelines** for backend and frontend, mapped to real paths.
- **Environment promotion model** (`dev` → `staging` → `prod`) with controlled approvals.
- **Immutable artifact strategy** (traceable build IDs + SBOM + image signing).
- **Security-first secret and identity model** (OIDC + short-lived cloud credentials).
- **Actionable observability** (SLO dashboards + alert runbooks + deployment correlation).
- **Reliable recovery posture** (documented RTO/RPO, backup validation drills).

---

## 3) Improvement Roadmap

## Phase 0 (Week 1): Baseline & Stabilization

### Goals
- Establish trustworthy baseline before introducing new automation.

### Actions
- Inventory all workflows, mark each as **active**, **legacy**, or **experimental**.
- Fix path references from legacy folders to `apps/backend` and `apps/frontend`.
- Define branch strategy and deployment ownership (who can ship where).
- Add CI badge + status matrix in `README.md`.

### Success Criteria
- Main branch shows deterministic CI behavior (no duplicate/conflicting workflows).
- Every workflow trigger maps to real repository paths.

---

## Phase 1 (Weeks 2-4): CI Standardization & Faster Feedback

### Goals
- Improve consistency, speed, and quality signal of CI.

### Actions
- Consolidate backend CI into one canonical workflow:
  - build, test, static analysis, dependency audit, artifact upload.
- Consolidate frontend CI into one canonical workflow:
  - install, lint (blocking), tests, build, bundle budget check.
- Introduce reusable workflow templates (`workflow_call`) for shared logic.
- Enforce concurrency controls and cancel superseded runs.
- Add test reporting artifacts and failure summaries.

### Success Criteria
- CI median runtime reduced by at least 25%.
- Lint/test/build quality gates block merges on failure.
- No duplicated CI responsibilities across files.

---

## Phase 2 (Weeks 5-8): Progressive Delivery & Environment Governance

### Goals
- Deploy predictably with lower release risk.

### Actions
- Implement staged deployments:
  - PR merge to `main` deploys to `dev` automatically.
  - promotion job deploys to `staging`.
  - protected manual approval for `prod`.
- Externalize all environment-specific values to GitHub environments and cloud parameter stores.
- Add post-deploy smoke tests and health verification gates.
- Add rollback automation (redeploy last known good image).

### Success Criteria
- Each deployment has traceable artifact SHA and environment metadata.
- Rollback to previous stable release in < 10 minutes.

---

## Phase 3 (Weeks 9-12): DevSecOps Hardening

### Goals
- Shift security left and reduce supply-chain risk.

### Actions
- Add SAST + dependency vulnerability scanning in PR and main workflows.
- Add container image scanning (critical/high severity policy).
- Generate SBOM for backend and frontend artifacts.
- Move from long-lived secrets to OIDC-based cloud auth for GitHub Actions.
- Enforce branch protection rules: required checks, signed commits/tags (if team-ready).

### Success Criteria
- Critical vulnerabilities block deployment by policy.
- 100% deployment workflows authenticate via short-lived credentials.

---

## Phase 4 (Weeks 13-16): Observability, Reliability, and Operations

### Goals
- Ensure production operability and measurable reliability.

### Actions
- Define and publish service SLOs:
  - API availability, p95 latency, error rate.
- Implement dashboard set:
  - deployment frequency, lead time, MTTR, change failure rate.
- Add structured logging and trace correlation IDs across frontend/backend.
- Add on-call runbooks for top incident classes.
- Automate backup verification for stateful components.

### Success Criteria
- Weekly reliability review uses real SLO data.
- MTTR trending downward with documented incident playbooks.

---

## 4) Priority Backlog (Highest ROI First)

1. Fix workflow paths to `apps/*` and retire legacy duplicates.
2. Remove hardcoded deployment identifiers from workflow YAML and migrate to environment secrets/vars.
3. Make lint/test gates mandatory.
4. Add deployment smoke tests and rollback job.
5. Implement OIDC-based cloud auth for Actions.
6. Define SLOs and create a single operations dashboard.

---

## 5) Metrics and Reporting Cadence

### Weekly
- CI pass rate
- Median CI duration
- Number of flaky test failures

### Bi-weekly
- Deployment frequency by environment
- Change failure rate
- Mean time to restore

### Monthly
- Open critical/high vulnerabilities
- Secret rotation and credential posture score
- Reliability against SLO targets

---

## 6) Roles and Ownership Model

- **DevOps Owner**: pipeline architecture, IaC governance, reliability KPIs.
- **Backend Owner**: service build/test quality, runtime health, migration safety.
- **Frontend Owner**: web build quality, performance budgets, client error telemetry.
- **Security Champion**: vulnerability triage SLA, policy-as-code guardrails.

Use CODEOWNERS + required review rules so each critical path has accountable reviewers.

---

## 7) Risks and Mitigations

- **Risk:** Consolidation causes temporary pipeline instability.  
  **Mitigation:** Keep legacy workflow toggled but disabled via narrow triggers until replacement proves stable.

- **Risk:** Security scanning increases CI time.  
  **Mitigation:** Split fast PR checks from deep nightly scans.

- **Risk:** Team adoption friction for stricter gates.  
  **Mitigation:** 2-week soft-enforcement period with visible metrics before hard blocking.

---

## 8) 30/60/90-Day Execution Summary

### 0-30 Days
- CI/CD inventory and cleanup.
- Path fixes and duplicate retirement.
- Mandatory quality gates.

### 31-60 Days
- Staged promotion pipeline.
- Post-deploy verification.
- Rollback automation.

### 61-90 Days
- OIDC + security scans + SBOM.
- SLO dashboards and runbooks.
- Reliability review cadence operational.

---

## 9) Definition of Done for the Plan

This improvement plan is considered complete when:

- Every deployment uses a traceable, immutable artifact.
- Every production change has automated verification and rollback path.
- Security checks are policy-enforced in CI/CD.
- Reliability is measured with agreed SLOs and reviewed on schedule.
