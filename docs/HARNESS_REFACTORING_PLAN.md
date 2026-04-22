# Nexvest Harness 精神 CI/CD 重构计划

**版本**：1.0
**创建日期**：2026/04/22
**目标完成**：2026/07/01 ~ 2026/08/31（6-10 周）
**联系人**：Nexvest 核心团队

---

## 📌 总体目标

将 Nexvest 项目的 CI/CD 流程从**被动的代码检查**转变为**主动的持续验证**，符合 Harness 精神的核心理念：
- **每一步都在验证而不是检测**
- **自动化代替手动检查**
- **生产就绪是默认状态，而非例外**

### 核心问题分析

| 当前问题 | 影响 | 优先级 |
|--------|------|--------|
| **零测试覆盖** | 无法保证代理稳定性，盲目部署 | 🔴 P0 |
| **升级通知是 stub** | 线上告警无法自动响应 | 🔴 P0 |
| **Harness 检查被注释** | PR 无法验证生产就绪标准 | 🟡 P1 |
| **部署流程缺失** | 无法自动化部署到 K8s | 🟡 P1 |
| **熵管理仅 dry-run** | 无法真正管理代理行为退化 | 🟡 P2 |

### 重构后收益预期

| 指标 | 当前 | 目标 | 提升 |
|------|------|------|------|
| **代码覆盖率** | 0% | 70%+ | 🟢 100% 改善 |
| **PR 自动检查失败率** | 手动（0%）| 自动门控（5-10%） | 🟢 更早发现问题 |
| **升级通知自动化** | 0% | 100% P1/P2/P3 | 🟢 SLA 15min 内响应 |
| **生产部署时间** | 手动（30 min） | 自动（5 min） | 🟢 6 倍加速 |
| **基础设施代码化** | 0%（无 IaC） | 100%（Helm+Kustomize） | 🟢 可追踪、可版本化 |

---

## 🎯 分阶段重构计划

### 第 1 阶段：本地开发体系建立（W1-W2）

**目标**：让开发者在提交前就能发现问题，建立基础测试框架

**为什么做**：
- 减轻 CI 负担，快速反馈给开发者
- 统一开发环境，保证本地和 CI 环境一致
- 为后续的 Harness 检查奠定基础（需要测试存在）

**关键任务**：

| 任务 | 产物 | 预期效果 |
|------|------|--------|
| 创建 `.pre-commit-config.yaml` | 本地钩子配置 | `git commit` 前自动检查 (black、flake8、isort、markdown linting) |
| 创建 `pyproject.toml` | 统一工具配置 | black、isort、flake8、pytest、coverage 集中配置，降低配置分散 |
| 创建 `pytest.ini` | 测试框架配置 | pytest 执行规则、覆盖率阈值（70%）、输出格式 |
| 编写单元测试套件 | `tests/unit/test_*.py` | 3 个核心模块的测试（loop_detection、entropy_agent、reasoning_optimizer） |
| 本地验证 | CI 绿灯 | 所有检查通过，覆盖率 ≥70% |

**交付物清单**：
```
.pre-commit-config.yaml
pyproject.toml
pytest.ini
tests/
├── unit/
│   ├── __init__.py
│   ├── test_loop_detection.py      (回圈检测逻辑)
│   ├── test_entropy_agent.py        (熵管理代理)
│   ├── test_reasoning_optimizer.py  (推理优化中间件)
│   └── conftest.py                  (pytest fixtures)
└── __init__.py
```

**验收标准**：
- ✅ `pre-commit run --all-files` 全部通过
- ✅ `pytest --cov=tools --cov-report=term-missing` 显示 ≥70% 覆盖率
- ✅ `black --check .` 通过
- ✅ `flake8` 无错误

**预期里程碑**：
- Day 2：配置文件完成
- Day 5：单元测试框架完成
- Day 10：本地验证通过

**风险与对策**：
| 风险 | 对策 |
|------|------|
| 难以达到 70% 覆盖率 | 优先覆盖关键路径（happy path + error cases），逐步迭代 |
| 本地环境差异导致测试失败 | 使用 Python 3.10/3.11 tox 多版本测试 |

---

### 第 2 阶段：激活 Harness 自动化门控（W2-W3）

**目标**：让每个 PR 都自动验证 Level 3 生产就绪标准

**为什么做**：
- Harness 精神要求代码必须符合生产级别标准
- 自动检查替代人工审查，减少遗漏
- 文档和代码保持同步，避免 AGENTS_LEVEL3.md 过时

**关键任务**：

| 任务 | 产物 | 预期效果 |
|------|------|--------|
| 激活 `harness-checks` job | 改写 .github/workflows/agent-ci.yml | 所有 PR 自动运行生产就绪检查（不需要标签） |
| 创建生产就绪验证脚本 | `scripts/validate_harness_readiness.py` | 自动检查 Level 3 文档、中间件接口、可观测性端点 |
| 关键文件修改时强制检查 | 流程规则 | 修改 `tools/agents/` 时必须有单元测试 |
| 重构 workflow 顺序 | .github/workflows/agent-ci.yml | lint-and-test → harness-checks（分层加速） |

**交付物清单**：
```
.github/workflows/
├── agent-ci.yml              (改写：激活 harness-checks，改为无条件执行)
└── (新增或改写后续 workflows)

scripts/
└── validate_harness_readiness.py  (生产就绪验证脚本)
```

**验收标准**：
- ✅ PR 修改 `tools/agents/entropy_agent.py` 时，CI 强制要求有对应的单元测试
- ✅ PR 修改 docs 时，AGENTS_LEVEL3.md 变更会被记录
- ✅ `harness-checks` job 对所有 PR 运行（不需要 `harness` 标签）
- ✅ PR 失败时，失败原因清晰（例：缺少文档）

**预期里程碑**：
- Day 11-13：workflow 改写 + 验证脚本完成
- Day 14：在实际 PR 上验证工作

**风险与对策**：
| 风险 | 对策 |
|------|------|
| 检查过严格导致 PR 频繁失败 | 调整检查规则，从 MUST-HAVE 到 NICE-TO-HAVE 分级 |
| Harness 检查与基础 lint 冲突 | 明确职责边界：lint = 代码格式，harness = 生产就绪 |

---

### 第 3 阶段：升级自动化 + Discord 通知（W3-W4，可与阶段 2 并行）

**目标**：将升级策略从文档变为自动化事件响应

**为什么做**：
- 线上告警（来自 Prometheus）必须自动化响应，不能等人工
- Discord 通知是核心 DevOps 沟通渠道
- P1/P2/P3 分级保证 SLA（P1 15min 内响应）

**关键任务**：

| 任务 | 产物 | 预期效果 |
|------|------|--------|
| 实现 Discord 集成 | 改写 .github/workflows/agent-escalation.yml | 告警触发 → Discord 消息发送（支持多频道分级） |
| 定义升级触发条件 | Prometheus 告警规则 | error_rate > 5% (P1)、latency p99 > 2s (P2)、低频错误 (P3) |
| 实现事件审计日志 | 日志系统 | 记录升级时间、原因、响应人，用于事后分析 |
| Discord Webhook 配置 | GitHub Secrets | 安全存储 Discord webhook URL，支持多频道 |

**交付物清单**：
```
.github/workflows/
└── agent-escalation.yml       (实现真实升级逻辑，Discord 集成)

tools/
└── agents/
    └── escalation/
        └── escalation_handler.py  (升级事件处理，Discord 通知)

configs/
└── prometheus-alerts.yml      (告警规则：P1/P2/P3)
```

**验收标准**：
- ✅ 模拟 Prometheus 告警，Discord 消息在 30 秒内发送
- ✅ P1 告警发送到 #nexvest-critical 频道
- ✅ P2 告警发送到 #nexvest-warnings 频道
- ✅ 升级事件记录到审计日志（可查询）

**预期里程碑**：
- Day 14-15：Discord Webhook 配置完成
- Day 16-17：升级处理逻辑完成
- Day 18：在测试环境验证

**风险与对策**：
| 风险 | 对策 |
|------|------|
| Discord 通知过于频繁导致疲劳 | 实现告警聚合和去重，避免重复通知 |
| Webhook 失败导致消息丢失 | 实现重试机制（exponential backoff）+ 本地日志备份 |

---

### 第 4a 阶段：本地 K8s 部署基础设施准备（W4-W5）

**目标**：准备本地 K8s 集群部署所需的基础设施

**为什么做**：
- 为第 4b 阶段的实际部署奠定基础
- 选定 Helm + Kustomize 方案，标准化部署流程
- 准备镜像仓库、命名空间、存储等基础设施

**关键任务**（与用户协作）：

| 任务 | 产物 | 预期效果 |
|------|------|--------|
| 准备 K8s 集群环境 | kubeconfig、命名空间 | `kubectl config use-context` 可用，`nexvest-agents` 命名空间存在 |
| 设置 Docker Registry 访问 | 凭证配置 | CI 可以 push 镜像到本地 registry |
| 准备存储类（StorageClass） | K8s StorageClass | Prometheus/Grafana 可以申请 PVC |
| 设置 Ingress Controller | Ingress 配置 | Service 可以通过 Ingress 暴露 |

**交付物清单**：
```
K8s 集群配置
├── kubeconfig（已就位）
├── nexvest-agents namespace
├── Docker Registry 凭证（已配置）
├── StorageClass 定义（用于 PVC）
└── Ingress Controller（nginx/traefik）

文档
└── docs/DEPLOYMENT_SETUP.md  (部署基础设施检查清单)
```

**验收标准**：
- ✅ `kubectl get namespaces | grep nexvest-agents` 返回 nexvest-agents
- ✅ `kubectl auth can-i create pods --namespace nexvest-agents` 返回 yes
- ✅ `docker push <registry>/test:latest` 成功
- ✅ `kubectl get sc` 返回至少一个可用的 StorageClass

**预期里程碑**：
- Day 19-21：K8s 环境检查完成
- Day 22-25：Helm 目录结构准备完成

**风险与对策**：
| 风险 | 对策 |
|------|------|
| 本地 K8s 网络配置复杂 | 使用 kubectl port-forward 临时方案，后续升级 Ingress |
| 镜像仓库认证问题 | 预先配置 imagePullSecrets，参考 K8s docs |

---

### 第 4b 阶段：K8s 部署流程 + 熵管理生产化（W5-W7）

**目标**：建立完整的本地 K8s 部署流程，实现生产就绪

**为什么做**：
- 自动化部署是 Harness 精神的终极目标
- 熵管理需要真实执行，而不是 dry-run
- 完整的可观测性堆栈（Prometheus + Grafana + Loki）支撑监控和告警

**关键任务**：

| 任务 | 产物 | 预期效果 |
|------|------|--------|
| 建立 Helm 部署清单 | `manifests/helm/nexvest-agent/` | `helm install nexvest ...` 可以部署到 K8s |
| 建立 Kustomize 覆盖 | `manifests/kustomize/overlays/prod/` | 支持 dev/staging/prod 环境定制 |
| 实现部署 workflow | `.github/workflows/agent-deploy.yml` | merge main → 自动部署到 K8s（全自动） |
| 升级 entropy-agent | `tools/agents/entropy/entropy_agent.py` | 真实修改 ConfigMap/Secret，不仅 dry-run |
| 部署可观测性堆栈 | `manifests/helm/nexvest-observability/` | Prometheus 采集指标，Grafana 展示，Loki 聚合日志 |
| 验证部署健康 | 部署检查脚本 | pod 健康、服务可达、指标采集正常 |

**交付物清单**：
```
manifests/
├── helm/
│   ├── nexvest-agent/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   ├── values-prod.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── configmap.yaml
│   │       ├── secret.yaml
│   │       └── ingress.yaml
│   └── nexvest-observability/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── prometheus-deployment.yaml
│           ├── grafana-deployment.yaml
│           ├── loki-deployment.yaml
│           └── configmaps/
├── kustomize/
│   ├── base/
│   │   └── nexvest/
│   │       ├── kustomization.yaml
│   │       └── manifests (复用或补充)
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── prod/

.github/workflows/
└── agent-deploy.yml         (部署 workflow：main branch)

tools/agents/entropy/
└── entropy_agent.py         (改写：真实执行 ConfigMap 修改)

docs/
├── DEPLOYMENT_GUIDE.md      (部署指南)
└── OBSERVABILITY_SETUP.md   (可观测性堆栈说明)
```

**验收标准**：
- ✅ `helm lint manifests/helm/nexvest-agent/` 通过
- ✅ `helm template nexvest manifests/helm/nexvest-agent/ | kubectl apply -f - --dry-run=client` 成功
- ✅ merge to main → 自动部署到 K8s（pod 运行成功）
- ✅ Prometheus `/metrics` 端点可以被抓取
- ✅ Grafana dashboard 显示实时指标（CPU、Memory、Error Rate）
- ✅ entropy-agent 运行后，ConfigMap 被修改（git diff 可见）

**预期里程碑**：
- Day 26-30：Helm 清单完成，本地 `helm install` 成功
- Day 31-35：可观测性堆栈部署成功
- Day 36-40：部署 workflow 完整验证
- Day 41-45：生产环境测试和文档完善

**风险与对策**：
| 风险 | 对策 |
|------|------|
| 部署失败导致 pod 无法启动 | 实现详细的日志收集和健康检查，快速诊断 |
| 存储相关问题（PVC 挂载失败） | 预先配置 StorageClass，本地测试 PVC 申请 |
| 镜像版本控制混乱 | 使用 semantic versioning + git tag，workflow 自动构建版本号 |

---

## 📊 时间表与里程碑

```
W1   W2   W3   W4   W5   W6   W7   W8   W9   W10
├────┤
   第 1 阶段
        ├────┤
           第 2 阶段
        ├───────┤ (并行)
           第 3 阶段
             ├────┤
                第 4a 阶段
                   ├───────────┤
                      第 4b 阶段 (长周期)
                                    ├────┤
                                    缓冲 + 优化
```

### 关键截止日期

| 阶段 | 开始 | 完成 | 可交付物 |
|------|------|------|--------|
| 第 1 | 2026/04/28 | 2026/05/11 | pytest 70%+ 覆盖率 |
| 第 2 | 2026/05/05 | 2026/05/18 | PR 自动 Harness 检查 |
| 第 3 | 2026/05/05 | 2026/05/25 | Discord 升级通知工作 |
| 第 4a | 2026/05/19 | 2026/06/01 | K8s 部署基础准备就绪 |
| 第 4b | 2026/06/02 | 2026/06/23 | 自动部署到 K8s 成功 |
| 缓冲 | 2026/06/23 | 2026/07/07 | 优化、文档、生产验收 |

---

## 💾 配置管理策略

### Secrets 管理演进路线

**阶段 1-3**（当前）：
```
GitHub Secrets
  └─ workflow env vars
     └─ pod 环境变量 / 挂载
```

**阶段 4a-4b**：
```
GitHub Secrets (外部存储)
  └─ K8s Secret (集群内)
     └─ pod 环境变量
```

**阶段 4c（后续升级，可选）**：
```
HashiCorp Vault / K8s Sealed Secrets
  └─ 更安全的密钥管理
```

### 版本控制策略

**Git Tag**：
- `v1.0.0-alpha` - 阶段 1 完成
- `v1.0.0-beta` - 阶段 2-3 完成
- `v1.0.0-rc1` - 阶段 4a 完成
- `v1.0.0` - 阶段 4b 完成，生产就绪

**Docker 镜像标签**：
- `latest` - main branch 最新镜像
- `stable` - 生产就绪镜像（对应版本 tag）
- `v1.0.0-rc1` - 版本特定镜像

---

## 📋 依赖关系与阻塞项

```
第 1 阶段（测试框架）⬅ 必须先完成
    │
    ├─ 阻塞第 2 阶段？ 是
    │  （harness-checks 依赖测试存在）
    │
    └──────────────→ 第 2 阶段（Harness 自动化）
                    │
                    ├─ 阻塞第 3 阶段？ 否
                    │  （两者独立）
                    │
                    └──────────────→ 第 3 阶段（升级自动化）
                                     │
                                     └──→ 并行（不相互依赖）

    第 4a 阶段（基础准备）
    │ 与前 3 个阶段独立准备
    │
    └──────────────→ 第 4b 阶段（部署 + 熵管理）
                    │ 依赖 1+2+3+4a 全部完成
```

---

## 🎓 学习与参考

**推荐阅读**：
- [Harness 工程指南](https://www.harness.io/) - 持续验证理念
- [Helm 文档](https://helm.sh/docs/) - 部署打包
- [Kustomize 教程](https://kustomize.io/) - 环境定制
- [Prometheus 告警规则](https://prometheus.io/docs/alerting/latest/overview/) - 监控告警

**内部参考文档**：
- `docs/agents/AGENTS_LEVEL3.md` - Level 3 代理标准
- `docs/agents/ESCALATION_POLICY.md` - 升级策略
- `manifests/dev/main.tf` - 当前 Terraform 配置

---

## 📝 更新记录

| 版本 | 日期 | 改动 | 作者 |
|------|------|------|------|
| 1.0 | 2026/04/22 | 初始版本，包含 4 个阶段完整计划 | Nexvest Team |

---

## ❓ 常见问题

**Q: 能否跳过某个阶段？**
A: 不建议。每个阶段都是前一个阶段的基础。第 1 阶段（测试）必须完成，否则第 2 阶段（Harness 检查）无法进行。

**Q: 如果遇到阻塞怎么办？**
A: 记录在 GitHub Issues，标记为 `blocker`，同步核心团队。优先级顺序：P0 > Harness 阶段 > K8s 部署。

**Q: 可以加快时间表吗？**
A: 可以，但需要增加资源投入。建议 4 个阶段平行 2 个团队同时进行（第 1+2 一队，第 3+4 一队）。

**Q: 生产环境部署什么时候开始？**
A: 阶段 4b 完成后（W7），在本地 K8s 验证通过后，可以逐步推至生产环境。

---

## 🚀 下一步

1. **立即行动**：启动第 1 阶段（本地开发体系）
2. **每周同步**：团队每周一 10:00 同步进度
3. **文档更新**：每个阶段完成后更新本文档，记录实际耗时和偏差

---

**文档维护**：本文档由 Nexvest 核心团队维护，定期更新。最后更新时间：2026/04/22 15:30 UTC+8
