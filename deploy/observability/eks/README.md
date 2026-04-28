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
sum(kafka_topic_partition_current_offset{topic="devboard.tasks"})
sum(increase(spring_kafka_listener_seconds_count{job="devboard-event-service",result="success"}[$__range]))
up
```

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
