# Level 3 — Production Harness: 設計指南與實作範例

本檔為 Level 3 的詳細設計與快速上手範例，包括中介層、可觀察性、熵管理、版本化/A-B、監控與升級政策。

目標（1-2 週 MVP）：
- 建立最小可運行的 middleware pipeline（loop detection + reasoning optimizer）。
- 提供 Prometheus metrics endpoint 與 Grafana dashboard 範例。
- 部署定時 entropy 管理 agent 與範例 workflow。
- 提供版本化範例與 A/B 流量切分 YAML。
- 定義升級/通知策略與 Escalation workflow。

架構概念：
- Agents 執行前/後經由 middleware 管線，middleware 可攔截、調度、打分或中止請求。
- Observability：agents 應暴露關鍵指標（latency, error_rate, loop_detected, decision_entropy）並導出到 Prometheus。
- Entropy management：定期審查/重置隨機 seed 與隨機性分佈，避免 agent 行為惡化。

目錄：
- `tools/agents/middleware/`：中介層範例程式碼（loop_detection.py, reasoning_optimizer.py）。
- `tools/agents/observability/`：Prometheus exporter 範例。
- `tools/agents/entropy/entropy_agent.py`：排程執行的 entropy 管理 agent。
- `manifests/agents/versioning.yaml`：版本化與 A/B 分流範例。
- `manifests/dashboards/agent_performance_grafana.json`：Grafana dashboard 範例。
- `.github/ESCALATION_POLICY.md`：升級政策說明。
- `.github/workflows/entropy-agent.yml`：排程 workflow 範例。

驗收準則（MVP）：
- Middleware 能在偵測到簡單的回圈（基於歷史 prompt fingerprint）時中止並記錄 metric。
- /metrics endpoint 可被 Prometheus 抓取（本 repo 包含簡單 exporter 範例）。
- entropy agent 可被排程觸發且寫入 audit log。
- PR 加入或修改 agent 時，CI 檢查會驗證 Level3 文件存在並通過基本測試。

下一步：檢視 `tools/agents/` 的範例並在 sandbox env 部署測試。若需要，我可以幫您把 exporter 部署到 k8s 或提供 Terraform 範例。
