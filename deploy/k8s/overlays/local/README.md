## 🚀 Run with Kubernetes (Minikube)
1️⃣ Start Minikube

`minikube start`

2️⃣ Deploy all resources
```
kubectl apply -f k8s/local/namespace.yaml
kubectl apply -f k8s/local/
```
3️⃣ Verify deployment
```
kubectl get all -n devboard
```
Expected:
```
frontend → Running
backend → Running
mysql → Running
```
4️⃣ Access the application
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
kubectl logs deployment/devboard-backend -n devboard

# Restart deployment
kubectl rollout restart deployment devboard-backend -n devboard

# Port forward (alternative access)
kubectl port-forward svc/devboard-frontend 8080:80 -n devboard
```

📌 Future Improvements

- [ ] Add Ingress (custom domain)
- [ ] CI/CD with Jenkins or GitHub Actions
- [ ] Deploy to AWS (EKS + RDS)
- [ ] Helm chart packaging
-[] Horizontal Pod Autoscaling
