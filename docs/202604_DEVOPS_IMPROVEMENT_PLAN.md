# DevBoard DevOps Improvement TODO Checklist

## Goal

Improve DevBoard's CI/CD, deployment governance, security posture, observability, and reliability over a 6-month roadmap.

## Current Foundation

DevBoard already has the foundations of a modern DevOps setup:

- [x] Monorepo structure with separated application and infrastructure concerns: `apps`, `deploy`, `infra`, and `ci`
- [x] Multiple CI and deployment workflows under `.github/workflows/`
- [x] Terraform directories for AWS and legacy environments
- [x] Docker Compose and Kubernetes deployment assets

## Key Gaps To Close

- [ ] Fix workflow path drift from legacy folders to current paths
  - [ ] Replace `devboard-backend` references with `apps/backend`
  - [ ] Replace `devboard-frontend` references with `apps/frontend`
- [ ] Reduce mixed and overlapping CI/CD patterns
  - [ ] Identify duplicate backend workflows
  - [ ] Identify duplicate frontend workflows
  - [ ] Decide which workflows are canonical
  - [ ] Disable or remove legacy workflow triggers
- [ ] Remove risky deployment hardcoding
  - [ ] Move bucket names out of workflow YAML
  - [ ] Move CloudFront distribution IDs out of workflow YAML
  - [ ] Move region-specific deployment values out of workflow YAML
  - [ ] Store environment-specific values in GitHub environments, secrets, vars, or cloud parameter stores
- [ ] Strengthen quality gates
  - [ ] Make frontend lint blocking
  - [ ] Make backend tests blocking
  - [ ] Make frontend tests and build blocking
- [ ] Define one platform-wide operational baseline
  - [ ] Publish service SLOs
  - [ ] Define error budget targets
  - [ ] Define alerting expectations
  - [ ] Link dashboards to incident runbooks

## Target State

By the end of this plan, DevBoard should have:

- [ ] Single-source CI/CD pipelines for backend and frontend mapped to real repository paths
- [ ] Environment promotion model: `dev -> staging -> prod`
- [ ] Controlled approvals for production deployments
- [ ] Immutable artifact strategy with traceable build IDs
- [ ] SBOM generation for release artifacts
- [ ] Container image signing or equivalent artifact trust control
- [ ] Security-first secret and identity model using OIDC and short-lived cloud credentials
- [ ] SLO dashboards with actionable alerts
- [ ] Deployment correlation in logs, metrics, and dashboards
- [ ] Documented RTO and RPO targets
- [ ] Backup validation drills for stateful components

## Priority Backlog

- [ ] Fix workflow paths to `apps/*` and retire legacy duplicates
- [ ] Remove hardcoded deployment identifiers from workflow YAML
- [ ] Migrate deployment configuration to environment secrets and vars
- [ ] Make lint, test, and build gates mandatory
- [ ] Add deployment smoke tests
- [ ] Add rollback automation
- [ ] Implement OIDC-based cloud auth for GitHub Actions
- [ ] Define SLOs
- [ ] Create a single operations dashboard

## Phase 0: Week 1, Baseline And Stabilization

Goals:

- [ ] Establish a trustworthy baseline before introducing new automation

Implementation tasks:

- [ ] Inventory all workflows
- [ ] Mark each workflow as active, legacy, or experimental
- [x] Fix path references from legacy folders to `apps/backend` and `apps/frontend`
- [x] Define branch strategy
- [x] Define deployment ownership
- [x] Document who can ship to each environment
- [ ] Add CI badge to `README.md`
- [ ] Add workflow status matrix to `README.md`

Acceptance criteria:

- [ ] Main branch has deterministic CI behavior
- [ ] No duplicate or conflicting workflows run for the same responsibility
- [ ] Every workflow trigger maps to real repository paths

## Phase 1: Weeks 2-4, CI Standardization And Faster Feedback

Goals:

- [ ] Improve CI consistency
- [ ] Improve CI speed
- [ ] Improve CI quality signal

Backend CI tasks:

- [ ] Consolidate backend CI into one canonical workflow
- [ ] Run backend build
- [ ] Run backend tests
- [ ] Run backend static analysis
- [ ] Run backend dependency audit
- [ ] Upload backend artifacts

Frontend CI tasks:

- [ ] Consolidate frontend CI into one canonical workflow
- [ ] Install frontend dependencies
- [ ] Make frontend lint blocking
- [ ] Run frontend tests
- [ ] Run frontend build
- [ ] Add frontend bundle budget check

Shared CI tasks:

- [ ] Introduce reusable workflow templates using `workflow_call`
- [ ] Enforce concurrency controls
- [ ] Cancel superseded workflow runs
- [ ] Add test reporting artifacts
- [ ] Add failure summaries

Acceptance criteria:

- [ ] CI median runtime is reduced by at least 25 percent
- [ ] Lint failures block merges
- [ ] Test failures block merges
- [ ] Build failures block merges
- [ ] No duplicated CI responsibilities remain across workflow files

## Phase 2: Weeks 5-8, Progressive Delivery And Environment Governance

Goals:

- [ ] Deploy predictably
- [ ] Lower release risk
- [ ] Make environment promotion traceable

Implementation tasks:

- [ ] Implement staged deployments
- [ ] Deploy PR merges to `main` automatically to `dev`
- [ ] Add promotion job for `staging`
- [ ] Add protected manual approval for `prod`
- [ ] Externalize environment-specific values to GitHub environments
- [ ] Externalize sensitive values to cloud parameter stores or secrets managers
- [ ] Add post-deploy smoke tests
- [ ] Add health verification gates
- [ ] Add rollback automation
- [ ] Redeploy last known good image during rollback

Acceptance criteria:

- [ ] Each deployment has traceable artifact SHA
- [ ] Each deployment records environment metadata
- [ ] Rollback to previous stable release completes in less than 10 minutes

## Phase 3: Weeks 9-12, DevSecOps Hardening

Goals:

- [ ] Shift security left
- [ ] Reduce supply-chain risk
- [ ] Replace long-lived cloud credentials

Implementation tasks:

- [ ] Add SAST scanning to PR workflows
- [ ] Add SAST scanning to main workflows
- [ ] Add dependency vulnerability scanning to PR workflows
- [ ] Add dependency vulnerability scanning to main workflows
- [ ] Add container image scanning
- [ ] Define policy for critical and high severity image findings
- [ ] Generate SBOM for backend artifacts
- [ ] Generate SBOM for frontend artifacts
- [ ] Move GitHub Actions cloud auth to OIDC
- [ ] Remove long-lived cloud credentials from deployment workflows
- [ ] Enforce branch protection required checks
- [ ] Evaluate signed commits or signed tags when the team is ready

Acceptance criteria:

- [ ] Critical vulnerabilities block deployment by policy
- [ ] 100 percent of deployment workflows authenticate using short-lived credentials

## Phase 4: Weeks 13-16, Observability, Reliability, And Operations

Goals:

- [ ] Make production operability measurable
- [ ] Define reliability expectations
- [ ] Improve incident response and recovery

SLO tasks:

- [ ] Define API availability SLO
- [ ] Define p95 latency SLO
- [ ] Define error-rate SLO
- [ ] Publish SLO targets in repo docs

Dashboard tasks:

- [ ] Create deployment frequency dashboard
- [ ] Create lead time dashboard
- [ ] Create MTTR dashboard
- [ ] Create change failure rate dashboard
- [ ] Add deployment correlation to dashboards

Operations tasks:

- [ ] Add structured logging across backend services
- [ ] Add trace correlation IDs across frontend and backend
- [ ] Add runbook for deployment failures
- [ ] Add runbook for elevated API errors
- [ ] Add runbook for latency incidents
- [ ] Add runbook for infrastructure degradation
- [ ] Automate backup verification for stateful components

Acceptance criteria:

- [ ] Weekly reliability review uses real SLO data
- [ ] MTTR trends downward over time
- [ ] Top incident classes have documented playbooks

## 30/60/90-Day Execution Plan

### 0-30 Days

- [ ] Complete CI/CD inventory
- [ ] Clean up duplicate workflows
- [ ] Fix workflow path references
- [ ] Retire legacy workflow triggers
- [ ] Enforce mandatory quality gates

### 31-60 Days

- [ ] Implement staged promotion pipeline
- [ ] Add post-deploy verification
- [ ] Add rollback automation
- [ ] Externalize deployment configuration

### 61-90 Days

- [ ] Implement OIDC for deployment workflows
- [ ] Add security scans
- [ ] Generate SBOMs
- [ ] Create SLO dashboards
- [ ] Create operational runbooks
- [ ] Start reliability review cadence

## Metrics And Reporting Cadence

Weekly:

- [ ] Report CI pass rate
- [ ] Report median CI duration
- [ ] Report number of flaky test failures

Bi-weekly:

- [ ] Report deployment frequency by environment
- [ ] Report change failure rate
- [ ] Report mean time to restore

Monthly:

- [ ] Report open critical and high vulnerabilities
- [ ] Report secret rotation status
- [ ] Report credential posture score
- [ ] Report reliability against SLO targets

## Roles And Ownership

- [ ] Assign DevOps Owner for pipeline architecture, IaC governance, and reliability KPIs
- [ ] Assign Backend Owner for service build and test quality, runtime health, and migration safety
- [ ] Assign Frontend Owner for web build quality, performance budgets, and client error telemetry
- [ ] Assign Security Champion for vulnerability triage SLA and policy-as-code guardrails
- [ ] Add or update `CODEOWNERS`
- [ ] Configure required review rules for critical paths

## Risks And Mitigations

Pipeline consolidation risk:

- [ ] Keep legacy workflows available with narrow or disabled triggers until replacements prove stable
- [ ] Compare old and new workflow output during transition

Security scanning runtime risk:

- [ ] Split fast PR checks from deep nightly scans
- [ ] Track CI duration before and after security controls are added

Stricter gates adoption risk:

- [ ] Run a 2-week soft-enforcement period
- [ ] Publish quality gate metrics during soft enforcement
- [ ] Switch to hard blocking after the team has visibility into failure patterns

## Definition Of Done

This improvement plan is complete when:

- [ ] Every deployment uses a traceable immutable artifact
- [ ] Every production change has automated verification
- [ ] Every production change has a rollback path
- [ ] Security checks are policy-enforced in CI/CD
- [ ] Reliability is measured with agreed SLOs
- [ ] Reliability is reviewed on a regular schedule
