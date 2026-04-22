______________________________________________________________________

# Step 3: 補齊 Infrastructure、Delegate 與外部系統連接，部署至 `dev` 環境

## **文檔類型**: 部署與運維指南 **版本**: 1.0 **編制日期**: 2026-04-20

## 目標

- 建立並註冊 Harness Delegate（讓 Pipeline 步驟可在你的環境執行）
- 定義 `dev` Environment 與對應 Infrastructure（例如 Kubernetes cluster）
- 串接常用外部系統：Git、Docker Registry、Kubernetes、Secrets 管理

## 前置需求

- 一個可供安裝 Delegate 的執行環境（例如小型 VM 或 Kubernetes cluster）
- 權限建立 Service Account、建立或安裝必要的 infra（e.g., k8s cluster）

## 安裝與註冊 Delegate（快速指南）

1. 在 Harness UI 中：Project → Setup → Delegates → New Delegate，選擇 Platform（Kubernetes / Self-hosted）
1. 依指示下載或使用 Helm chart 安裝（若使用 k8s）：

```bash
# 範例：使用 Helm 安裝（假設已設定 kubeconfig 指向 dev cluster）
helm repo add harness https://harness.github.io/helm-charts
helm repo update
helm install harness-delegate harness/harness-delegate --namespace harness-delegate --create-namespace \
  --set accountId=<YOUR_HARNESS_ACCOUNT_ID> --set managerUrl=<HARNESS_MANAGER_URL> --set token=<DELEGATE_TOKEN>
```

1. 等待 Delegate 在 Harness UI 顯示為 `Healthy`。

## 定義 Environment 與 Infrastructure

- 在 Harness 中建立 Environment（`dev`），並綁定對應的 Infrastructure Definition（例如 Kubernetes Cluster 或 VM）
- 為 Kubernetes 設定 Kubeconfig Connector，使 Harness 能夠部署 Kubernetes manifests

## 串接外部系統（清單）

- Git Connector（repo 存取）
- Docker Registry Connector（image 推送/拉取）
- Kubernetes Connector（部署目標）
- Secrets Manager / Vault（安全儲存憑證）

## 範例：Pipeline Stage 部署到 Kubernetes

```yaml
# pipelines/deploy-to-dev.yaml  (stage 範例)
pipeline:
  name: Deploy to Dev
  identifier: deploy_dev
  stages:
    - stage:
        name: Deploy Stage
        identifier: deploy_stage
        type: Deployment
        spec:
          infrastructure:
            environmentRef: dev
          execution:
            steps:
              - step:
                  type: KubernetesApply
                  name: Apply Manifests
                  identifier: k8s_apply
                  spec:
                    manifests:
                      - |-
                        apiVersion: apps/v1
                        kind: Deployment
                        metadata:
                          name: hello-app
                        spec:
                          replicas: 1
                          selector:
                            matchLabels:
                              app: hello-app
                          template:
                            metadata:
                              labels:
                                app: hello-app
                            spec:
                              containers:
                                - name: hello
                                  image: <YOUR_REGISTRY>/hello:latest
                                  ports:
                                    - containerPort: 8080
```

## 驗證

1. 確認 Delegate 健康且能 reach 外部資源（git、registry、k8s API）。
1. Run `Deploy to Dev` Pipeline，檢查 Kubernetes 中是否建立 `hello-app` Pod/Deployment。

## 排錯重點

- Delegate 無法建立連線：檢查網路、代理、DNS 與 Manager URL
- 權限錯誤：針對 K8s Connector 檢查 ServiceAccount 是否有 `create`/`apply` 權限
- Image Pull Error：確認 Registry 憑證與 image 標籤是否正確

## 延伸建議

- 使用 Infrastructure as Code（例如 Terraform）建立 cluster 與雲端資源，並把 state 與 pipeline 結合
- 建立 Policy（Policy as Code）來阻止非合規部署到 prod

## Changelog

| 版本 | 日期 | 撰寫人 | 變更內容 | | ---- | ---------- | ------------ | ------------------------------ | | 1.0
| 2026-04-20 | Nexvest 團隊 | 初版：Delegate 與 dev 部署指南 |
