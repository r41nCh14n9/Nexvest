# Step 2: Infra / 部署與外部系統設定

本階段將專注於基礎設施、部署設定與外部系統整合，讓 Hello World 專案能在多環境中運行。

---

## 2.1 Infra 與外部系統概覽

此階段內容包括：

- Connectors 設定
- Delegate 與執行代理
- Environment / Infrastructure 定義
- Docker Registry、Kubernetes、SonarQube 等外部系統
- 部署流程與 Kubernetes manifests

---

## 2.2 Connectors 設定

在 Harness 中建立以下 Connectors：

### Git Connector
- Type: GIT
- URL: `https://gitness.local/nexvest/nexvest-core`
- Auth: SSH

### Docker Registry Connector
- Type: DOCKER_REGISTRY
- Provider: Docker Hub 或 Private Registry
- URL: `https://docker.io`
- Auth: 帳號密碼或 token

### Kubernetes Connector
- Type: KUBERNETES
- Master URL: `https://kubernetes.default.svc.cluster.local`
- Auth: Service Account Token

### Ollama Connector
- Type: HTTP
- URL: `http://host.docker.internal:11434`
- Auth: NONE

---

## 2.3 Delegate 設定

Delegate 是實際跑 Step 的執行節點，通常部署在你的本地或遠端叢集。

```yaml
# delegate-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: harness-delegate
  namespace: harness-delegate-ng
data:
  delegate.yaml: |
    accountId: YOUR_ACCOUNT_ID
    delegateId: nexvest-delegate-1
    delegateName: nexvest-local-delegate
    delegateToken: YOUR_DELEGATE_TOKEN
    managerHost: https://app.harness.io
    grpc:
      enabled: true
      port: 9881
```

---

## 2.4 Environments / Infrastructure 定義

定義開發、測試、生產環境，並指定對應的 Infrastructure：

```yaml
# .harness/environments.yaml
apiVersion: harness.io/v1
kind: Environment
metadata:
  name: nexvest-dev
  namespace: default
spec:
  environmentType: NON_PROD
  infrastructure:
    - name: nexvest-dev-k8s
      infrastructureType: KUBERNETES
      spec:
        connectorRef: nexvest-k8s-connector
        namespace: nexvest-dev

---
apiVersion: harness.io/v1
kind: Environment
metadata:
  name: nexvest-prod
  namespace: default
spec:
  environmentType: PROD
  infrastructure:
    - name: nexvest-prod-k8s
      infrastructureType: KUBERNETES
      spec:
        connectorRef: nexvest-prod-k8s-connector
        namespace: nexvest-prod
```

---

## 2.5 部署設定與 Kubernetes Manifest

### Dockerfile

```dockerfile
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### Kubernetes

```yaml
# k8s/dev/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nexvest-app
  namespace: nexvest-dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nexvest-app
  template:
    metadata:
      labels:
        app: nexvest-app
    spec:
      containers:
        - name: nexvest-app
          image: nexvest:latest
          ports:
            - containerPort: 8080
          livenessProbe:
            httpGet:
              path: /actuator/health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
```

```yaml
# k8s/dev/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: nexvest-service
  namespace: nexvest-dev
spec:
  selector:
    app: nexvest-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

---

## 2.6 外部系統整合

### SonarQube

```bash
docker run -d \
  --name sonarqube \
  -p 9000:9000 \
  sonarqube:latest
```

連到 `http://localhost:9000`，設定 `nexvest-core` 專案。

### Prometheus / ELK

若要後續監控，可先建立 Prometheus 或 ELK 堆棧，但這部分可放在更高階的 step2 或 step4。

---

## 2.7 結論

完成 step2 後，你應該已經具備：

- Harness 與外部 Infra 的連接器設定
- Delegate 與 Environment 的基礎結構
- Docker/K8s 的部署配置
- 主要外部系統（Git、Registry、Ollama、SonarQube）整合
