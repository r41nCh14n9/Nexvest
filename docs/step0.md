# 第 0 阶段：AI Inference Service 部署指南

**版本**：1.0
**完成时间**：W0（第 1 周前）
**资源需求**：独立 K8s 集群 + 2-4 CPU + 8-16GB RAM + 15GB 存储

---

## 📋 目录

1. [前置要求](#前置要求)
2. [部署选项](#部署选项)
3. [选项 1：本地 Ollama（推荐快速验证）](#选项-1本地-ollama推荐快速验证)
4. [选项 2：K8s 部署 Ollama](#选项-2k8s-部署-ollama)
5. [验证部署](#验证部署)
6. [配置动态切换](#配置动态切换)
7. [故障排查](#故障排查)

---

## 前置要求

### 必须
- ✅ Docker 已安装（如果选择本地 Ollama）
- ✅ kubectl 已配置（如果选择 K8s 部署）
- ✅ curl 或 Postman（用于测试 API）

### 可选
- Python 3.10+ 和 requests 库（本地客户端测试）

---

## 部署选项

| 方案 | 部署位置 | 复杂度 | 推荐场景 | 启动时间 |
|------|---------|--------|---------|---------|
| **本地 Ollama** | 本地计算机 | ⭐ 简单 | 快速验证、开发 | 5-10 分钟 |
| **K8s 部署** | 独立 K8s namespace | ⭐⭐⭐ 复杂 | 生产就绪、长期运行 | 15-20 分钟 |

**建议流程**：
1. **Day 1-2**：先用本地 Ollama 快速验证可行性
2. **Day 3-4**：如果验证通过，升级到 K8s 部署

---

## 选项 1：本地 Ollama（推荐快速验证）

### 1.1 安装 Ollama

**macOS/Linux：**
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows：**
- 下载：https://ollama.ai/download/OllamaSetup.exe
- 双击安装

**Docker 方式（任何系统）：**
```bash
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama_data:/root/.ollama \
  ollama/ollama
```

### 1.2 下载模型

```bash
# 下载 llama2:7b（约 4GB）
ollama pull llama2:7b

# 验证模型已下载
ollama list
# 输出示例：
# NAME            ID              SIZE      MODIFIED
# llama2:7b       78e26419b446    3.8 GB    2 minutes ago
```

### 1.3 启动 Ollama 服务

```bash
# 如果用 ollama 命令，它会自动启动
ollama serve

# 如果用 Docker，服务已在后台运行
docker logs ollama
```

### 1.4 测试 API

```bash
# 测试 /api/tags 端点（列出可用模型）
curl http://localhost:11434/api/tags

# 输出示例：
# {"models":[{"name":"llama2:7b","model":"llama2:7b",...}]}
```

**注意 API 端口号**：
- Ollama 本地：`http://localhost:11434`
- Docker：`http://localhost:11434`（如果映射了 11434 端口）
- K8s：`http://nexvest-ai-inference:8000`（后续）

### 1.5 Python 测试脚本

在本地运行以下脚本验证 Ollama 可用：

```python
# test_ollama.py
import requests
import json

OLLAMA_API = "http://localhost:11434"

# 测试 1：列出模型
print("=" * 50)
print("Test 1: List available models")
print("=" * 50)
response = requests.get(f"{OLLAMA_API}/api/tags")
print(json.dumps(response.json(), indent=2))

# 测试 2：简单推理
print("\n" + "=" * 50)
print("Test 2: Simple inference")
print("=" * 50)
prompt = "What is the capital of France? Answer in one word."
data = {
    "model": "llama2:7b",
    "prompt": prompt,
    "stream": False
}
response = requests.post(f"{OLLAMA_API}/api/generate", json=data)
result = response.json()
print(f"Prompt: {prompt}")
print(f"Response: {result['response']}")
print(f"Token time: {result['eval_duration']} ns")

# 测试 3：代码分析示例
print("\n" + "=" * 50)
print("Test 3: Code analysis example")
print("=" * 50)
code_analysis_prompt = """
Analyze this code for potential issues:

```python
def process_agent_output(output, max_retries=3):
    for i in range(max_retries):
        try:
            result = output.process()
            return result
        except:
            if i == max_retries - 1:
                raise
```

Rate entropy score (0-1) and suggest improvements.
"""
data = {
    "model": "llama2:7b",
    "prompt": code_analysis_prompt,
    "stream": False
}
response = requests.post(f"{OLLAMA_API}/api/generate", json=data)
result = response.json()
print(result['response'])
```

运行测试：
```bash
python test_ollama.py
```

---

## 选项 2：K8s 部署 Ollama

### 2.1 准备 Helm Chart

创建目录结构：
```bash
mkdir -p manifests/helm/nexvest-ai-inference/templates
```

### 2.2 创建 Helm Chart 文件

#### `manifests/helm/nexvest-ai-inference/Chart.yaml`
```yaml
apiVersion: v2
name: nexvest-ai-inference
description: Ollama AI Inference Service for Nexvest
type: application
version: 0.1.0
appVersion: "0.1.0"

keywords:
  - ollama
  - ai
  - inference
  - llama2

home: https://ollama.ai
sources:
  - https://github.com/ollama/ollama

maintainers:
  - name: Nexvest Team
    email: team@nexvest.local
```

#### `manifests/helm/nexvest-ai-inference/values.yaml`
```yaml
# AI Inference Service 配置

replicaCount: 1

image:
  repository: ollama/ollama
  pullPolicy: IfNotPresent
  tag: "latest"  # 或指定版本如 "0.1.7"

service:
  type: ClusterIP
  port: 8000        # K8s Service 端口
  targetPort: 11434 # Ollama 内部端口
  name: nexvest-ai-inference

# 资源限制
resources:
  limits:
    cpu: "4"
    memory: "16Gi"
  requests:
    cpu: "2"
    memory: "8Gi"

# 存储配置
persistence:
  enabled: true
  size: 15Gi
  storageClassName: ""  # 使用默认 StorageClass，或指定特定类

# 模型配置
model:
  name: "llama2:7b"
  pullOnStart: true  # 启动时自动拉取模型

# 环境变量
env:
  - name: OLLAMA_NUM_THREADS
    value: "4"
  - name: OLLAMA_KEEP_ALIVE
    value: "5m"

# 健康检查
livenessProbe:
  httpGet:
    path: /api/tags
    port: 11434
  initialDelaySeconds: 60
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /api/tags
    port: 11434
  initialDelaySeconds: 30
  periodSeconds: 10
```

#### `manifests/helm/nexvest-ai-inference/templates/deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "nexvest-ai-inference.fullname" . }}
  labels:
    {{- include "nexvest-ai-inference.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "nexvest-ai-inference.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "nexvest-ai-inference.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: ollama
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: 11434
          protocol: TCP
        env:
        {{- toYaml .Values.env | nindent 10 }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
        livenessProbe:
          {{- toYaml .Values.livenessProbe | nindent 10 }}
        readinessProbe:
          {{- toYaml .Values.readinessProbe | nindent 10 }}
        volumeMounts:
        - name: ollama-data
          mountPath: /root/.ollama

      # Init container 用于拉取模型
      initContainers:
      - name: model-puller
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        command: ["ollama", "pull", "{{ .Values.model.name }}"]
        volumeMounts:
        - name: ollama-data
          mountPath: /root/.ollama
        resources:
          requests:
            cpu: "2"
            memory: "8Gi"

      volumes:
      - name: ollama-data
        persistentVolumeClaim:
          claimName: {{ include "nexvest-ai-inference.fullname" . }}-pvc
```

#### `manifests/helm/nexvest-ai-inference/templates/service.yaml`
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "nexvest-ai-inference.fullname" . }}
  labels:
    {{- include "nexvest-ai-inference.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.targetPort }}
      protocol: TCP
      name: http
  selector:
    {{- include "nexvest-ai-inference.selectorLabels" . | nindent 4 }}
```

#### `manifests/helm/nexvest-ai-inference/templates/pvc.yaml`
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {{ include "nexvest-ai-inference.fullname" . }}-pvc
  labels:
    {{- include "nexvest-ai-inference.labels" . | nindent 4 }}
spec:
  accessModes:
    - ReadWriteOnce
  {{- if .Values.persistence.storageClassName }}
  storageClassName: {{ .Values.persistence.storageClassName }}
  {{- end }}
  resources:
    requests:
      storage: {{ .Values.persistence.size }}
```

#### `manifests/helm/nexvest-ai-inference/templates/_helpers.tpl`
```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "nexvest-ai-inference.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "nexvest-ai-inference.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Namespace }}
{{- $name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Namespace $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "nexvest-ai-inference.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "nexvest-ai-inference.labels" -}}
helm.sh/chart: {{ include "nexvest-ai-inference.chart" . }}
{{ include "nexvest-ai-inference.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "nexvest-ai-inference.selectorLabels" -}}
app.kubernetes.io/name: {{ include "nexvest-ai-inference.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### 2.3 部署到 K8s

```bash
# 创建 nexvest-ai namespace
kubectl create namespace nexvest-ai

# 验证 Helm Chart 语法
helm lint manifests/helm/nexvest-ai-inference/

# 干运行（预览将部署的资源）
helm install nexvest-ai manifests/helm/nexvest-ai-inference/ \
  --namespace nexvest-ai \
  --dry-run \
  --debug

# 实际部署
helm install nexvest-ai manifests/helm/nexvest-ai-inference/ \
  --namespace nexvest-ai

# 监控部署进度
kubectl rollout status deployment/nexvest-ai-inference -n nexvest-ai
```

### 2.4 验证部署

```bash
# 查看 Pod 状态
kubectl get pods -n nexvest-ai

# 查看 Pod 日志
kubectl logs -n nexvest-ai deployment/nexvest-ai-inference -f

# 查看 Service
kubectl get svc -n nexvest-ai

# 端口转发（用于本地测试）
kubectl port-forward svc/nexvest-ai-inference 8000:8000 -n nexvest-ai
```

---

## 验证部署

### 方式 1：curl 测试（任何环境）

```bash
# 如果是本地 Ollama，用 localhost:11434
# 如果是 K8s 部署，可以 port-forward 到本地或直接在 Pod 中测试

# 测试 1：列出模型
curl http://localhost:8000/api/tags

# 测试 2：简单推理
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2:7b",
    "prompt": "What is 2+2?",
    "stream": false
  }'
```

### 方式 2：Python 脚本测试

将本文件中的 `test_ollama.py` 改为指向正确的 API 端点：

```python
# 如果是本地 Ollama
OLLAMA_API = "http://localhost:11434"

# 如果是 K8s 部署且 port-forward 了
OLLAMA_API = "http://localhost:8000"

# 如果是 K8s 内部访问
OLLAMA_API = "http://nexvest-ai-inference:8000"
```

---

## 配置动态切换

创建配置文件后续用于切换 AI 后端。

### 3.1 创建 `config/ai_backend.yaml`

```yaml
# AI 后端配置（支持动态切换）
# 初期：本地 Ollama
# 后期：可改为 OpenAI/Azure

backend:
  # 当前活跃的后端
  active_provider: "ollama"  # 或 "openai", "azure", "local"

  # Ollama 本地推理配置
  ollama:
    # 如果是本地 Ollama
    endpoint: "http://localhost:11434"

    # 如果是 K8s 部署
    # endpoint: "http://nexvest-ai-inference.nexvest-ai.svc.cluster.local:8000"

    model: "llama2:7b"
    timeout: 30            # 秒
    max_retries: 2
    temperature: 0.3       # 模型温度（0-1，越低越确定）

  # OpenAI 外部 API 配置（未来用）
  openai:
    api_key: "${OPENAI_API_KEY}"  # 从环境变量读取
    model: "gpt-4"
    timeout: 30
    temperature: 0.3

  # Azure OpenAI 配置（未来用）
  azure:
    api_key: "${AZURE_OPENAI_KEY}"
    endpoint: "${AZURE_OPENAI_ENDPOINT}"
    model: "gpt-4"
    timeout: 30

# 备份配置（当主提供商不可用时自动切换）
fallback_enabled: true
fallback_provider: "openai"  # 如果 Ollama 不可用，改用 OpenAI
```

### 3.2 在应用中加载配置

后续在 `tools/agents/ai_inference/config_manager.py` 中实现配置加载逻辑：

```python
import yaml
import os

def load_ai_backend_config(config_path="config/ai_backend.yaml"):
    """加载 AI 后端配置"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # 替换环境变量
    if config['backend']['openai']['api_key'].startswith('${'):
        key_name = config['backend']['openai']['api_key'].strip('${}')
        config['backend']['openai']['api_key'] = os.getenv(key_name)

    return config

def get_active_provider(config):
    """获取当前活跃的 AI 后端"""
    return config['backend']['active_provider']
```

---

## 故障排查

### 问题 1：Ollama 模型下载失败

**症状**：`ollama pull llama2:7b` 卡住或超时

**解决**：
```bash
# 查看下载进度（可能需要等待 10-30 分钟）
ollama list

# 如果需要中止，改用更小的模型
ollama pull neural-chat:7b  # 更轻量的模型

# 或改用量化版本
ollama pull llama2:7b-q4  # 4-bit 量化，更小更快
```

### 问题 2：K8s Pod 一直处于 Pending 状态

**症状**：`kubectl get pods` 显示 Pending

**排查**：
```bash
# 查看 Pod 事件
kubectl describe pod -n nexvest-ai <pod-name>

# 常见原因：
# 1. PVC 无法绑定 → 检查 StorageClass
# 2. 节点资源不足 → 降低资源要求或增加节点

# 降低资源要求
helm upgrade nexvest-ai manifests/helm/nexvest-ai-inference/ \
  --namespace nexvest-ai \
  --set resources.requests.cpu="1" \
  --set resources.requests.memory="4Gi" \
  --set resources.limits.cpu="2" \
  --set resources.limits.memory="8Gi"
```

### 问题 3：API 响应超时

**症状**：调用 `/api/generate` 总是超时

**原因和解决**：
```bash
# 原因 1：模型还在下载
# 解决：等待 init-container 完成模型拉取

# 原因 2：资源不足，推理很慢
# 解决：增加分配的 CPU，或改用更小的模型

# 原因 3：网络问题
# 解决：检查 Service 和 Pod 网络连接
kubectl exec -it -n nexvest-ai <pod-name> -- curl http://localhost:11434/api/tags
```

### 问题 4：K8s 和本地的网络连接

**如果 AI Service 在 K8s，但应用在本地**：

```bash
# 方式 1：Port Forward（开发用）
kubectl port-forward svc/nexvest-ai-inference 8000:8000 -n nexvest-ai

# 然后应用连接 localhost:8000

# 方式 2：Service NodePort（生产用）
# 改写 values.yaml 中的 service.type 为 NodePort
helm upgrade nexvest-ai manifests/helm/nexvest-ai-inference/ \
  --namespace nexvest-ai \
  --set service.type="NodePort"

# 查看 NodePort
kubectl get svc -n nexvest-ai

# 然后应用连接 <node-ip>:<node-port>
```

---

## ✅ 完成检查清单

部署完成后，请检查：

- [ ] 选择了部署方式（本地 Ollama 或 K8s）
- [ ] 模型已下载（`ollama list` 显示 llama2:7b）
- [ ] API 端点可访问（`curl /api/tags` 返回 200）
- [ ] Python 测试脚本能正常调用推理
- [ ] 配置文件 `config/ai_backend.yaml` 已创建
- [ ] 本地项目知道 AI Service 的地址（localhost:11434 或 K8s Service）

**完成后，可以开始第 1 阶段的本地 AI 检查实现。**

---

## 📚 参考资源

- Ollama 官网：https://ollama.ai
- Ollama 模型库：https://ollama.ai/library
- Ollama API 文档：https://github.com/ollama/ollama/blob/main/docs/api.md
- Helm 最佳实践：https://helm.sh/docs/chart_best_practices/
