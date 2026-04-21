# COPILOT_PROMPTS.md

Copilot / Copilot Chat 共享 Prompt 範本（請在使用時依專案上下文替換方括號內容，並在 PR 描述註明使用的範本與實際 prompt）。

1) 問題拆解（請求產出可執行範例）

```
請以繁體中文說明，幫我完成 [功能描述] 的最小可運行程式碼範例（語言：Python/TypeScript），並提供如何執行測試的指令。
```

2) 修 bug（範本）
```
Context: 我們在 `module/path` 中遇到 X 錯誤，重現步驟：...
Goal: 請協助產生小幅 patch 修復該問題，並新增/更新對應的測試。
Constraints: 保持 API 不變；不修改資料庫 schema；提供 1-2 個測試用例。
Output: 顯示要修改的檔案與簡短變更說明，以及如何在本地執行測試。
```

3) 新功能（範本）
```
Context: 我們要新增 feature X，需求：...；涉及哪些檔案：...
Goal: 建議最小可行實作 (MVP)，分步列出變更，並提供測試、文件樣板與 migration（如需要）。
Constraints: 儘量減少跨模組改動；遵守現有 style。
Output: patch 清單、測試指令、README 變更樣板。
```

4) 文件更新（範本）
```
Context: 文件位於 docs/，需更新以反映最新 API。
Goal: 產生繁體中文文件段落，首次出現技術名詞提供中英對照；使用 Mermaid 圖表（如有）。
Constraints: 使用專案文件風格與 `.markdownlint.json` 規範。
Output: Markdown 片段與 mermaid markup。
```

5) 產生測試（範本）
```
Context: 函式 `module.func()` 目前未有單元測試。
Goal: 產生 pytest 單元測試，覆蓋正向與錯誤情境，各 1-2 個案例。
Constraints: 使用 pytest fixtures 與 project style。
Output: 測試檔案內容與執行指令。
```

6) 重構代碼（保持行為不變，新增測試）
```
請協助重構以下程式碼以提高可讀性與可測試性，保留現有行為。請新增對應的單元測試，並說明如何運行測試。
程式碼：
```[language]
[程式碼]
```
```

7) 寫 commit message 與 PR 描述
```
根據下面的變更列舉（檔案與摘要），請產出一段清晰的 commit message（主標題+說明）與 PR 描述，包含變更目的、測試步驟與回滾建議。
變更：
- file1.py: 修改 A
- file2.ts: 新增 B
```

8) 拒絕/安全提示（用於禁止產生敏感內容）
```
注意：不可在回應中包含任何形式的私密金鑰、密碼、個人身份資訊或受版權保護的大段原文。
```

使用說明：在使用任何範本時，請在 PR 描述貼上「使用的範本」與實際 prompt。
