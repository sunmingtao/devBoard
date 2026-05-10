# Kafka Consumer Lag Runbook

## Purpose

Use this when DevBoard events are being produced but the event-service is not
consuming them quickly enough, or not consuming at all.

## Alerts

- `DevBoardKafkaConsumerLagHigh`: consumer group lag for `devboard.tasks` is
  above 50 for 5 minutes.
- `DevBoardKafkaNoMessagesConsumed`: the event-service Kafka listener has not
  recorded successful consumption for 15 minutes.
- `DevBoardKafkaListenerErrors`: the event-service listener recorded one or
  more non-success listener results.
- `DevBoardKafkaExporterDown`: Kafka lag metrics may be unavailable.

## Impact

Task changes can still be accepted by the backend, but downstream event
processing is delayed. The event-service database may not reflect recent task
events, and any event-driven UI or audit view can become stale.

## First Checks

```bash
export APP_NS=devboard
export MONITORING_NS=monitoring

kubectl get pods -n "$APP_NS" -l app=devboard-event-service
kubectl get pods -n "$APP_NS" | grep kafka
kubectl get pods -n "$MONITORING_NS" | grep kafka-exporter
kubectl logs -n "$APP_NS" deployment/devboard-event-service --tail=120
```

Check the live lag metrics:

```bash
kubectl port-forward -n "$MONITORING_NS" svc/devboard-monitoring-kube-p-prometheus 9090:9090

curl -fsS 'http://localhost:9090/api/v1/query?query=sum%20by%20(consumergroup%2Ctopic)%20(kafka_consumergroup_lag%7Btopic%3D%22devboard.tasks%22%7D)'
curl -fsS 'http://localhost:9090/api/v1/query?query=sum(rate(spring_kafka_listener_seconds_count%7Bjob%3D%22devboard-event-service%22%2Cresult%3D%22success%22%7D%5B10m%5D))'
```

## Diagnosis

Check whether the consumer is running:

```bash
kubectl describe deployment devboard-event-service -n "$APP_NS"
kubectl describe pod -n "$APP_NS" -l app=devboard-event-service
kubectl get endpoints devboard-event-service -n "$APP_NS"
```

Check configuration:

```bash
kubectl get configmap devboard-event-service-config -n "$APP_NS" -o yaml
kubectl exec -n "$APP_NS" deployment/devboard-event-service -- printenv | grep -E 'KAFKA|TASK_EVENTS|DATABASE'
```

Check Kafka reachability from the event-service pod:

```bash
kubectl exec -n "$APP_NS" deployment/devboard-event-service -- sh -c 'nc -vz devboard-kafka.devboard.svc.cluster.local 9092'
```

If `nc` is unavailable in the image, use logs, pod events, and Kafka pod status
instead:

```bash
kubectl get pods -n "$APP_NS" | grep kafka
kubectl describe pod -n "$APP_NS" -l app.kubernetes.io/name=kafka
```

## Recovery

If the event-service is unhealthy or stuck, restart it:

```bash
kubectl rollout restart deployment/devboard-event-service -n "$APP_NS"
kubectl rollout status deployment/devboard-event-service -n "$APP_NS"
```

If the latest release introduced listener failures, roll back the GitOps image
tag using [Rollback Procedure](rollback-procedure.md).

If Kafka is unavailable, recover Kafka first:

```bash
kubectl get pods -n "$APP_NS" | grep kafka
kubectl describe pod -n "$APP_NS" -l app.kubernetes.io/name=kafka
kubectl logs -n "$APP_NS" -l app.kubernetes.io/name=kafka --tail=120
```

If lag is high but consumption is healthy, allow the consumer to catch up. Avoid
restarting repeatedly because that can delay progress.

## Validation

Confirm lag is falling:

```bash
curl -fsS 'http://localhost:9090/api/v1/query?query=sum%20by%20(consumergroup%2Ctopic)%20(kafka_consumergroup_lag%7Btopic%3D%22devboard.tasks%22%7D)'
```

Confirm successful listener activity:

```bash
curl -fsS 'http://localhost:9090/api/v1/query?query=sum(increase(spring_kafka_listener_seconds_count%7Bjob%3D%22devboard-event-service%22%2Cresult%3D%22success%22%7D%5B10m%5D))'
```

Confirm alerts resolve:

```bash
curl -fsS 'http://localhost:9093/api/v2/alerts' | grep DevBoardKafka || true
```

## Escalation

Escalate if:

- Kafka pods are not schedulable because the EKS node group lacks capacity.
- Lag continues to increase after the event-service is healthy.
- Listener errors continue after rollback.
- Database writes from event-service are failing after events are consumed.

## Follow-Up

- Add a regression test for the failed event payload if parsing caused the issue.
- Add resource requests or scale the event-service if lag was caused by load.
- Tune alert thresholds after observing normal demo and production traffic.
