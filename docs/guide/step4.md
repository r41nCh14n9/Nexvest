---
# Step 4: 專案功能開發、單元測試整合與整合測試驗證

**文檔類型**: 開發與測試指南
**版本**: 1.0
**編制日期**: 2026-04-20
---

## 目標

- 編寫並整合專案功能程式碼
- 在 Harness Pipeline 中加入單元測試步驟（失敗則阻止後續部署）
- 建立整合測試階段，模擬完整流程驗證

## 前置需求

- 已完成 Step1-3：Pipeline、Delegate、Infra、AI Connector 已可執行
- 專案程式碼與測試框架（例如 Python 的 `pytest`、Node 的 `jest`）

## 範例：專案目錄與基本測試

```text
my-service/
  ├─ src/
  │   └─ app.py
  ├─ tests/
  │   └─ test_app.py
  ├─ requirements.txt
  └─ Dockerfile
```

`tests/test_app.py` 範例（Python + pytest）:

```python
def test_basic():
    assert 1 + 1 == 2

```

## 範例：Pipeline 中加入單元測試步驟

```yaml
# pipelines/test-and-deploy.yaml
pipeline:
  name: Test and Deploy
  identifier: test_deploy
  stages:
    - stage:
        name: Test Stage
        identifier: test_stage
        spec:
          execution:
            steps:
              - step:
                  type: ShellScript
                  name: Run Unit Tests
                  identifier: run_tests
                  spec:
                    shell: Bash
                    onDelegate: true
                    command: |
                      set -e
                      pip install -r requirements.txt
                      pytest -q
    - stage:
        name: Deploy Stage
        identifier: deploy_stage
        when:
          condition: "${pipeline.stages.test_stage.status} == 'Success'"
        spec:
          execution:
            steps:
              - step: { /* deploy step, e.g., KubernetesApply */ }
```

說明：

- 若 `Run Unit Tests` 失敗，Pipeline 停止且不會進入 `Deploy Stage`。

## 整合測試（高階流程）

1. 在測試環境（dev）部署服務（使用前一步成功產生的 artifact/image）。
2. 執行自動化整合測試（例如用 pytest + requests 或 Postman Collection Runner）。
3. 若整合測試通過，通知 Slack/Teams 並推進至下一階段／發佈。

## CI 範例（GitHub Actions 觸發 Harness 或 Webhook）

```yaml
# .github/workflows/ci.yaml
name: CI
on:
  push:
    branches: [main]
jobs:
  push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: |
          python -m pip install -r requirements.txt
          pytest -q
      - name: Trigger Harness (optional)
        run: |
          curl -X POST https://<harness-webhook-or-manager>/trigger -H "Authorization: Bearer ${{ secrets.HARNESS_TOKEN }}" -d '{"pipeline":"test_deploy"}'
```

## 驗證與回饋

- 每次 PR 或 main push 觸發單元測試；CI 成功後再觸發 Harness Pipeline 進行部署與整合測試
- 設定 Pipeline 的通知（成功/失敗）回報到 Slack/Teams

## 延伸建議

- 把測試報告（coverage、junit xml）上傳為 Artifact，並在 Harness Execution 中顯示
- 加入分段 Canary/Blue-Green 部署策略，並在 Pipeline 中把整合測試作為驗收門檻

## Changelog

| 版本 | 日期       | 撰寫人       | 變更內容                         |
| ---- | ---------- | ------------ | -------------------------------- |
| 1.0  | 2026-04-20 | Nexvest 團隊 | 初版：單元測試與整合測試整合範例 |
