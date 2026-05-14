# Database Connectivity Runbook

## Purpose

Use this when backend or event-service pods cannot connect to MySQL/RDS, when
database-backed endpoints fail, or when logs show SQL, JDBC, authentication, or
connection pool errors.

## Signals

- Backend `/api/health` or `/actuator/health` fails.
- Event-service `/api/health` is up but event persistence fails.
- Logs contain `CommunicationsException`, `Access denied`, `Connection refused`,
  `Connection timed out`, `HikariPool`, or SQL migration errors.
- `DevBoardBackendHighErrorRate`, `DevBoardServiceUnavailable`, or event-service
  alerts fire after database writes fail.

## First Checks

```bash
export APP_NS=devboard

kubectl get pods -n "$APP_NS" -l app=devboard-backend
kubectl get pods -n "$APP_NS" -l app=devboard-event-service
kubectl logs -n "$APP_NS" deployment/devboard-backend --tail=160 | grep -Ei 'sql|jdbc|hikari|database|mysql|rds|connection|access denied' || true
kubectl logs -n "$APP_NS" deployment/devboard-event-service --tail=160 | grep -Ei 'sql|jdbc|hikari|database|mysql|rds|connection|access denied' || true
```

Check current database configuration:

```bash
kubectl get configmap devboard-backend-config -n "$APP_NS" -o yaml
kubectl get configmap devboard-event-service-config -n "$APP_NS" -o yaml
kubectl get secret -n "$APP_NS"
```

## Diagnosis

Classify the failure:

| Symptom | Likely cause | Check |
| --- | --- | --- |
| `Access denied` | wrong username/password or rotated secret | Kubernetes secret and RDS user |
| timeout to RDS hostname | security group, subnet, route, or RDS stopped | AWS RDS status and network rules |
| unknown host | wrong endpoint in configmap | `DATABASE_URL` value |
| pool exhausted | slow queries or too little DB capacity | backend logs and RDS metrics |
| migration error | schema change failure | app startup logs and Liquibase output |

Check DNS and TCP reachability from a running app pod:

```bash
kubectl exec -n "$APP_NS" deployment/devboard-backend -- sh -c 'echo "$DATABASE_URL"'
kubectl exec -n "$APP_NS" deployment/devboard-backend -- sh -c 'getent hosts devboard-dev-eks-db.ctigw2agmnko.ap-southeast-2.rds.amazonaws.com'
kubectl exec -n "$APP_NS" deployment/devboard-backend -- sh -c 'nc -vz devboard-dev-eks-db.ctigw2agmnko.ap-southeast-2.rds.amazonaws.com 3306'
```

If the image does not include `getent` or `nc`, use the logs plus a temporary
debug pod in the same namespace:

```bash
kubectl run mysql-network-check -n "$APP_NS" --rm -it --image=busybox:1.36 --restart=Never -- sh
nslookup devboard-dev-eks-db.ctigw2agmnko.ap-southeast-2.rds.amazonaws.com
nc -vz devboard-dev-eks-db.ctigw2agmnko.ap-southeast-2.rds.amazonaws.com 3306
```

Check AWS-side status if RDS is the database:

```bash
aws rds describe-db-instances --query 'DBInstances[].{id:DBInstanceIdentifier,status:DBInstanceStatus,endpoint:Endpoint.Address}'
```

## Recovery

If EKS credentials changed, update the AWS Secrets Manager secret that backs
`devboard-backend-secret`. External Secrets Operator will refresh the Kubernetes
secret; restart the affected deployments if they need to reload environment
variables immediately:

```bash
aws secretsmanager put-secret-value \
  --secret-id devboard/dev/backend \
  --secret-string '{"DATABASE_PASSWORD":"<password>"}'

kubectl rollout restart deployment/devboard-backend -n "$APP_NS"
kubectl rollout restart deployment/devboard-event-service -n "$APP_NS"
kubectl rollout status deployment/devboard-backend -n "$APP_NS"
kubectl rollout status deployment/devboard-event-service -n "$APP_NS"
```

If the RDS instance is stopped, start it:

```bash
aws rds start-db-instance --db-instance-identifier <db-instance-id>
aws rds wait db-instance-available --db-instance-identifier <db-instance-id>
```

If network rules changed, restore EKS-to-RDS access in Terraform rather than
patching security groups by hand. After applying Terraform, restart app pods so
connection pools reinitialize cleanly.

If the latest app release caused a migration or query failure, use
[Rollback Procedure](rollback-procedure.md) and plan a forward fix.

## Validation

```bash
kubectl port-forward -n "$APP_NS" svc/devboard-backend 8080:8080
curl -fsS http://localhost:8080/api/health
curl -fsS http://localhost:8080/actuator/health

kubectl port-forward -n "$APP_NS" svc/devboard-event-service 8081:8081
curl -fsS http://localhost:8081/api/health
```

Check that errors stopped:

```bash
kubectl logs -n "$APP_NS" deployment/devboard-backend --since=5m
kubectl logs -n "$APP_NS" deployment/devboard-event-service --since=5m
```

## Follow-Up

- Move hardcoded database endpoints toward environment-specific values.
- Add a database connectivity smoke test after deployment.
- Document RDS start/stop schedule if cost-saving automation is enabled.
- Review backup and restore readiness after any serious database incident.
