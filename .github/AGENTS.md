# AGENTS.md

團隊代理 (Agent) 使用與協作約定 — 適用 3-10 人小型團隊

目的：統一 agent 在團隊中的行為、權限與可驗證流程，減少不同成員間的誤解與不一致性。

主要項目：

- **授權與範圍**：agent 僅限於產生建議、範例與補丁草案；任何修改需由人類審查並且由具有 commit 權限的開發者實際提交。
- **Prompt 可追溯**：所有 agent 變更在 PR 描述中必須包含原始 prompt、agent 回覆（必要時節錄）、以及變更摘要。
- **最小可測試產出**：agent 變更必須包含或更新對應測試，或說明為何不需新增測試（需經審查同意）。
- **CI 強制規範**：PR 必須通過 `.github/workflows/agent-ci.yml` 中定義的檢查，否則禁止合併。
- **安全與隱私**：agent 不得生成或上傳秘密 (secrets)、個資或第三方授權受限內容。

架構與約束（範例）

- 代碼風格：使用 Black / Flake8（Python）、Prettier（前端）。
- 依賴管理：變更依賴需新增變更說明與安全性評估。
- 模組邊界：核心服務（例如資料存取層）不得由 agent 自動改寫，需先經架構審查。

流程範例

1. 開 issue 並標記 `agent`，描述預期輸出。
2. 由 agent 生成補丁草案並建立 WIP PR（標題含 `[agent]`）。
3. 在 PR 描述內粘貼 prompt 與 agent 回覆摘要。
4. 團隊成員審查 PR，使用 `CODE_REVIEW_AGENT_CHECKLIST.md`。
5. CI 通過 → 經過一位以上人類核准後合併。

參考：請參考 `.github/CODE_REVIEW_AGENT_CHECKLIST.md` 以及 `COPILOT_PROMPTS.md` 範本。
