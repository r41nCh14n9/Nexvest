# Step 1: Hello World 架構建置

本階段建立最簡單的 Hello World 開發環境與 Harness Pipeline，驗證整體架構是否可用。

---

## 1.1 環境概述

此階段目標是讓你完成以下項目：

- Ollama 本地 AI 推理引擎啟動
- Harness Gitness 初次部署
- Harness 與 Ollama 連接
- 簡單 Hello World 專案上線
- 基本 Pipeline 執行成功

---

## 1.2 安裝與啟動 Ollama

1. 下載並安裝 Ollama
   - 參考 [Ollama 官網](https://ollama.com/)
2. 啟動模型
   ```bash
   ollama run qwen2.5-coder:7b
   ```
3. 驗證 API
   ```bash
   curl http://localhost:11434/v1/models
   ```

---

## 1.3 部署 Harness Gitness

使用 Docker 來啟動 Harness Open Source：

```bash
mkdir -p ~/harness-data

docker run -d \
  -p 3000:3000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/harness-data:/data \
  --name harness-opensource \
  harness/gitness
```

瀏覽器訪問 `http://localhost:3000`，完成管理員帳號註冊。

---

## 1.4 連接 Ollama

在 Harness UI 中進入 **Project Settings** > **Connectors**，新增 AI Provider：

- Type: OpenAI Compatible
- Base URL: `http://host.docker.internal:11434/v1`
- API Key: `dummy-key`
- Model Name: `qwen2.5-coder:7b`

> 注意：Harness 在 Docker 裡運行，無法直接用 `localhost` 連到宿主機，因此要使用 `host.docker.internal`。

---

## 1.5 Hello World 專案與 Pipeline

建立一個最簡單的 Hello World 專案：

1. 在 Harness 中建立 repository
2. 新增最簡單的 Java 程式
   ```java
   public class HelloWorld {
     public static void main(String[] args) {
       System.out.println("Hello, Nexvest!");
     }
   }
   ```
3. 建立 `.harness/build-pipeline.yaml`
   ```yaml
   version: 1
   kind: pipeline
   metadata:
     name: helloworld-pipeline
     identifier: helloworld_pipeline
   spec:
     stages:
       - name: build
         type: ci
         spec:
           steps:
             - name: compile
               type: run
               spec:
                 container: maven:3.9-eclipse-temurin-17
                 script: |
                   mvn clean package -DskipTests
   ```

---

## 1.6 驗證步驟

1. 在 Harness 中觸發 `helloworld-pipeline`
2. 確認 `build` Stage 成功
3. 若有錯誤，先檢查 Docker 容器網路與 Ollama 連線

---

## 1.7 結論

完成 step1 後，你應該已經具備：

- 本地 Ollama 模型服務
- Harness Gitness 執行環境
- Harness 與 Ollama 的基本連接
- 一個最簡單的 Hello World Pipeline
