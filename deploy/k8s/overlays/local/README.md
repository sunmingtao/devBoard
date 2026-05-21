## 🚀 Run with Kubernetes (Minikube)
1️⃣ Start Minikube

`minikube start`

2️⃣ Install the controllers used by this overlay

The local overlay now includes an Argo Rollouts `Rollout` and an External
Secrets `ExternalSecret`, so install both CRDs/controllers before applying the
app manifests:

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo add external-secrets https://charts.external-secrets.io
helm repo update

helm upgrade --install argo-rollouts argo/argo-rollouts \
  --namespace argo-rollouts \
  --create-namespace \
  --version 2.40.9

helm upgrade --install external-secrets external-secrets/external-secrets \
  --namespace external-secrets \
  --create-namespace \
  --version 2.3.0 \
  --set installCRDs=true

kubectl wait --for condition=Established crd/rollouts.argoproj.io --timeout=180s
kubectl wait --for condition=Established crd/externalsecrets.external-secrets.io --timeout=180s
```

3️⃣ Create local-only backend secrets

`backend-secret.yaml` is intentionally ignored by Git. Create it from the
example and replace `JWT_SECRET` with a local base64 signing secret:

```bash
cp deploy/k8s/overlays/local/backend-secret.example.yaml deploy/k8s/overlays/local/backend-secret.yaml
openssl rand -base64 64
```

Then edit `deploy/k8s/overlays/local/backend-secret.yaml` and paste the
generated value into `JWT_SECRET`.

4️⃣ Deploy all resources

```
kubectl apply -k deploy/k8s/overlays/local
```

5️⃣ Verify deployment

```
kubectl get all -n devboard
kubectl get rollout devboard-backend -n devboard
kubectl wait --for=condition=Available rollout.argoproj.io/devboard-backend -n devboard --timeout=300s
```
Expected:
```
frontend → Running
backend → Running
mysql → Running
```
6️⃣ Access the application

```
minikube service devboard-frontend -n devboard
```
Example output:

```
http://127.0.0.1:40xxx
```

Open in browser.

🔍 API Test
```
curl http://127.0.0.1:<PORT>/api/health
```

Expected response:

```
{
  "code": 0,
  "message": "success",
  "data": "OK"
}
```

## ⚙️ Configuration
### Backend Config (ConfigMap)
- SPRING_PROFILES_ACTIVE
- DATABASE_URL
- DATABASE_USERNAME
- CORS_ALLOWED_ORIGINS

### Secrets

MySQL credentials stored in Kubernetes Secret

## 🧠 Key Learnings

- Migrated from Docker Compose → Kubernetes
- Understood Deployment vs Pod
- Implemented Service networking (ClusterIP & NodePort)
- Used ConfigMap & Secret for configuration management
- Debugged:
  - CrashLoopBackOff
  - DB connection issues
  - Secret updates & rollout restart

## 🛠️ Useful Commands

```
# Check pods
kubectl get pods -n devboard

# View logs
kubectl logs -l app=devboard-backend -n devboard

# Restart backend Rollout
kubectl rollout restart rollout.argoproj.io/devboard-backend -n devboard

# Watch backend Rollout status
kubectl get rollout devboard-backend -n devboard -w

# Port forward (alternative access)
kubectl port-forward svc/devboard-frontend 8080:80 -n devboard
```

📌 Future Improvements

- [ ] Add Ingress (custom domain)
- [ ] CI/CD with Jenkins or GitHub Actions
- [ ] Deploy to AWS (EKS + RDS)
- [ ] Helm chart packaging
-[] Horizontal Pod Autoscaling
