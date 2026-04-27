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

* [ ] Add dependencies:

  * [ ] `spring-boot-starter-actuator`
  * [ ] `micrometer-registry-prometheus`
* [ ] Enable endpoint:

  * [ ] `/actuator/prometheus`
* [ ] Verify metrics exposed

---

### Kafka Metrics

* [ ] Enable Kafka consumer metrics
* [ ] Validate key metrics:

  * [ ] `kafka_consumer_records_consumed_total`
  * [ ] `kafka_consumer_records_lag_max`
  * [ ] `kafka_consumer_fetch_latency`

---

## 🥉 Phase 3 — Prometheus + Grafana

### Prometheus

* [ ] Deploy Prometheus (Helm)
* [ ] Configure scrape target:

  * [ ] backend service
  * [ ] event-service
* [ ] Verify metrics collection

---

### Grafana

* [ ] Deploy Grafana
* [ ] Connect Prometheus data source
* [ ] Create dashboard:

  * [ ] Kafka consumer lag
  * [ ] message throughput
  * [ ] error rate

---

## 🏆 Phase 4 — Reliability & Monitoring

### Health Checks

* [ ] Add readinessProbe for Kafka consumer
* [ ] Add livenessProbe for Kafka consumer

---

### Alerts (Optional but High Value)

* [ ] Alert if:

  * [ ] consumer lag > threshold
  * [ ] no messages consumed for X minutes
  * [ ] error rate spikes

---

## 🔥 Phase 5 — Demo Scenario (Interview Killer)

* [ ] Simulate failure:

  * [ ] Stop consumer / kill pod
* [ ] Observe:

  * [ ] lag increases in Grafana
* [ ] Recover:

  * [ ] restart consumer
  * [ ] lag drops

---

## 🎯 Final Outcome

* [ ] Event-driven microservice architecture (Kafka)
* [ ] Real-time observability (Prometheus + Grafana)
* [ ] Self-healing and monitored system (K8s + probes)

---

## 🧠 Key Learning Outcomes

* [ ] Kafka producer/consumer fundamentals
* [ ] Consumer lag monitoring
* [ ] Observability pipeline (metrics → Prometheus → Grafana)
* [ ] Debugging distributed systems
* [ ] Designing resilient microservices

---

## 🚀 Stretch Goals (Optional)

* [ ] Dead Letter Queue (DLQ)
* [ ] Retry mechanism
* [ ] Schema evolution (Avro / JSON schema)
* [ ] Distributed tracing (Jaeger / OpenTelemetry)

---
