# DevBoard 深入学习 Kubernetes / AWS Cloud Feature Plan

## 目标

通过在现有 DevBoard 项目中新增一组「可落地、可演示、可运维」的云原生功能，系统化提升你在 Kubernetes 与 AWS Cloud 的实战能力。

---

## 现状（基于仓库结构）

你当前项目已经具备很好的基础：
- 多服务架构（backend + event-service + frontend）
- K8s base/overlay（local + eks）
- 观测性栈（Prometheus/Grafana/告警规则）
- EKS + GitOps 相关文档和流水线雏形

这意味着你非常适合进入下一阶段：**平台工程能力 + 生产级可靠性能力**。

---

## 建议优先实现的 6 个 Feature（按学习收益排序）

## Feature 1: External Secrets + AWS Secrets Manager

### 你会学到
- IAM Roles for Service Accounts (IRSA)
- Secrets Manager 与 K8s Secret 同步机制
- GitOps 下密钥治理最佳实践

### 实现范围
- 在 EKS 安装 External Secrets Operator
- 把 `devboard-backend-secret` 从手工创建改为 ExternalSecret
- 数据库密码、JWT Secret、Kafka 凭据统一托管在 Secrets Manager

### 验收标准
- `kubectl get externalsecret -n devboard` 状态 `Ready=True`
- Pod 重建后能自动拉取最新密钥
- Git 仓库中不再需要明文/手工注入密钥步骤

---

## Feature 2: Progressive Delivery（Argo Rollouts + ALB/Nginx）

### 你会学到
- Canary / Blue-Green 发布策略
- 指标驱动自动回滚
- 发布风险控制与 SLO 思维

### 实现范围
- backend 切换为 Rollout 资源
- 10% -> 30% -> 100% 金丝雀流量策略
- 配置 Prometheus 指标门禁（5xx、p95 latency）

### 验收标准
- 触发新版本发布时可看到分阶段流量切换
- 指标超阈值自动中止 rollout
- 有可复用的发布 runbook

---

## Feature 3: Event-driven Autoscaling（KEDA + Kafka Lag）

### 你会学到
- 基于业务负载的弹性策略（不是仅 CPU）
- Kafka lag 指标语义与消费能力建模
- HPA/KEDA 与稳定性权衡

### 实现范围
- 给 `event-service` 增加 KEDA ScaledObject
- 使用 Kafka lag 作为扩缩容信号
- 设置冷却时间、最小副本、防抖参数

### 验收标准
- 制造消息堆积时副本数自动增长
- backlog 消退后副本数回落
- 不出现频繁抖动（thrashing）

---

## Feature 4: Multi-environment GitOps Promotion（dev -> stage -> prod）

### 你会学到
- 环境分层与配置漂移控制
- 镜像晋升（promotion）而非“每环境重新构建”
- 审批门禁与可追溯性

### 实现范围
- 新增 `deploy/k8s/overlays/stage`、`overlays/prod`
- 约定镜像标签晋升流程（例如 commit SHA）
- Jenkins / GitHub Actions 增加 promotion job

### 验收标准
- 同一镜像 digest 可从 dev 晋升到 prod
- 每次发布都可追踪 commit/tag/变更人
- 回滚只需回退 overlay 引用版本

---

## Feature 5: SLO + Error Budget + Alert Tuning

### 你会学到
- 从“有监控”升级为“有可靠性目标”
- 告警降噪（减少误报）
- 以用户体验定义系统健康

### 实现范围
- 给 backend 设定可量化 SLO（例如 99.5% 可用性）
- 按 burn-rate 设计多窗口告警
- Grafana 增加 SLO 看板

### 验收标准
- 能展示 7 天 / 30 天 SLO 达成率
- 告警与 runbook 一一映射
- 演练期间能根据 error budget 做发布决策

---

## Feature 6: Cost-aware Platform（成本可观测 + 资源治理）

### 你会学到
- requests/limits 与成本、稳定性的关系
- 集群成本归因（namespace/workload）
- FinOps 基础实践

### 实现范围
- 全服务补齐 requests/limits
- 安装 Kubecost（或 OpenCost）
- 给 devboard namespace 建成本看板

### 验收标准
- 能定位高成本 workload
- 能给出至少 2 条降本建议（含性能影响评估）
- 成本数据可进入周报/复盘

---

## 12 周学习与落地节奏（建议）

### Phase 1（Week 1-4）基础治理
1. External Secrets
2. 多环境 overlay 分层
3. SLO 初版与告警清理

### Phase 2（Week 5-8）发布与弹性
4. Argo Rollouts 金丝雀
5. KEDA Kafka Lag 扩缩容
6. 故障演练（回滚、限流、降级）

### Phase 3（Week 9-12）平台化与复盘
7. 成本治理看板
8. 平台 runbook 补全
9. 形成面试/汇报材料（架构图+指标提升）

---

## 建议从哪一个开始？

如果你希望**最快提升 AWS + K8s 的面试竞争力**：
1) 先做 **Feature 1 (External Secrets)**
2) 再做 **Feature 2 (Progressive Delivery)**
3) 第三个做 **Feature 3 (KEDA)**

这个组合最能体现“安全、稳定、弹性”三条主线，也最接近真实生产场景。

---

## 交付物清单（每个 Feature 都建议有）

- 架构图（变更前后）
- K8s Manifests / Helm values
- CI/CD 流水线变更
- 监控看板与告警规则
- 一页 runbook（故障定位 + 回滚步骤）
- Demo 脚本（5~10 分钟）

这样你不仅“做了功能”，还会沉淀成完整的平台工程案例。
