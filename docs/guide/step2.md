---
# Step 2: 串接 AI Model（Ollama）並在 Pipeline 中測試 AI 任務

**文檔類型**: 開發指南
**版本**: 1.0
**編制日期**: 2026-04-20
---

## 目標

- 把 AI model（以 Ollama 為例）作為外部服務接入 Harness（透過 Connector / HTTP API）
- 在 Pipeline 中新增一個 AI 任務步驟，能呼叫模型並驗證回應

## 前置需求

- 已有可使用的 Ollama endpoint（本地執行或網路可達）
- 有權限在 Harness 建立 Connector（或使用 Secrets 存放 API key）
- 熟悉基本 HTTP 呼叫與 JSON

## 建議架構

- 使用 Harness 的 Generic HTTP Connector（或自訂 Connector）保存 Ollama endpoint 與憑證
- Pipeline 的 AI 步驟以 Shell/Script/HTTP 或自訂 Task 呼叫該 endpoint，並將回傳結果用於後續步驟

## 範例：建立 Connector（概念）

- 在 Harness UI 中：Project → Connectors → New Connector → 選擇 `HTTP` 或 `Generic API`
- 填寫：Endpoint（例如 `http://ollama.local:11434/v1/`）、Auth（若有）

## 範例：Pipeline 中的 AI 呼叫步驟（使用 curl）

```yaml
# pipelines/hello-with-ai-pipeline.yaml
pipeline:
  name: Hello + AI
  identifier: hello_ai_pipeline
  stages:
    - stage:
        name: AI Stage
        identifier: ai_stage
        type: Custom
        spec:
          execution:
            steps:
              - step:
                  type: ShellScript
                  name: Call Ollama
                  identifier: call_ollama
                  spec:
                    shell: Bash
                    onDelegate: true
                    command: |
                      # 使用已在 Connector/Secrets 設定的環境變數
                      set -e
                      prompt='Hello, please respond with a short greeting.'
                      resp=$(curl -s -X POST "http://$OLLAMA_HOST:11434/v1/generate" \
                        -H "Content-Type: application/json" \
                        -d '{"model":"gpt-4o-mini","prompt":"'$prompt'","max_tokens":50}')
                      echo "AI response: $resp"
```

說明：

- `$OLLAMA_HOST` 可由 Delegate 或步驟的環境變數注入（使用 Harness Secrets/Variables）
- 若你的 Ollama endpoint API 不同，請依實際 API 調整 `curl` payload

## 驗證步驟

1. 在 Harness 建立或匯入 `hello-with-ai-pipeline.yaml`。
2. 設定好 Connector/Secrets，確保 Delegate 可連到 Ollama。
3. Run Pipeline，於 Execution Logs 檢查 `Call Ollama` 步驟輸出，確認有合理回應。

## 常見問題與排解

- 連線失敗：檢查 Delegate 網路是否能 reach Ollama host（內網/防火牆問題）
- 認證錯誤：確保 API Key/Token 存在於 Harness Secrets，且步驟使用該 Secrets
- 回應格式不正確：查看 Ollama 的 API 規格，調整 `Content-Type` 或 body

## 延伸

- 將 AI 步驟的輸出解析後作為下一個步驟的輸入（例如自動產生測試、生成部署參數）
- 把 Ollama 包裝成一個可重用的 Template/Step，方便在其他 Pipeline 使用

## Changelog

| 版本 | 日期       | 撰寫人       | 變更內容                          |
| ---- | ---------- | ------------ | --------------------------------- |
| 1.0  | 2026-04-20 | Nexvest 團隊 | 初版：Ollama 串接與 Pipeline 範例 |
