# DevBoard Kafka + Observability TODO List

## 🎯 Goal

Extend DevBoard into an **event-driven architecture** using Kafka and implement **observability** with Prometheus and Grafana.

---

## 🥇 Phase 1 — Kafka Integration (Core)

### Backend (Producer)

* [x] Add Kafka dependency to backend (Spring Boot)
* [x] Configure Kafka producer (bootstrap servers, serializers)
* [x] Publish events on key actions:

  * [x] Task created
  * [x] Task updated
* [x] Define event schema (JSON)

  * [x] eventType
  * [x] taskId
  * [x] timestamp
  * [x] userId (optional)

---

### New Microservice (Consumer)

* [x] Create new service: `event-service`
* [x] Add Spring Kafka dependency
* [x] Implement Kafka listener:

  * [x] Subscribe to topic `devboard.tasks`
  * [x] Log consumed events
* [ ] (Optional) Persist events into DB (audit log)

---

### Kafka Infrastructure

* [x] Run Kafka locally (Docker Compose or Bitnami chart)
* [x] Deploy Kafka to EKS (Helm)
* [x] Create topic:

  * [x] `devboard.tasks`

---

## 🥈 Phase 2 — Basic Observability

### Metrics (Micrometer + Actuator)

* [x] Add dependencies:

  * [x] `spring-boot-starter-actuator`
  * [x] `micrometer-registry-prometheus`
* [x] Enable endpoint:

  * [x] `/actuator/prometheus`
* [x] Verify metrics exposed

---

### Kafka Metrics

* [x] Enable Kafka consumer metrics
* [x] Validate key metrics:

  * [x] `kafka_consumer_records_consumed_total`
  * [x] `kafka_consumer_records_lag_max`
  * [x] `kafka_consumer_fetch_latency`

---

## 🥉 Phase 3 — Prometheus + Grafana

### Prometheus

* [x] Deploy Prometheus (Helm)
* [x] Configure scrape target:

  * [x] backend service
  * [x] event-service
* [x] Verify metrics collection

---

### Grafana

* [x] Deploy Grafana
* [x] Connect Prometheus data source
* [x] Create dashboard:

  *[x] Kafka consumer lag
  * [x] message throughput
  * [ ] error rate

### Kafka Exporter
### JMX Exporter

---

## 🏆 Phase 4 — Reliability & Monitoring

### Health Checks

* [x] Add readinessProbe for Kafka consumer
* [x] Add livenessProbe for Kafka consumer

---

### Alerts (Optional but High Value)

* [ ] Alert if:

  * [ ] consumer lag > threshold
  * [ ] no messages consumed for X minutes
  * [ ] error rate spikes

---

## 🔥 Phase 5 — Demo Scenario (Interview Killer)

* [x] Simulate failure:

  * [x] Stop consumer / kill pod
* [x] Observe:

  * [x] lag increases in Grafana
* [x] Recover:

  * [x] restart consumer
  * [x] lag drops

---

## 🎯 Final Outcome

* [x] Event-driven microservice architecture (Kafka)
* [x] Real-time observability (Prometheus + Grafana)
* [x] Self-healing and monitored system (K8s + probes)

---

## 🧠 Key Learning Outcomes

* [x] Kafka producer/consumer fundamentals
* [x] Consumer lag monitoring
* [x] Observability pipeline (metrics → Prometheus → Grafana)
* [x] Debugging distributed systems
* [x] Designing resilient microservices

---

## 🚀 Stretch Goals (Optional)

* [ ] Dead Letter Queue (DLQ)
* [ ] Retry mechanism
* [ ] Schema evolution (Avro / JSON schema)
* [ ] Distributed tracing (Jaeger / OpenTelemetry)

---
