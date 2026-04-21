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
- v1.0 (2026-04-21): 初始版本
