# Local Prometheus

This compose file runs Prometheus, Grafana, and Kafka Exporter locally. Prometheus scrapes Spring Boot Actuator metrics from services running inside WSL:

- backend: `http://<wsl-ip>:8080/actuator/prometheus`
- event-service: `http://<wsl-ip>:8081/actuator/prometheus`

Kafka Exporter connects to the local Kafka Docker network and exposes consumer group lag at `http://localhost:9308/metrics`.

Start Kafka first so the shared Docker network exists:

```bash
cd ../../kafka
docker compose up -d
cd ../observability/local
```

Start the apps, then start the observability stack:

```bash
docker compose up -d
```

If WSL restarts, its IP may change. Refresh it with:

```bash
hostname -I | awk '{print $1}'
```

Then update `prometheus.yml` and restart Prometheus:

```bash
docker compose restart prometheus
```

Open Prometheus:

```text
http://localhost:9090
```

Open Grafana:

```text
http://localhost:3001
```

Default login:

```text
admin / admin
```

The `DevBoard Local Observability` dashboard is provisioned automatically in the `DevBoard` folder.

Useful starter queries:

```promql
up
jvm_memory_used_bytes
http_server_requests_seconds_count
kafka_consumer_fetch_manager_records_consumed_total
kafka_consumer_fetch_manager_records_lag_max
kafka_consumergroup_lag
```

Stop the local observability stack:

```bash
docker compose down
```

## Alertmanager on local Kubernetes

The local kube-prometheus-stack values enable Alertmanager with a `demo-null`
receiver. This keeps alerts visible in Prometheus, Grafana, and Alertmanager
without sending external notifications during interview demos.

Install or upgrade the local Kubernetes stack:

```bash
helm upgrade --install devboard-monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --wait \
  --timeout 20m \
  -f deploy/observability/local/kube-prometheus-stack-values.yaml
```

Open Alertmanager locally:

```bash
kubectl port-forward -n monitoring svc/devboard-monitoring-kube-p-alertmanager 9093:9093
```

Then browse to `http://localhost:9093`.

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

Create a temporary demo silence:

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
