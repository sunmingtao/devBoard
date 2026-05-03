# EKS GitOps Integration TODO

## Goal

Move the working local Argo CD setup toward EKS without mixing local-only choices, Jenkins-era deployment steps, and AWS production routing.

---

## 1. Separate Local and EKS Argo CD Apps

- [x] Keep the current local `devboard` app pointed at:
  - [x] `deploy/k8s/overlays/local`
- [x] Add a separate EKS DevBoard Argo CD app, for example:
  - [x] `deploy/gitops/apps/devboard-eks.yaml`
- [x] Point the EKS app at:
  - [x] `deploy/k8s/overlays/eks`
- [x] Keep local-only apps separate from EKS:
  - [x] `ingress-nginx`
  - [x] `ingress-nginx-namespace`
- [x] Decide naming convention:
  - [x] `devboard-local`
  - [x] `devboard-eks`
  - [x] `devboard-kafka`

---

## 2. Fix the EKS Overlay Before Argo Uses It

- [x] Add `deploy/k8s/overlays/eks/ingress.yaml` to `deploy/k8s/overlays/eks/kustomization.yaml`
- [ ] Add EKS image tag handling without `envsubst`
  - [x] Option A: use fixed tags in EKS overlay patches, similar to local
  - [ ] Option B: have Jenkins update Kustomize image tags in Git after image build
  - [ ] Option C: add Argo CD Image Updater later
- [x] Remove or replace unresolved placeholders:
  - [x] `${IMAGE_TAG}`
  - [x] `${DB_HOST}`
  - [x] `${DB_PASSWORD}`
Run ```
kubectl create secret generic devboard-backend-secret \
  -n devboard \
  --from-literal=DATABASE_PASSWORD="${RDS_EKS_DB_PASSWORD}"
``` after EKS cluster is created (TODO)
  - [x] `PLACEHOLDER_LOADBALANCER_DNS`
- [x] Verify EKS render is clean:
  - [x] `kubectl kustomize deploy/k8s/overlays/eks`
  - [x] no `${...}` placeholders in rendered output

---

## 3. Decide How EKS Secrets Are Managed

- [x] Do not commit real database passwords to Git
- [x] Replace `backend-secret.yaml` strategy
  - [x] Option A: manually create `devboard-backend-secret` in EKS before Argo sync
  - [ ] Option B: use External Secrets Operator with AWS Secrets Manager
  - [ ] Option C: use Sealed Secrets
- [ ] Document which secret strategy is used for the interview demo
- [x] Ensure Argo CD does not overwrite manually managed secrets unless intended

---

## 4. Decide How RDS Host Is Managed

- [x] Stop relying on Jenkins `envsubst` for `${DB_HOST}`
- [x] Choose one GitOps-friendly option:
  - [x] Put non-secret RDS endpoint directly in EKS ConfigMap
  - [ ] Generate/update ConfigMap in Git from Terraform output
  - [ ] Use External Secrets/Config operator pattern later
- [x] Confirm backend can connect to RDS from EKS nodes
- [x] Confirm RDS security group allows EKS access

---

## 5. Use AWS Load Balancer Controller, Not ingress-nginx, on EKS

- [x] Keep `ingress-nginx` only for local Minikube
- [x] Confirm Terraform infra pipeline installs AWS Load Balancer Controller
  - [x] IAM role
  - [x] service account in `kube-system`
  - [x] Helm release in `kube-system`
  - [x] Do not also manage this controller with Argo CD
- [x] Confirm controller is running:
  - [x] `kubectl get pods -n kube-system | grep aws-load-balancer-controller`
- [x] Confirm EKS Ingress uses ALB annotations:
  - [x] `kubernetes.io/ingress.class: alb`
  - [x] `alb.ingress.kubernetes.io/scheme: internet-facing`
  - [x] `alb.ingress.kubernetes.io/target-type: ip`
  - [x] certificate ARN
- [x] Add ALB health check annotations to the EKS ingress manifest:
  - [x] `alb.ingress.kubernetes.io/healthcheck-path: /api/health`
  - [x] `alb.ingress.kubernetes.io/success-codes: "200"`

---

## 6. Convert Kafka Ownership From Jenkins to Argo CD

- [x] Stop installing Kafka in `Jenkinsfile.eks.deploy`
- [x] Use the existing Argo CD Kafka app for EKS as well, or create `devboard-kafka-eks.yaml`
- [x] Confirm Kafka service DNS matches app config:
  - [x] `devboard-kafka.devboard.svc.cluster.local:9092`
- [x] Decide persistence for EKS Kafka:
  - [x] demo mode: persistence disabled
  - [ ] more realistic mode: persistence enabled with EBS-backed storage class
- [ ] Document why Kafka is single-node for demo

---

## 7. Redefine Jenkins Role in GitOps

- [x] Keep Jenkins as CI:
  - [x] test
  - [x] build Docker images
  - [x] push image tags
  - [ ] scan images later
- [x] Remove direct `kubectl apply -k` deployment from Jenkins EKS pipeline
- [x] Remove direct `helm upgrade --install` for Kafka from Jenkins EKS pipeline
- [ ] Add GitOps handoff:
  - [ ] Jenkins updates image tag in Git
  - [ ] Jenkins pushes commit
  - [ ] Argo CD reconciles EKS cluster from Git
- [ ] Add a clear interview sentence:
  - [ ] "Jenkins produces artifacts; Argo CD owns deployment reconciliation."

---

## 8. Observability GitOps Plan

- [ ] Add Argo CD app for EKS observability, for example:
  - [ ] `deploy/gitops/apps/observability-eks.yaml`
- [ ] Point it to:
  - [ ] `deploy/observability/eks`
- [ ] Decide how Helm-installed monitoring moves from Jenkins to GitOps:
  - [ ] kube-prometheus-stack as Argo CD Helm app
  - [ ] kafka-exporter as Argo CD Helm app
  - [ ] dashboards and ServiceMonitors from `deploy/observability/eks`
- [ ] Avoid mixing Jenkins Helm ownership and Argo CD ownership

---

## 9. EKS Validation Checklist

- [x] Terraform EKS infra applied
- [x] AWS Load Balancer Controller running
- [x] Argo CD installed on EKS
- [ ] Private Git repo credentials configured in Argo CD, if needed
- [x] Namespace apps synced
- [x] Kafka app synced and healthy
- [x] DevBoard EKS app synced and healthy
- [x] Ingress has ALB hostname:
  - [x] `kubectl get ingress devboard-ingress -n devboard`
- [x] DNS points to ALB
- [x] HTTPS works:
  - [x] `curl -I https://www.smtdevboard.com`
- [x] Backend health works:
  - [x] `curl https://www.smtdevboard.com/api/health`
- [x] Frontend loads in browser

---

## 10. Interview Story

- [ ] Explain local-to-EKS progression:
  - [ ] local Minikube used ingress-nginx NodePort
  - [ ] EKS uses AWS Load Balancer Controller and ALB
- [ ] Explain ownership boundary:
  - [ ] one resource, one owner
  - [ ] Jenkins no longer mutates Kubernetes runtime resources
  - [ ] Argo CD reconciles cluster state from Git
- [ ] Explain secret handling decision
- [ ] Explain image tag promotion flow
- [ ] Explain rollback:
  - [ ] revert Git commit
  - [ ] Argo CD reconciles previous desired state