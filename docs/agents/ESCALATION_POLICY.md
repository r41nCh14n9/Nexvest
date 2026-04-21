# Agent Escalation Policy

本文件定義 agent 在遇到停滯（stuck）、重覆錯誤或安全風險時的升級流程與聯絡點。

1. 分級定義
   - P1 (Critical): Agent 無法回應、持續發生高頻錯誤或造成資料外洩風險。
   - P2 (High): Agent 重複失效、顯著性能下降或產生大量警示。
   - P3 (Medium): 偶發錯誤或功能退化。

2. 自動化步驟
   - 觸發條件：超過 N 次錯誤、loop_detected metric 被觸發、或 entropy 異常。
   - 初步動作：middleware 先行降級/中止，記錄事件並產生 alert（Prometheus alertmanager）。
   - 如果 alert 未在 15 分鐘內清除，交由 on-call 工程師進行人工處理。

3. 通知渠道
   - PagerDuty / OpsGenie（建議）或 Slack 指定頻道。
   - Escalation workflow: `.github/workflows/agent-escalation.yml`

4. 事後流程
   - 事件記錄、root-cause 分析、回滾與防範措施寫入 incident report。
