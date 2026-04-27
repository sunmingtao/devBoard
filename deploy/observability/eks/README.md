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

Useful PromQL:

```promql
sum by (consumergroup, topic) (kafka_consumergroup_lag)
up
```
