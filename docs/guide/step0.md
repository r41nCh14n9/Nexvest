# Step 0: Harness Engineering 概念說明

此文件說明 Harness Engineering 的核心概念，讓後續 Step 1~4 的操作更有脈絡。

---

## 0.1 Harness 的定位

Harness 不是寫應用程式的工具，主要負責以下三類工作：

- **部署與交付流程**：建立 CI/CD Pipeline、管理 Stage、步驟與執行順序。
- **環境與基礎設施管理**：定義 Environments、Infrastructure、Connectors、Delegates。
- **安全與治理**：管理 RBAC、Service Account、Policy as Code、Approval Workflow。

應用功能開發仍由開發者或 Prompt Engineering 完成；Harness 則負責將它們可靠地交付到環境中。

---

## 0.2 Harness 四層架構

1. **Connectors (連接器)**
   - 連接外部資源，例如 Git、Docker Registry、Kubernetes、AI 服務（Ollama）。
2. **Delegates (代理)**
   - 執行 Pipeline 任務的節點。通常部署在可連線的基礎設施上。
3. **Environments + Infrastructure**
   - 定義部署目標環境（如開發、測試、生產）及其底層資源。
4. **Pipelines + Templates + Policies**
   - Pipeline 定義流程，Templates 讓步驟可重用，Policies 保證標準一致。

---

## 0.3 Harness 與 AI 的協作方式

在這個專案中：

- **Harness** 負責執行與交付
- **Ollama** 負責 AI 分析與建議
- **Prompt Engineering** 可協助生成程式碼、測試或 Pipeline 配置

這三者是互補的，並不是互相取代：

- 若要新增功能，仍然需要寫程式或使用 AI 生成程式碼。
- 若要部署、測試、治理，則可透過 Harness 來自動化管理。

---

## 0.4 主要概念速記

### Connector

用來安全連接外部系統，例如 Git、K8s、Docker Registry、Ollama API。

### Delegate

運行在你的環境中的執行代理，負責實際跑 Step。

### Environment

Harness 中的部署環境定義，例如 `dev`、`test`、`prod`。

### Service Account / RBAC

定義 Pipeline 的執行權限與資源存取範圍。

### Policy as Code

使用規則檔（例如 Rego）強制要求 Pipeline/部署符合公司標準。

### Template / Skill

可重用的步驟或 Stage 模板，避免重複定義流程。

---

## 0.5 建議實作順序

1. 先完成 `step0` 的概念理解與目標（Harness + AI 整合）
2. 在 `step1` 建置 Harness 專案骨架與最簡單的 Hello World Pipeline，確認 pipelines 可執行
3. 在 `step2` 串接 AI model（例如 Ollama）作為 Connector，並在 Pipeline 中加入 AI 任務測試
4. 在 `step3` 補齊 Infrastructure、Delegate 與外部系統連接，部署至 `dev` 環境
5. 在 `step4` 進行專案功能開發與單元測試，並將測試整合到 Pipeline
6. 使用 CI/CD 執行整合測試與完整流程驗證，回饋並優化 Pipeline 與 Policy
