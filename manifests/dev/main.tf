# 1. 定義 Provider
terraform {
  required_providers {
    harness = {
      source  = "harness/harness"
      version = "~> 0.30.0" # 請檢查 Terraform Registry 獲取最新版本
    }
  }
}

provider "harness" {
  endpoint   = "https://app.harness.io/gateway"
  account_id = "m6gpME2lTaehTN7w4-ut2A"
  platform_api_key = "pat.m6gpME2lTaehTN7w4-ut2A.69e7201e97a96f13311319e4.Pl7mdJeLpB8yFNB2gobd"
}

# 2. 定義 GitOps Cluster 資源
resource "harness_platform_gitops_cluster" "example" {
  identifier = "nexvest_gitops_cluster"
  account_id = "m6gpME2lTaehTN7w4-ut2A"
  project_id = "Nexvest"      # 對應你的 Project ID
  org_id     = "default"      # 預設為 default
  agent_id   = "harnessagent" # 這裡就是你要指定的 Agent Identifier

  request {
    cluster {
      server = "https://kubernetes.default.svc" # 目標集群的 API Server 地址
      name   = "target-k8s-cluster"

      # 認證設定
      config {
        tls_client_config {
          insecure = true # 如果是開發環境或內部叢集，可設為 true
        }
      }
    }
  }
}
