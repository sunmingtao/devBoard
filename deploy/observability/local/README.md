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
