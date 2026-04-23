# Nexvest Harness 精神 CI/CD 重构计划

**版本**：2.0（AI-First 重构）
**创建日期**：2026/04/22
**修订日期**：2026/04/23
**目标完成**：2026/07/01 ~ 2026/08/31（7-11 周，含 AI Service 部署）
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

### 🏗️ 第 0 阶段：部署 AI Inference Service（W0，第 1 周前）

**目标**：在 K8s 集群中部署本地 AI 推理服务，为后续的 AI 驱动检查奠定基础

**为什么做**：
- 第 1-4 阶段的所有 AI 能力都依赖此服务（熵分析、风险评分、升级决策、部署评估）
- 使用本地推理引擎（Ollama）降低成本，避免外部 API 依赖
- 配置动态切换机制，未来可灵活改为 OpenAI/Azure 等

**关键任务**：

| 任务 | 产物 | 预期效果 |
|------|------|--------|
| 准备 Ollama 容器镜像 | Dockerfile（选用官方） | K8s 可以 pull ollama 镜像 |
| 创建 Helm 部署清单 | `manifests/helm/nexvest-ai-inference/` | `helm install` 可一键部署 AI Service |
| 配置模型下载 | init-container | Pod 启动时自动下载 llama2:7b 模型 |
| 创建 AI 配置文件 | `config/ai_backend.yaml` | 支持 ollama/openai/azure 动态切换 |
| 验证 AI Service 可用 | HTTP 端点测试 | `curl http://nexvest-ai:8000/api/generate` 返回 200 |

**交付物清单**：
```
manifests/
└── helm/
    └── nexvest-ai-inference/
        ├── Chart.yaml
        ├── values.yaml              # Ollama 配置：模型选择、资源限制
        ├── values-prod.yaml         # 生产配置（可选）
        └── templates/
            ├── deployment.yaml      # Ollama Pod（GPU/CPU 配置）
            ├── service.yaml         # HTTP Service（端口 8000）
            ├── pvc.yaml            # 模型存储（通常 8-15GB）
            ├── configmap.yaml      # 模型参数配置
            └── init-container.yaml # 模型拉取脚本

config/
├── ai_backend.yaml             # 后端选择（ollama/openai/azure）
├── ai_harness_config.yaml      # 风险阈值 + 权重配置
└── risk_profiles.yaml          # 严重/高/中/低风险定义

docs/
└── AI_SERVICE_SETUP.md         # AI Service 部署和使用指南
```

**验收标准**：
- ✅ `helm install nexvest-ai manifests/helm/nexvest-ai-inference/` 成功
- ✅ `kubectl get pods -n nexvest-agents | grep nexvest-ai` 显示 Running 状态
- ✅ `curl http://nexvest-ai-inference:8000/api/tags` 返回可用模型列表（包括 llama2:7b）
- ✅ `curl -X POST http://nexvest-ai-inference:8000/api/generate -d '{"model":"llama2:7b","prompt":"test"}'` 返回有效响应
- ✅ `config/ai_backend.yaml` 配置正确，provider 指向 ollama

**资源占用**：
- **Pod 资源**：2-4 CPU + 8-16GB RAM（取决于模型大小）
- **存储**：10-20GB PVC（模型存储 8-15GB + 缓存）
- **网络**：内部 K8s 通信，无外部流量

**预期里程碑**：
- Day 1-2：Helm Chart 准备
- Day 3：模型下载并验证
- Day 4：HTTP API 测试通过

**风险与对策**：
| 风险 | 对策 |
|------|------|
| 模型下载超时（15GB 可能需要 10+ 分钟） | 预先下载模型到本地镜像或使用 initContainer 超时配置 |
| 内存不足导致 OOM | 使用 llama2:7b 而非 13B，监控内存使用 |
| 模型首次推理慢（冷启动可能 10+ 秒） | 设置合理的 timeout（30 秒），使用连接池复用 |

**后续升级路径**：
```yaml
# 初期：本地 Ollama
provider: "ollama"
endpoint: "http://nexvest-ai-inference:8000"
model: "llama2:7b"

# 3 个月后：可改为 OpenAI（无需改代码）
provider: "openai"
api_key: "${OPENAI_API_KEY}"
model: "gpt-4"
```

---

### 第 1 阶段：AI 驱动的本地开发体系（W1-W2）

**目标**：在本地开发中激活 AI 能力，让开发者在提交前获得智能反馈

**前置条件**：第 0 阶段 AI Service 已部署，本地可通过 HTTP 调用

**为什么做**：
**目标**：在本地开发中激活 AI 能力，让开发者在提交前获得智能反馈

**前置条件**：第 0 阶段 AI Service 已部署，本地可通过 HTTP 调用

**为什么做**：
- 开发者获得实时的 AI 驱动反馈（不仅是静态检查）
- AI 评估熵变化、循环风险、推理配置建议（不是硬编码规则）
- 建立从本地到 CI 的一致的 AI 驱动检查体验

**关键任务**：

| 任务 | 产物 | 预期效果 |
|------|------|--------|
| 包装 AI Service 客户端 | `tools/agents/ai_inference/ai_client.py` | 本地脚本可便利地调用 AI Service |
| 创建本地 AI 检查钩子 | 改写 `.pre-commit-config.yaml` | `git commit` 前自动调用 AI 分析 |
| 实现风险评分逻辑 | `tools/agents/ai_inference/risk_assessor.py` | 根据 AI 返回的信号计算风险分数 |
| 实现 prompt 构建器 | `tools/agents/ai_inference/prompt_builder.py` | 将代码改动转换为 AI 可理解的 prompt |
| 配置动态加载 | `tools/agents/ai_inference/config_manager.py` | 读取 config/ai_harness_config.yaml 动态调整 |

**新增的关键技术**：

1. **AI 风险分类（四层）**
   ```
   CRITICAL  (0.95+)  → ❌ error 阻挡（代码不能提交）
   HIGH      (0.75+)  → ❌ error 阻挡（初期基准）
   MEDIUM    (0.50+)  → ⚠️  warning（可提交，但有风险提示）
   LOW       (0.25+)  → ℹ️  info（提示，开发者可忽略）

   初期阈值配置：acceptable_risk_level = "high"
   （即只有 CRITICAL 和 HIGH 才阻挡，MEDIUM/LOW 仅警告）
   ```

2. **AI 驱动的本地检查流程**
   ```
   git commit
     ↓
   pre-commit triggers
     ↓
   [Stage 1: 基础检查]
     • black / isort / flake8
     • pytest coverage > 70%
   ↓
   [Stage 2: AI 分析]  ← 调用 AI Service
     • 发送代码改动到 Ollama
     • 获取风险评分：entropy / loop / reasoning
     • 计算综合分数
   ↓
   Decision:
     • 综合分数 > 0.85 → ✅ 通过
     • HIGH 或 CRITICAL 风险 → ❌ 阻挡（给出改进建议）
     • MEDIUM/LOW → ⚠️ 警告（可继续提交）
   ```

**交付物清单**：
```
.pre-commit-config.yaml
  ├── black / isort / flake8（原有）
  └── 新增钩子：
      └── ai-driven-checks
          ├── 调用 ai_client.py
          ├── 发送代码改动到 AI Service
          ├── 接收风险评分
          └── 根据阈值决定 error/warning/info

tools/agents/ai_inference/
├── __init__.py
├── ai_client.py              # HTTP 客户端，调用 AI Service
├── risk_assessor.py          # 风险评分逻辑（调用 AI 获得信号）
├── prompt_builder.py         # 构建发送给 AI 的 prompt
└── config_manager.py         # 动态读取配置文件

config/
├── ai_backend.yaml           # 后端选择（ollama/openai）
├── ai_harness_config.yaml    # 权重、阈值、可接受风险等级
└── risk_profiles.yaml        # 风险等级定义（CRITICAL/HIGH/MEDIUM/LOW）

tests/unit/
└── test_ai_inference/        # AI 模块的单元测试
    ├── test_ai_client.py
    ├── test_risk_assessor.py
    └── test_prompt_builder.py
```

**验收标准**：
- ✅ `pre-commit run --all-files` 全部通过（含 AI 检查）
- ✅ AI 检查能正确调用 AI Service（可通过 mock 测试）
- ✅ 风险评分能正确计算（CRITICAL/HIGH/MEDIUM/LOW）
- ✅ 高于阈值的风险被标记为 error，阻止提交
- ✅ 低于阈值的风险被标记为 warning，允许提交
- ✅ AI 建议清晰易懂（例："entropy 上升建议分解函数"）

**预期里程碑**：
- Day 6-8：AI 客户端和 prompt 构建器完成
- Day 9-10：风险评分逻辑完成并与 AI Service 集成
- Day 11-12：本地测试通过，开发者可使用

**风险与对策**：
| 风险 | 对策 |
|------|------|
| AI 响应超时导致 pre-commit 卡住 | 设置 30 秒超时，失败时降级为 warning（不阻挡） |
| AI 评分不准确导致误报 | 初期 acceptable_risk_level="high"（宽松），逐步收严 |
| 网络连接问题（AI Service 不可达） | 本地缓存上次评分，或配置回退行为 |

---

### 第 2 阶段：AI 驱动的 Harness 自动门控（W2-W3）

**交付物清单**：
```
.github/workflows/
├── agent-ci.yml              (改写：激活 harness-checks，改为无条件执行)
└── (新增或改写后续 workflows)

scripts/
└── validate_harness_readiness.py  (生产就绪验证脚本)
```

**目标**：在 GitHub Actions 中激活 AI 驱动的自动门控，让每个 PR 都通过 AI 评估的生产就绪性检查

**前置条件**：
- 第 0 阶段 AI Service 已部署
- 第 1 阶段本地 AI 检查已验证

**为什么做**：
- CI 层面的 AI 驱动决策，比本地检查更严格
- 综合评分（code_quality + entropy_safety + loop_safety）判断 PR 是否生产就绪
- 不仅检查"有没有问题"，更重要的是"有什么风险"和"怎么改"

**关键任务**：

| 任务 | 产物 | 预期效果 |
|------|------|--------|
| 改写 CI workflow | `.github/workflows/agent-ci.yml` | PR 提交 → 自动运行 AI 门控检查 |
| 实现 AI 综合评分 | `scripts/ai_harness_gates.py` | 基于多维度信号计算生产就绪分数（0-1） |
| 集成 AI Service 调用 | 在 workflow 中调用 AI Service | 评估代码改动的风险 |
| 生成 PR 评论报告 | 改写 workflow 生成 PR comment | 开发者可在 PR 上看到 AI 分析报告 |
| 配置 PR 合并规则 | GitHub branch protection | 只有通过 AI 门控的 PR 才能合并 |

**新的 CI 流程**：
```
PR 提交到 GitHub
  ↓
[Stage 1: 基础检查]（3-5min）
  • pytest coverage > 70%
  • black / isort / flake8 通过
  ↓
[Stage 2: AI 驱动的 Harness 门控]（3-5min）← 依赖 AI Service
  • 发送 PR diff 到 Ollama
  • AI 分析：代码质量、熵安全、循环安全
  • 计算综合分数 = w1×code_quality + w2×entropy + w3×loop
  ↓
[Decision]
  • 综合分数 >= 0.85 且无 CRITICAL/HIGH 风险
    → ✅ PR 可以合并，自动标记为 approved
  • 有 HIGH/CRITICAL 风险
    → ❌ PR 阻挡，生成详细改进建议，开发者修改后重试
  • 综合分数 < 0.85（但无高风险）
    → ⚠️  PR 标记为需审查，提示人工审核
```

**交付物清单**：
```
.github/workflows/
└── agent-ci.yml（改写）
    ├── Stage 1: lint-and-test（原有）
    └── Stage 2: ai-harness-gates（新增）
        ├── 调用 AI Service
        ├── 计算综合评分
        ├── 生成 PR comment（AI 分析报告）
        └── 设置合并状态（approve/block/review_required）

scripts/
└── ai_harness_gates.py      # AI 门控评分脚本
    ├── 接收 PR diff 和 config
    ├── 调用 AI Service 分析
    ├── 计算权重评分
    └── 输出评分结果 + 改进建议

config/
├── ai_harness_config.yaml   # 权重、阈值可在此调整
└── risk_profiles.yaml       # 风险等级定义

docs/
└── AI_HARNESS_GATES.md      # AI 门控说明和配置指南
```

**验收标准**：
- ✅ PR 提交时自动触发 AI 门控检查
- ✅ 高风险 PR 被阻挡，显示清晰的失败原因
- ✅ 低风险 PR 自动通过，可直接合并
- ✅ PR comment 显示 AI 分析报告（风险分数、建议等）
- ✅ 权重配置在 config 文件中可调整，无需改代码

**预期里程碑**：
- Day 13-15：workflow 改写完成
- Day 16-17：AI 门控脚本完成并联调
- Day 18：在实际 PR 上验证工作

**风险与对策**：
| 风险 | 对策 |
|------|------|
| 门控过严导致所有 PR 都被阻挡 | 逐步提高阈值，初期设置为 0.75（较宽松） |
| AI Service 不可达导致 workflow 卡住 | 设置 timeout，失败时默认通过（放宽要求） |
| 权重配置不合理导致评分不准确 | 后续迭代优化，基于实际 PR 数据调整 |

---

### 第 3 阶段：AI 驱动的智能升级（W3-W4，并行第 2 阶段）

**目标**：将线上告警从简单转发升级为 AI 分析后的智能决策和响应

**前置条件**：
- 第 0 阶段 AI Service 已部署
- Prometheus 告警规则已配置

**为什么做**：
- 线上问题需要快速响应，AI 可以自动分析严重程度
- 不仅转发告警，还要给出根因分析和建议方案
- Discord 通知要包含"问题是什么""严重程度是多少""建议怎么做"

**关键任务**：

| 任务 | 产物 | 预期效果 |
|------|------|--------|
| 改写升级 workflow | `.github/workflows/agent-escalation.yml` | Prometheus 告警触发 → AI 分析 → Discord 通知 |
| 实现 AI 分析引擎 | `tools/agents/escalation/escalation_analyzer.py` | AI 分析告警信号，判断严重程度 |
| 实现智能通知 | `tools/agents/escalation/discord_smart_notifier.py` | 发送包含 AI 分析的 Discord 消息 |
| 配置告警规则 | `config/prometheus-alerts.yml` | 定义多种告警场景和触发条件 |
| 实现升级建议生成 | `tools/agents/escalation/escalation_suggester.py` | 基于告警类型生成修复建议 |

**AI 驱动的升级逻辑**：
```
Prometheus 采集信号（每 30 秒一次）
  ↓
检测到异常
  ↓
发送到 AI Service
  ↓
[AI 分析]（调用 Ollama）
  ├── entropy 是否大幅上升？  → 代理可能失控
  ├── error_rate 上升多少？    → 用户影响范围
  ├── loop_detection 是否触发？ → 代理陷入循环
  ├── 过去 1 小时趋势如何？     → 是持续恶化还是偶发
  └── 综合评估严重程度
  ↓
AI 输出风险等级：
  • CRITICAL（0.95+）→ P1 立即升级，切换为 dry-run
  • HIGH（0.75+）    → P1 立即升级，通知值班人员
  • MEDIUM（0.50+）  → P2 30min 内响应
  • LOW（0.25+）     → P3 1 小时内处理
  ↓
生成 Discord 消息（包含分析 + 建议）
  例：
  "🚨 **CRITICAL ALERT**
   问题：Agent AuthService 陷入循环（57 次重复调用）
   影响：用户无法认证（error_rate 15%）
   趋势：过去 10 分钟持续恶化
   建议：
   1) 立即切换为 dry-run 模式
   2) 审查最近的 5 个决策
   3) 重启 Agent（待确认）
   ⏰ 自动升级到值班人员"
  ↓
等待人工确认或自动执行建议
```

**交付物清单**：
```
.github/workflows/
└── agent-escalation.yml（改写）
    ├── 接收 Prometheus webhook
    ├── 调用 AI Service 分析
    ├── 生成升级建议
    └── 发送 Discord 消息

tools/agents/escalation/
├── __init__.py
├── escalation_analyzer.py       # AI 分析引擎
├── discord_smart_notifier.py    # 智能通知
├── escalation_suggester.py      # 建议生成器
└── alert_aggregator.py          # 告警聚合（去重防疲劳）

config/
├── prometheus-alerts.yml        # 告警规则定义
├── escalation_profiles.yaml     # 升级策略配置
└── discord_channels.yaml        # Discord 频道映射

docs/
└── ESCALATION_GUIDE.md          # 升级流程说明
```

**验收标准**：
- ✅ 模拟 Prometheus 告警，AI Service 能正确分析
- ✅ Discord 消息在 60 秒内发送
- ✅ 消息包含风险等级、根因分析、改进建议
- ✅ 不同风险等级发送到不同频道（P1→critical，P2→warnings）
- ✅ 告警聚合和去重工作（相同告警 5 分钟内只发送一次）

**预期里程碑**：
- Day 13-16：升级分析器完成
- Day 17-18：Discord 集成完成
- Day 19-20：在测试环境验证

**风险与对策**：
| 风险 | 对策 |
|------|------|
| 告警过于频繁导致 Discord 疲劳 | 实现告警聚合，相同告警 5-10 分钟只发送一次 |
| AI 分析结果不准确 | 初期保守评分，宁可报高不报低，后续迭代优化 |
| Discord webhook 失败导致消息丢失 | 实现重试机制（exponential backoff），本地日志备份 |

---

### 第 4a 阶段：本地 K8s 部署基础设施准备（W4-W5）

**目标**：准备本地 K8s 集群部署所需的基础设施，为 AI 驱动的部署做准备

**前置条件**：第 0 阶段 AI Service 已部署在 K8s

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

### 第 4b 阶段：AI 驱动的 K8s 部署 + 熵管理生产化（W5-W7）

**目标**：建立完整的 AI 驱动的 K8s 部署流程，实现生产就绪和熵管理的真实执行

**前置条件**：
- 第 0 阶段 AI Service 已部署
- 第 4a 阶段基础设施已准备

**为什么做**：
- 自动化部署是 Harness 精神的终极目标
- 熵管理需要真实执行，而不是 dry-run
- 完整的可观测性堆栈（Prometheus + Grafana + Loki）支撑监控和告警

**关键任务**：

| 任务 | 产物 | 预期效果 |
|------|------|--------|
| 建立 Helm 部署清单 | `manifests/helm/nexvest-agent/` | `helm install nexvest ...` 可以部署到 K8s |
| 建立 Kustomize 覆盖 | `manifests/kustomize/overlays/prod/` | 支持 dev/staging/prod 环境定制 |
| 实现 AI 部署决策引擎 | `scripts/ai_deployment_analyzer.py` | AI 评估部署安全性，决定是否可以部署 |
| 改写部署 workflow | `.github/workflows/agent-deploy.yml` | merge main → AI 评估 → 决定是否部署 |
| 升级 entropy-agent | `tools/agents/entropy/entropy_agent.py` | 真实修改 ConfigMap/Secret，基于 AI 信号动态调整 |
| 部署可观测性堆栈 | `manifests/helm/nexvest-observability/` | Prometheus 采集指标，Grafana 展示，Loki 聚合日志 |
| 验证部署健康 | 部署检查脚本 | pod 健康、服务可达、指标采集正常 |

**AI 驱动的部署决策流程**：
```
PR 合并到 main
  ↓
触发 agent-deploy workflow
  ↓
[AI 部署评估]（调用 Ollama）
  检查过去 7 天的数据：
  ├── entropy_score 趋势：是上升还是下降？稳定吗？
  ├── error_rate：是否低于安全阈值（< 2%）？
  ├── loop_detection：过去 7 天是否有高风险触发？
  ├── test_coverage：新代码的覆盖率是否 > 70%？
  └── 综合计算部署安全分数（0-1）
  ↓
AI 决策：
  • 安全分数 >= 0.85  → ✅ 立即部署到生产
  • 安全分数 0.70-0.84 → ⏸️ 部署到 staging，监控 1 小时
  • 安全分数 < 0.70   → ❌ 阻止部署，通知团队审查
  ↓
若部署通过：
  • entropy_agent 运行
    → 根据当前系统信号调整 ConfigMap（并发数、超时等）
  • reasoning_optimizer 运行
    → 根据性能信号推荐 LLM 参数优化
  ↓
持续监控（1 小时）
  • 如果 error_rate 上升 > 2% → 立即回滚
  • 如果 entropy 异常上升 → 告警通知
  • 如果一切正常 → 部署成功，自动标记为 prod_deployed
```

**交付物清单**：
```
manifests/
├── helm/
│   ├── nexvest-agent/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── configmap.yaml        # 由 entropy_agent 修改
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
│
├── kustomize/
│   ├── base/nexvest/
│   │   ├── kustomization.yaml
│   │   └── manifests
│   └── overlays/
│       ├── dev/      # 开发环境配置
│       ├── staging/  # 暂存环境配置
│       └── prod/     # 生产环境配置

.github/workflows/
└── agent-deploy.yml  # 改写：AI 决策 + 自动部署

scripts/
└── ai_deployment_analyzer.py  # AI 部署决策引擎
    ├── 查询过去 7 天的 Prometheus 数据
    ├── 调用 AI Service 分析趋势
    ├── 计算部署安全分数
    └── 输出部署建议

tools/agents/entropy/
└── entropy_agent.py   # 改写：真实执行 ConfigMap 修改

docs/
├── DEPLOYMENT_GUIDE.md      # 部署指南
└── OBSERVABILITY_SETUP.md   # 可观测性堆栈说明
```

**验收标准**：
- ✅ `helm lint manifests/helm/nexvest-agent/` 通过
- ✅ `helm template nexvest manifests/helm/nexvest-agent/ | kubectl apply -f - --dry-run=client` 成功
- ✅ merge main → 自动触发 AI 部署评估
- ✅ 安全分数 >= 0.85 时自动部署，pod 运行成功
- ✅ 安全分数 < 0.85 时阻止部署，给出清晰的原因
- ✅ Prometheus `/metrics` 端点可以被抓取
- ✅ Grafana dashboard 显示实时指标（CPU、Memory、Error Rate）
- ✅ entropy-agent 运行后，ConfigMap 被修改（git diff 可见）
- ✅ 部署失败时自动回滚

**预期里程碑**：
- Day 26-30：Helm 清单完成，本地 `helm install` 成功
- Day 31-35：可观测性堆栈部署成功，数据采集验证
- Day 36-40：AI 部署决策引擎完成并在 staging 测试
- Day 41-45：生产部署流程验证，文档完善

**风险与对策**：
| 风险 | 对策 |
|------|------|
| 部署失败导致 pod 无法启动 | 实现详细的日志收集和健康检查，快速诊断 |
| 存储相关问题（PVC 挂载失败） | 预先配置 StorageClass，本地测试 PVC 申请 |
| 镜像版本控制混乱 | 使用 semantic versioning + git tag，workflow 自动构建版本号 |
| AI 部署决策不准确 | 初期保守评分（threshold 0.85），后期基于实际数据调优 |

---

## 📊 时间表与里程碑

```
W0   W1   W2   W3   W4   W5   W6   W7   W8   W9   W10  W11
├──┤
  第 0 阶段（AI Service 部署）
      ├────┤
         第 1 阶段（AI 本地检查）
            ├────┤
               第 2 阶段（AI 门控）
            ├────────┤ (并行)
               第 3 阶段（AI 升级）
                  ├────┤
                     第 4a 阶段（基础设施）
                        ├───────────┤
                           第 4b 阶段（AI 部署）
```

### 关键截止日期

| 阶段 | 开始 | 完成 | 可交付物 | 前置条件 |
|------|------|------|--------|---------|
| 第 0 | 2026/04/21 | 2026/04/25 | Ollama AI Service 部署 + HTTP API 就绪 | 无 |
| 第 1 | 2026/04/28 | 2026/05/11 | 本地 AI 检查 + pytest 70% 覆盖率 | 第 0 完成 |
| 第 2 | 2026/05/05 | 2026/05/18 | PR 自动 AI 门控 + 综合评分 | 第 0、1 完成 |
| 第 3 | 2026/05/05 | 2026/05/25 | Discord AI 驱动升级通知 | 第 0 完成 |
| 第 4a | 2026/05/12 | 2026/05/25 | K8s 基础设施就绪 | 第 0 完成 |
| 第 4b | 2026/05/26 | 2026/07/01 | AI 驱动的 K8s 部署 + 观测性堆栈 | 第 0、4a 完成 |

**关键依赖**：所有阶段都依赖第 0 阶段的 AI Service 部署。建议优先完成第 0 阶段以解锁后续工作。

---

## 🔑 关键技术决策

### 为什么选择 Ollama + llama2:7b？

| 维度 | Ollama | 外部 API（OpenAI） |
|------|--------|------------------|
| **初期成本** | ✅ $0 | ✅ $0 |
| **持续成本** | ✅ 低（算力费） | ❌ 高（$100-500/月） |
| **数据隐私** | ✅ 本地完全控制 | ⚠️ 数据上云 |
| **推理延迟** | ⚠️ 3-10 秒 | ✅ 1-2 秒 |
| **精度** | ⚠️ 7B 可能不如 GPT-4 | ✅ 最新 SOTA |
| **升级灵活性** | ✅ 可随时改模型 | ✅ 可随时改 API |
| **自主性** | ✅ 完全自主 | ❌ 依赖外部 |

**推荐**：初期用 Ollama + 7B，后期可灵活升级。配置文件支持无缝切换到 OpenAI。

---

## 🎯 总体目标重述

**从 0 到 1：建立 Harness 精神的 AI 驱动 CI/CD**

```
第 0 阶段后：有了 AI 大脑（Ollama 推理服务）
    ↓
第 1-2 阶段：AI 能检查代码（本地 + CI 层面）
    ↓
第 3 阶段：AI 能诊断问题（告警分析）
    ↓
第 4 阶段：AI 能决策部署（自动评估安全性）

最终：从被动检查 → 主动决策（真正的 Harness 精神）
```

### 成功指标

| 指标 | 当前 | 目标 | 阶段 |
|------|------|------|------|
| **代码覆盖率** | 0% | 70%+ | 第 1 完成 |
| **PR 自动检查失败率** | 0%（无检查） | 5-10% | 第 2 完成 |
| **升级通知自动化** | 0% | 100% P1/P2/P3 | 第 3 完成 |
| **生产部署自动化** | 0% | 100%（AI 决策） | 第 4 完成 |
| **MTTR（故障恢复时间）** | 30+ min | 5-10 min（AI 诊断 + 建议） | 第 3 完成 |
| **AI 决策准确率** | - | 85%+ | 全阶段 |
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
