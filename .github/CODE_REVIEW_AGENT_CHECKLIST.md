# CODE_REVIEW_AGENT_CHECKLIST.md

Agent 產生 PR 的審查檢查表

- [ ] PR 標題與描述包含原始 prompt 與 agent 回覆重點。
- [ ] 變更範圍合理（無不必要的跨模組改動）。
- [ ] 是否包含/更新測試；測試是否足夠覆蓋修正/功能。
- [ ] 是否遵守風格 (Black / Flake8 / Prettier)；本地可執行 `pre-commit`。
- [ ] 是否可能造成安全/隱私風險（機密、敏感資料）？
- [ ] 是否需要架構審查（例如 DB schema、跨服務 API）？若需要，已標註並等待審查。
- [ ] 如果 agent 省略了某些設計決策（例如 error handling），已在 PR 中註明並由人類補充。
- [ ] 由至少一位具備上下游影響知識的團隊成員審核並核准。

合併前請務必確保 CI 全數通過。
