# EKS Observability

This installs the DevBoard EKS observability stack:

- Prometheus and Grafana via `prometheus-community/kube-prometheus-stack`
- Kafka consumer group lag via `prometheus-community/prometheus-kafka-exporter`
- ServiceMonitors for backend and event-service Spring Boot Actuator metrics
- A Grafana dashboard for Kafka consumer group lag

The Jenkins EKS deploy pipeline installs this automatically after Kafka is installed.

Manual install:

```bash
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts --force-update
helm repo update

helm upgrade --install devboard-monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --wait \
  --timeout 20m \
  -f deploy/observability/eks/kube-prometheus-stack-values.yaml

helm upgrade --install devboard-kafka-exporter prometheus-community/prometheus-kafka-exporter \
  --namespace monitoring \
  --wait \
  --timeout 20m \
  -f deploy/observability/eks/kafka-exporter-values.yaml

kubectl apply -k deploy/observability/eks
```

Open Grafana locally:

```bash
kubectl port-forward -n monitoring svc/devboard-monitoring-grafana 3001:80
```

Then browse to `http://localhost:3001` and log in with `admin / admin`.

Open Alertmanager locally:

```bash
kubectl port-forward -n monitoring svc/devboard-monitoring-kube-p-alertmanager 9093:9093
```

Then browse to `http://localhost:9093`.

Alertmanager is enabled with a `demo-null` receiver by default. This gives the
interview/demo stack a working notification route without committing Slack or
SMTP credentials.

Useful PromQL:

```promql
sum by (consumergroup, topic) (kafka_consumergroup_lag)
sum(kafka_topic_partition_current_offset{topic="devboard.tasks"})
sum(increase(spring_kafka_listener_seconds_count{job="devboard-event-service",result="success"}[$__range]))
up
```

View active alerts from the CLI:

```bash
kubectl port-forward -n monitoring svc/devboard-monitoring-kube-p-prometheus 9090:9090
curl -fsS 'http://localhost:9090/api/v1/alerts'
curl -fsS 'http://localhost:9093/api/v2/alerts'
```

DevBoard custom alerts are installed by `application-alert-rules.yaml`,
`kafka-alert-rules.yaml`, and `http-alert-rules.yaml`:

- `DevBoardBackendUnavailable`
- `DevBoardEventServiceUnavailable`
- `DevBoardFrontendUnavailable`
- `DevBoardPodRestarting`
- `DevBoardHighContainerCpu`
- `DevBoardHighContainerMemory`
- `DevBoardKafkaConsumerLagHigh`
- `DevBoardKafkaNoMessagesConsumed`
- `DevBoardKafkaExporterDown`
- `DevBoardKafkaListenerErrors`
- `DevBoardBackendHighErrorRate`
- `DevBoardBackendHighLatency`
- `DevBoardActuatorScrapeFailure`
- `DevBoardServiceUnavailable`

Check whether Prometheus loaded the rules:

```bash
curl -fsS 'http://localhost:9090/api/v1/rules' | grep DevBoard
```

Validate pod restart alerting during a demo:

```bash
kubectl delete pod -n devboard -l app=devboard-event-service
kubectl rollout status deployment/devboard-event-service -n devboard
curl -fsS 'http://localhost:9090/api/v1/alerts' | grep DevBoardPodRestarting
```

The restart alert uses a `for: 5m` window, so it may take a few minutes to move
from pending to firing in Alertmanager.

Create a temporary silence during demos:

```bash
amtool --alertmanager.url=http://localhost:9093 silence add alertname=Watchdog \
  --duration=2h \
  --comment='demo silence' \
  --author='devboard-demo'
```

List and expire silences:

```bash
amtool --alertmanager.url=http://localhost:9093 silence query
amtool --alertmanager.url=http://localhost:9093 silence expire <silence-id>
```

Optional Slack notifications should use a Kubernetes secret, not a committed
webhook URL:

```bash
kubectl create secret generic alertmanager-slack-webhook \
  -n monitoring \
  --from-literal=webhook-url='https://hooks.slack.com/services/...'
```

Then add the secret name under `alertmanager.alertmanagerSpec.secrets` and add
a `slack_configs` receiver that reads:

```text
/etc/alertmanager/secrets/alertmanager-slack-webhook/webhook-url
```

Optional email notifications follow the same pattern: create an SMTP password
secret outside git, mount it through `alertmanager.alertmanagerSpec.secrets`,
and use `auth_password_file` in an `email_configs` receiver.

## Troubleshooting `No data`

If Grafana opens but the Kafka lag panel says `No data`, first verify the Kafka
exporter is seeing brokers and consumer groups:

```bash
kubectl port-forward -n monitoring svc/devboard-kafka-exporter-prometheus-kafka-exporter 9308:9308
curl -fsS http://localhost:9308/metrics | grep -E 'kafka_brokers|kafka_consumergroup_lag'
```

`kafka_brokers 0` or no `kafka_consumergroup_lag` series means the exporter has
nothing for Grafana to plot. Check cluster capacity and Kafka scheduling:

```bash
kubectl get nodes
kubectl get pods -n devboard
kubectl get pods -n monitoring
kubectl describe pod -n devboard devboard-kafka-controller-0
```

The full EKS dev stack needs enough pod capacity for the app, Kafka, ALB
controller, metrics server, and monitoring. The checked-in dev node group uses
three `t3.small` nodes so a single NotReady node does not immediately strand
Kafka or Prometheus.
