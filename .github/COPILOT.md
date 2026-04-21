# COPILOT 使用與專案約定

**目的**: 使用 GitHub Copilot / Copilot Chat 作為專案內 AI 助手的標準作業流程與範本，取代或補足過去使用 Claude/Cursor/Codex 的做法。

**版本**: 1.0
**建立日期**: 2026-04-21

主要約定：
- 使用語言：專案主要文件採用繁體中文，技術術語保留英文（首次出現提供中英對照）。
- 回覆格式：AI 產出程式碼時需提供最小可運行範例與「如何執行測試」指令。
- Prompt 範本：請參考 `COPILOT_PROMPTS.md`。
- 禁止事項：不得上傳或產生含有敏感金鑰、個資或受版權限制的大段內容。

如何使用 Copilot 與驗收標準：
- 生成或修改程式碼前，先開啟 issue 或 pull request 並標註目的。
- 每次 AI 變更必須包含對應的自動化測試或更新現有測試。
- 本地可用 `pre-commit` 執行格式化與靜態檢查（參見 `.pre-commit-config.yaml`）。

快速檢查指令：
```bash
# 安裝開發套件
pip install -r tools/requirements-dev.txt

# 初始化 pre-commit（只需一次）
pre-commit install

# 執行測試
pytest -q
```

Changelog:
-- v1.0 (2026-04-21): 初始版本

Level 1 — Basic Harness (Single Developer)

確認事項：
- **Formatting & Hooks**: 已包含 `.pre-commit-config.yaml`（Black / Flake8 / Prettier）作為本地格式化與靜態檢查機制。
- **Tests**: 專案含有 `tests/`（含 `tests/test_smoke.py`）作為最小可執行測試。
- **Agent doc**: 本檔 (`.github/COPILOT.md`) 提供單人代理使用約定（可作為 CLAUDE 替代文檔）。
- **Acceptance**: 每次 agent 變更應附上生成 prompt 與驗證步驟。

Level 2 — Team Harness (Small Team)

我們已新增下列團隊層級資源以促進 3-10 人協作：
- `.github/AGENTS.md`: 團隊範例與約定（見下方連結）。
- `COPILOT_PROMPTS.md`: 共享 prompt 範本，用於常見任務。
- `.github/workflows/agent-ci.yml`: CI workflow，會在 PR 時執行格式檢查、lint、文件檢查與測試以強制架構與品質規範。
- `.markdownlint.json`: 文件 linter 規則，確保 docs-as-code 一致性。
- `.github/CODE_REVIEW_AGENT_CHECKLIST.md`: Agent 產生 PR 的審查檢查表。

運作流程（團隊）：
- 開啟 issue 並指定 `agent:` 標籤以啟動 agent 輔助工作。
- 在 PR 描述中貼上 agent 生成的 prompt 與重要回溯（prompt → agent response → patch summary）。
- CI 會在 PR 中自動阻止不合規的變更（格式、lint、測試未通過）。

參考檔案：
- [.github/AGENTS.md](.github/AGENTS.md)
- [COPILOT_PROMPTS.md](COPILOT_PROMPTS.md)
- [.github/workflows/agent-ci.yml](.github/workflows/agent-ci.yml)
- [.markdownlint.json](.markdownlint.json)
- [.github/CODE_REVIEW_AGENT_CHECKLIST.md](.github/CODE_REVIEW_AGENT_CHECKLIST.md)
 - [.github/COPILOT_INSTRUCTIONS.md](.github/COPILOT_INSTRUCTIONS.md)  
 - [.github/copilot-instructions.md](.github/copilot-instructions.md) (已重命名為上方檔案，舊檔案將稍後移除)
