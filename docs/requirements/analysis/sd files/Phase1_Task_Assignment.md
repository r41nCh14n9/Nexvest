# Phase 1 詳細任務分配與開發指南

**文檔類型**: 開發指南 / 任務分配
**版本**: 1.0
**編制日期**: 2026-04-10
**上次更新**: 2026-04-10
**撰寫人員**: 技術團隊
**審核人員**: 待審核
**適用對象**: 開發團隊 / 項目經理

---

## 文檔概述

**目的**: 提供 Phase 1 項目的詳細任務分解、開發規範與進度規劃，確保團隊協同開發與品質控制。

---

## 目錄

1. [任務分解詳表](#任務分解詳表)
2. [團隊角色與職責](#團隊角色與職責)
3. [技術決策矩陣](#技術決策矩陣)
4. [開發規範與最佳實踐](#開發規範與最佳實踐)
5. [測試策略](#測試策略)
6. [部署與上線計劃](#部署與上線計劃)

---

## 任务分解详表

### Sprint 1: 基础设施与财报模块 (第 1-2 周)

#### Task 1.1: 数据库初始化 (2 天, 1 人)

**负责人**: DevOps 工程师

**交付物**:

- PostgreSQL 14+ 数据库初始化脚本
- 核心 schema 定义 (users, financial_metrics, fundamental_scores, watchlists 等)
- MongoDB (可选) 初始化 (存储财报原始数据)
- Redis Cluster 配置脚本
- 数据备份与恢复计划

**完成标准**:

- ✓ 本地开发环境数据库可用
- ✓ 数据库连接池配置完毕
- ✓ 主要表的索引已创建
- ✓ 备份脚本已就绪

**检查清单**:

```sql
-- 验证所有表已创建
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

-- 验证索引已创建
SELECT indexname FROM pg_indexes
WHERE schemaname = 'public';

-- 性能基准测试
EXPLAIN ANALYZE SELECT * FROM financial_metrics
WHERE symbol = '2330' ORDER BY report_date DESC LIMIT 10;
```

---

#### Task 1.2: 后端项目框架搭建 (2 天, 1 人)

**负责人**: 后端团队负责人

**交付物**:

- Node.js + Nest.js 基础项目框架
- API Gateway 配置 (Nginx + Kong/AWS ALB)
- 认证与授权模块 (JWT + OAuth 2.0)
- 环境配置管理 (.env, 多环境)
- CI/CD 管道初始化 (GitHub Actions)
- Docker & Kubernetes 部署配置
- 日志系统集成 (Winston)

**項目結構**:

```plaintext
nexvest-api/
├── src/
│   ├── main.ts (入口)
│   ├── app.module.ts
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── auth.module.ts
│   │   │   ├── auth.service.ts
│   │   │   ├── auth.controller.ts
│   │   │   ├── jwt.strategy.ts
│   │   │   └── guards/
│   │   ├── fundamental/
│   │   │   ├── fundamental.module.ts
│   │   │   ├── fundamental.service.ts
│   │   │   ├── fundamental.controller.ts
│   │   │   ├── entities/
│   │   │   └── dto/
│   │   ├── alert/
│   │   ├── news/
│   │   └── dashboard/
│   ├── common/
│   │   ├── decorators/
│   │   ├── filters/
│   │   ├── interceptors/
│   │   ├── pipes/
│   │   └── middleware/
│   ├── config/
│   └── utils/
├── test/
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/
├── package.json
└── tsconfig.json
```

**完成标准**:

- ✓ Nest.js 应用启动成功
- ✓ 所有依赖已安装
- ✓ 环境变量配置完毕
- ✓ Docker 镜像能正常构建与运行
- ✓ GitHub Actions 流水线可执行
- ✓ 本地开发环境可用

---

#### Task 1.3: 认证授权系统 (2 天, 1 人)

**负责人**: 后端工程师 A

**交付物**:

- JWT 认证实现 (token 生成、验证、刷新)
- 用户注册/登录 API
- 权限管理模块 (Role-Based Access Control)
- 安全加密方案 (bcrypt for password hash)
- Session 管理 (Redis 存储)

**主要 API**:

```plaintext
POST /auth/register
  Body: {phone, email, password, real_name}
  Response: {user_id, token, expires_in}

POST /auth/login
  Body: {phone/email, password}
  Response: {token, refresh_token, expires_in}

POST /auth/refresh
  Body: {refresh_token}
  Response: {token, expires_in}

POST /auth/logout
  Response: {message: "Logout successful"}

GET /auth/profile
  Response: {user_id, phone, real_name, created_at}
```

**完成标准**:

- ✓ 用户能成功注册与登录
- ✓ Token 加密与签名正确
- ✓ 密码存储使用 bcrypt (salt rounds ≥ 10)
- ✓ Token 过期时间设置正确 (15 分钟+刷新令牌 7 天)
- ✓ 所有 API 端点已测试通过

---

#### Task 1.4: 财报数据源对接 (3 天, 1-2 人)

**负责人**: 后端工程师 B

**交付物**:

- 财报数据爬取脚本 (从 TWSE/GSIS/Bloomberg API)
- 数据验证与清洗逻辑
- 定时同步任务 (Cron job / Agenda)
- 数据导入到 PostgreSQL

**数据源**:

- TWSE (台湾证券交易所): 公开财务数据
- 企业自行申报数据
- 第三方 API 集成 (如有)

**实现清单**:

- [ ] 爬虫完成台湾上市公司完整财务数据导入
- [ ] 每日定时更新最新财报
- [ ] 数据验证规则已实现 (非负、合理范围等)
- [ ] 错误数据自动告警

**完成标准**:

- ✓ 数据库中至少有 1500+ 上市公司的 5 年财务数据
- ✓ 数据准确度 > 99% (随机抽样验证)
- ✓ 缺失数据已标记，不影响计算

---

#### Task 1.5: FundamentalService 核心实现 (3 天, 1 人)

**负责人**: 后端工程师 C (财报模块负责人)

**交付物**:

- FundamentalService 类 (财务指标计算)
- 健康度评分算法实现
- 趋势分析算法
- 同业对标逻辑
- Redis 缓存集成

**核心方法**:

```typescript
class FundamentalService {
  // 计算健康度评分
  async calculateHealthScore(symbol: string, date?: Date): Promise<HealthScore>;

  // 获取历史趋势
  async getHistoricalTrend(
    symbol: string,
    years: number = 5,
  ): Promise<HealthScoreTrend[]>;

  // 同业对标
  async comparePeers(
    symbol: string,
    industryCode: string,
  ): Promise<PeerComparison>;

  // 预警检测
  async detectWarnings(symbol: string): Promise<WarningIndicator[]>;
}
```

**完成标准**:

- ✓ 所有计算方法已实现并通过单元测试
- ✓ 缓存键生成正确，TTL 设置合理
- ✓ 指标计算准确度高 (> 99.5%)
- ✓ 性能满足 < 500ms 查询时间

---

#### Task 1.6: Fundamental API 端点实现 (2 天, 1 人)

**负责人**: 后端工程师 C

**交付物**:

- FundamentalController 实现
- API 端点: GET /fundamentals/{symbol}, /history, /compare
- 请求验证 (DTO/Guards)
- 响应格式统一

**API 定义**:

```typescript
@Controller('fundamentals')
@UseGuards(JwtAuthGuard)
export class FundamentalController {

  @Get(':symbol')
  async getFundamental(
    @Param('symbol') symbol: string,
    @Query('date') date?: string
  ): Promise<FundamentalResponse>

  @Get(':symbol/history')
  async getHistory(
    @Param('symbol') symbol: string,
    @Query('years') years: number = 5
  ): Promise<HistoryResponse>

  @Get(':symbol/compare')
  async comparePeers(
    @Param('symbol') symbol: string,
    @Query('peer_symbols') peerSymbols?: string
  ): Promise<ComparisonResponse>
}
```

**完成标准**:

- ✓ 所有端点已实现并文档化
- ✓ 请求参数验证完整
- ✓ 错误处理与日志完善
- ✓ Swagger 文档自动生成

---

#### Task 1.7: 财报前端组件开发 (3 天, 1 人)

**负责人**: 前端工程师 A

**交付物**:

- FundamentalCard 组件 (Vue 3)
- HealthScoreMeter 组件 (仪表)
- TrendChart 组件 (ECharts)
- Stock 详情页面
- 数据绑定与状态管理

**组件清单**:

- [ ] FundamentalCard: 完整的财务健康卡片
- [ ] HealthScoreMeter: 圆形仪表，显示 0-5 分制
- [ ] TrendChart: 5/10 年历史折线图，支持缩放
- [ ] ScoreBreakdown: 分项评分条形图
- [ ] PeerComparison: 同业对标信息卡

**完成标准**:

- ✓ 所有组件已实现并能正常渲染
- ✓ 数据绑定正确，响应式更新顺畅
- ✓ 图表性能良好 (1 秒内加载)
- ✓ 开启深色模式正常显示

---

#### Task 1.8: 财报模块端到端集成与测试 (2 天, 测试工程师)

**负责人**: QA 工程师

**交付物**:

- 后端单元测试 (Jest, > 80% 覆盖率)
- 前端单元测试 (Vitest, > 70% 覆盖率)
- 集成测试 (e2e, Cypress)
- 性能基准测试报告
- Bug 修复

**测试清单**:

- [ ] 单位测试: FundamentalService
- [ ] API 测试: 所有 Fundamental 端点
- [ ] UI 测试: 组件单元测试
- [ ] 集成测试: 整个财报流程 (查询 → 计算 → 显示)
- [ ] 性能测试: 单个数据查询 < 500ms
- [ ] 并发测试: 1000 并发用户查询

**完成标准**:

- ✓ 测试通过率 > 95%
- ✓ 覆盖率达到目标
- ✓ 性能指标满足 SLA
- ✓ 已文档化主要测试用例

---

### Sprint 2: 警示系统与新闻模块 (第 3 周)

#### Task 2.1: 实时行情数据流处理 (2 天, 1 人)

**负责人**: 后端工程师 B

**交付物**:

- WebSocket 适配器 (接收实时行情)
- Redis Pub/Sub 集成
- 行情数据验证与缓存
- 推送给警示引擎

**实现方案**:

```plaintext
行情源 (WebSocket)
  ↓
WebSocket Adapter
  ↓
数据验证 & 格式化
  ↓
Redis Cache
  ↓
发布事件到 Kafka / Redis Pub/Sub
  ↓
Alert Engine 订阅处理
```

**完成标准**:

- ✓ 行情数据实时更新 (< 100ms 延迟)
- ✓ 缓存命中率 > 90%
- ✓ 重连机制工作正常
- ✓ 数据质量验证通过

---

#### Task 2.2: 警示规则引擎核心实现 (4 天, 1 人)

**负责人**: 后端工程师 A (警示模块负责人)

**交付物**:

- AlertEngineService 类
- 规则树评估算法 (支持 AND/OR)
- 条件匹配判断逻辑
- 触发记录保存
- 单元测试

**核心类**:

```typescript
class AlertEngineService {
  // 创建警示规则
  async createAlert(alert: CreateAlertDto): Promise<Alert>;

  // 评估单个警示
  async evaluateAlert(
    alert: Alert,
    marketData: MarketData,
  ): Promise<AlertTrigger | null>;

  // 批量评估用户的所有警示
  async evaluateUserAlerts(
    userId: string,
    marketData: MarketData,
  ): Promise<AlertTrigger[]>;

  // 条件判断
  private evaluateCondition(
    condition: AlertCondition,
    context: EvaluationContext,
  ): boolean;
}
```

**测试覆盖**:

- [ ] 单个条件判断 (价格/成交量/技术面)
- [ ] AND/OR 复合条件
- [ ] 嵌套规则树
- [ ] 边界条件 (最大规则数)

**完成标准**:

- ✓ 算法正确性通过单元测试 (> 95% 通过率)
- ✓ 处理复杂规则 & 嵌套逻辑
- ✓ 性能满足: 单个用户 1000 条规则评估 < 1 秒
- ✓ 已文档化规则语法与 API

---

#### Task 2.3: 警示推送服务 (2 天, 1 人)

**负责人**: 后端工程师 B

**交付物**:

- PushNotificationService 类
- APNs (iOS) 集成
- FCM (Android) 集成
- Email 推送 (Nodemailer / SendGrid)
- 重试与幂等性机制
- 推送统计与监控

**多渠道推送流程**:

```plaintext
AlertTrigger 触发
  ├─ 应用内通知 (实时 Push)
  ├─ APNs 推送 (iOS)
  ├─ FCM 推送 (Android)
  └─ 异步 Email
```

**完成标准**:

- ✓ iOS/Android 推送成功率 > 95%
- ✓ 推送延迟 < 5 秒
- ✓ 重试机制: 失败自动重试 3 次 (指数退避)
- ✓ 所有推送有审计日志

---

#### Task 2.4: Alert API & 数据库 (2 天, 1 人)

**负责人**: 后端工程师 A

**交付物**:

- AlertController 实现 (CRUD)
- Alert 数据模型与关系
- 数据库表设计与索引优化
- 预设警示模板库

**主要 API**:

```typescript
POST   /alerts                   // 创建警示
GET    /alerts                   // 获取用户所有警示
GET    /alerts/:id               // 获取单个警示
PUT    /alerts/:id               // 更新警示
DELETE /alerts/:id               // 删除警示
GET    /alerts/templates         // 获取预设模板
GET    /alerts/:id/triggers      // 获取触发历史
```

**完成标准**:

- ✓ CRUD 操作正确
- ✓ 数据库查询性能 < 100ms
- ✓ 至少 5 个预设模板已创建
- ✓ 所有 API 已文档化

---

#### Task 2.5: 警示前端界面 (3 天, 1 人)

**负责人**: 前端工程师 B

**交付物**:

- AlertForm 组件 (创建/编辑警示)
- RuleNodeEditor 组件 (AND/OR 编辑器)
- AlertList 组件 (警示列表)
- AlertHistory 组件 (触发历史)
- 实时通知 UI (Toast/Badge)

**关键交互**:

- AND/OR 逻辑可视化编辑
- 拖动、删除、添加条件
- 预设模板快速应用
- 实时预览匹配结果

**完成标准**:

- ✓ 所有组件可正常交互
- ✓ 规则可正确序列化 & 反序列化
- ✓ 拖放编辑流畅无卡顿
- ✓ 错误提示清晰

---

#### Task 2.6: 新闻爬虫与数据抓取 (3 天, 1 人)

**负责人**: 后端工程师 C

**交付物**:

- news 爬虫服务 (Scrapy / Node 爬虫框架)
- 新闻源集成 (彭博、路透、官方公告等)
- 数据清洗与标准化
- 去重逻辑 (URL Hash)
- 定时同步任务

**爬虫架构**:

```plaintext
新闻源 (多个 URL)
  ↓
Scraper (数据提取)
  ↓
数据清洗 (HTML 解析、去重)
  ↓
验证 (字段检查)
  ↓
存储到 MongoDB / PostgreSQL
```

**数据质量检查**:

- [ ] 标题与内容不为空
- [ ] URL 有效性检查
- [ ] 发布时间合理 (不是未来时间)
- [ ] 去重: 同一 URL 不重复存储

**完成标准**:

- ✓ 每天自动抓取 500+ 篇新闻
- ✓ 去重准确率 > 99%
- ✓ 数据清洗成功率 > 95%
- ✓ 爬虫稳定运行无错误

---

#### Task 2.7: Elasticsearch 集成与搜索 (2 天, 1 人)

**负责人**: 后端工程师 B

**交付物**:

- Elasticsearch 索引设计
- 新闻数据导入与同步
- 搜索与过滤逻辑
- 相关性排序算法

**索引设计**:

```json
{
  "mappings": {
    "properties": {
      "title": { "type": "text", "analyzer": "standard" },
      "content": { "type": "text" },
      "symbol": { "type": "keyword" },
      "industry": { "type": "keyword" },
      "source": { "type": "keyword" },
      "sentiment": { "type": "keyword" },
      "published_at": { "type": "date" },
      "relevance_score": { "type": "double" }
    }
  }
}
```

**查询示例**:

```javascript
GET /news/search
{
  "query": {
    "bool": {
      "must": [
        {"match": {"title": "AI"}},
        {"match": {"symbol": "NVDA"}}
      ],
      "filter": [
        {"term": {"sentiment": "positive"}}
      ]
    }
  },
  "sort": [{"published_at": {"order": "desc"}}]
}
```

**完成标准**:

- ✓ 搜索响应时间 < 200ms
- ✓ 中文分词正确
- ✓ 相关性排序合理
- ✓ 支持多字段查询与过滤

---

#### Task 2.8: AI 摘要集成 (初版，2 天，1 人)

**负责人**: 后端工程师 A

**交付物**:

- LLM API 集成 (OpenAI / Qwen / Claude)
- 提示词模板
- 摘要缓存机制
- 成本监控

**实现**:

```typescript
class SummarizationService {
  async generateSummary(news: News): Promise<string> {
    // 检查缓存
    const cachedSummary = await this.cache.get(`summary:${news.id}`);
    if (cachedSummary) return cachedSummary;

    // 调用 LLM API
    const summary = await this.llmService.summarize(
      news.title + "\n" + news.content,
    );

    // 存储缓存
    await this.cache.set(`summary:${news.id}`, summary, 7 * 24 * 3600);

    return summary;
  }
}
```

**完成标准**:

- ✓ 摘要质量可接受 (人工验证 > 80 篇)
- ✓ API 调用成本监控就位
- ✓ 失败降级: 返回原始前 300 字
- ✓ 处理能力: 50 篇/小时

---

#### Task 2.9: 新闻前端界面 (2 天, 1 人)

**负责人**: 前端工程师 A

**交付物**:

- NewsFeed 组件 (个性化新闻流)
- NewsCard 组件 (单条新闻卡片)
- NewsFilter 组件 (过滤/搜索)
- News 详情页

**关键特性**:

- 无限滚动加载
- 情绪标签显示 (正面/中性/负面)
- 屏蔽功能 (屏蔽源、关键词)
- 已读状态标记

**完成标准**:

- ✓ 新闻流加载流畅
- ✓ 无限滚动性能良好 (不卡顿)
- ✓ 过滤功能工作正确
- ✓ 移动端显示适配

---

### Sprint 3: 仪表板与集成测试 (第 4-6 周)

#### Task 3.1: 仪表板系统后端 (2 天, 1 人)

**负责人**: 后端工程师 C

**交付物**:

- DashboardService 类
- Dashboard CRUD 操作
- 配置持久化与加载
- 预设模板库

**完成标准**:

- ✓ CRUD 操作正确
- ✓ 配置保存与加载正常
- ✓ 用户间配置隔离完善
- ✓ 性能满足 < 500ms 查询

---

#### Task 3.2: 前端 Grid 布局与 Widget 系统 (3 天, 前端工程师)

**负责人**: 前端工程师 A

**交付物**:

- DashboardGrid 组件 (基于 Vue Grid Layout)
- Widget 容器与加载器
- 拖放编辑功能
- Widget 库与预设

**使用库**: `vue-grid-layout`

**完成标准**:

- ✓ 拖放编辑流畅
- ✓ 响应式布局正确
- ✓ 配置可保存与恢复
- ✓ 性能良好 (8+ 个 widget 不卡)

---

#### Task 3.3: 多端适配与性能优化 (2 天, 前端工程师)

**负责人**: 前端工程师 B

**交付物**:

- 响应式设计 (Mobile / Tablet / Desktop)
- 深色模式实现
- 代码分割与预加载
- 图片优化与 CDN

**性能优化目标**:

- 首屏加载时间: < 1.5s (3G 网络)
- Core Web Vitals:
  - LCP: < 2.5s
  - FID: < 100ms
  - CLS: < 0.1

**完成标准**:

- ✓ Lighthouse 评分 > 85
- ✓ 深色模式无显示问题
- ✓ Bundle 大小 < 500KB (gzip)
- ✓ 移动端流畅度 FPS > 50

---

#### Task 3.4: 集成测试与自动化 (2 天, QA 工程师)

**负责人**: QA 工程师

**交付物**:

- E2E 测试用例 (Cypress, > 20 个场景)
- 性能基准测试报告
- 负载测试 (1 万并发)
- Bug 跟踪与修复

**主要测试场景**:

1. 用户登录 → 浏览财报 → 设置警示 → 查看新闻
2. 创建自定义仪表板 → 拖放组件 → 保存与恢复
3. 大规模数据查询性能 (1000+ 股票)
4. 异常处理 (网络错误、超时)
5. 移动端基本功能

**完成标准**:

- ✓ E2E 测试覆盖所有关键路径
- ✓ 测试通过率 > 95%
- ✓ 性能基准已建立 (用作后续对标)
- ✓ 已发现并修复高优先级 Bug

---

#### Task 3.5: 部署与基础设施准备 (2 天, DevOps)

**负责人**: DevOps 工程师

**交付物**:

- Docker 镜像构建脚本
- Kubernetes 部署配置 (Dev/Staging/Prod)
- 监控与告警系统 (Prometheus + Grafana)
- 日志收集系统 (ELK)
- 备份与恢复计划

**K8s 部署配置示例**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nexvest-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nexvest-api
  template:
    metadata:
      labels:
        app: nexvest-api
    spec:
      containers:
        - name: api
          image: nexvest/api:v1.0.0
          ports:
            - containerPort: 3000
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
```

**完成标准**:

- ✓ 本地、Staging、生产环境配置完整
- ✓ 自动化部署流水线可工作
- ✓ 监控告警已配置
- ✓ 日志能正常收集与查询

---

#### Task 3.6: 用户手册与 Beta 准备 (1 天, 文档工程师)

**负责人**: 项目经理 / 文档工程师

**交付物**:

- 用户快速入门指南
- 功能使用文档
- API 文档 (Swagger)
- 常见问题解答 (FAQ)
- Beta 测试招募计划

**完成标准**:

- ✓ 文档清晰准确
- ✓ Swagger 文档自动生成完整
- ✓ FAQ 涵盖常见场景 (10+)
- ✓ Beta 用户招募信息已准备

---

#### Task 3.7: 修复与迭代 (1 周, 全团队)

**负责人**: 项目经理

**交付物**:

- 关键 Bug 修复
- 性能微调
- 用户反馈融合
- 最终版本发布

**迭代流程**:

1. 收集 Beta 用户反馈 (5-7 天)
2. 优先级分类与评估
3. 快速修复高优先级 Bug (< 24h)
4. 功能微调与性能优化
5. 最终版本发布

**完成标准**:

- ✓ 关键 Bug 修复率 > 90%
- ✓ 用户满意度 > 4.0/5.0
- ✓ 系统稳定性 > 99.5%
- ✓ 性能指标达成

---

## 团队角色与职责

### 后端团队 (3 人)

#### 后端负责人 (财报模块)

- 职责: FundamentalService 核心实现、指标计算、缓存策略
- 时间: 42 天
- 关键任务: 健康度评分算法、同业对标、API 设计

#### 后端工程师 A (警示模块)

- 职责: 警示规则引擎、推送服务、AI 摘要集成
- 时间: 42 天
- 关键任务: 规则树评估、LLM 集成、推送可靠性

#### 后端工程师 B (基础设施)

- 职责: 数据库、认证、实时数据流、新闻爬虫
- 时间: 42 天
- 关键任务: WebSocket、Redis、数据管道、爬虫稳定性

### 前端团队 (2 人)

#### 前端工程师 A (PC Web)

- 职责: 财报组件、新闻组件、仪表板
- 时间: 42 天
- 关键任务: ECharts 集成、响应式设计、性能优化

#### 前端工程师 B (移动端 / UI 通用)

- 职责: 移动端适配、深色模式、通用组件
- 时间: 42 天
- 关键任务: 响应式设计、动画优化、跨浏览器兼容

### QA / 测试 (1 人)

- 职责: 单元测试、集成测试、性能测试、自动化框架
- 时间: 42 天
- 关键任务: E2E 测试、性能基准、压力测试

### DevOps (1 人)

- 职责: 基础设施、CI/CD、监控告警、部署
- 时间: 42 天
- 关键任务: K8s 配置、数据库运维、监控系统

### 产品设计 (1 人)

- 职责: UI/UX 设计、交互原型、设计系统
- 时间: 30 天 (兼顾其他项目)
- 关键任务: 财报卡片设计、警示编辑器 UX、深色模式设计

### 项目经理 (1 人)

- 职责: 需求管理、进度跟踪、沟通协调
- 时间: 42 天
- 关键任务: 每日站会、风险管理、利益相关者沟通

---

## 技术决策矩阵

### 后端框架选型

| 选项              | 优点                          | 缺点                 | 决策                        |
| ----------------- | ----------------------------- | -------------------- | --------------------------- |
| Node.js + Nest.js | 快速开发、社区活跃、TS 支持好 | 单线程、CPU 密集型差 | ✅ 选择                     |
| Python + FastAPI  | 科学计算库丰富、性能好        | 部署复杂、生态不稳定 | 考虑未来 Phase 扩展数据分析 |
| Go + Gin          | 性能顶级、部署简单            | 生态小、财务计算库少 | 考虑用于高性能服务          |

### 数据库选型

| 选项       | 用途                            | 决策                        |
| ---------- | ------------------------------- | --------------------------- |
| PostgreSQL | 关系型数据 (用户、警示、仪表板) | ✅ 主数据库                 |
| Clickhouse | 时序数据分析 (未来财报分析用)   | 预留，Phase 2 可考虑        |
| MongoDB    | 财报原始数据存储                | 可选，暂用 PostgreSQL JSONB |
| Redis      | 缓存 & 会话存储                 | ✅ 核心组件                 |

### 前端框架选型

| 选项     | 优点                 | 缺点                 | 决策                 |
| -------- | -------------------- | -------------------- | -------------------- |
| Vue 3    | 易学、文档好、社区大 | 市场占有率低于 React | ✅ 选择 Web          |
| React 18 | 生态最成熟、性能优   | 学习曲线陡           | ✅ 选择 React Native |
| Angular  | 企业级功能完整       | 学习复杂、过度设计   | ✗ 不选               |

### 图表库选型

| 选项      | 优点                   | 缺点                   | 决策                 |
| --------- | ---------------------- | ---------------------- | -------------------- |
| ECharts 5 | 金融图表支持佳、性能好 | 库体积大 (1.5MB)       | ✅ 选择财报/技术图表 |
| Chart.js  | 轻量级、易上手         | 功能少、金融支持弱     | 简单统计图表         |
| D3.js     | 功能强大、自定义高     | 学习曲线陡、开发周期长 | ✗ 不选               |

### 消息队列选型

| 选项        | 优点             | 缺点       | 决策                  |
| ----------- | ---------------- | ---------- | --------------------- |
| Kafka       | 高吞吐、可靠性强 | 部署复杂   | ✅ 选择关键业务       |
| RabbitMQ    | 功能完整、可靠   | 吞吐量稍低 | 备选方案              |
| Redis Queue | 简单轻量         | 可靠性差   | 用于异步任务 (非关键) |

---

## 开发规范与最佳实践

### Git 工作流

**分支规范**:

```plaintext
main (主分支，保护)
  ├─ develop (开发分支)
  │   ├─ feature/p1-fundamental (功能分支)
  │   ├─ feature/p1-alert
  │   ├─ fix/critical-bug
  │   └─ release/v1.0.0 (发布分支)
```

**Commit 规范** (Conventional Commits):

```plaintext
<type>(<scope>): <subject>

feat(fundamental): 添加财报健康度评分计算
fix(alert): 修复规则引擎 AND 逻辑错误
docs(api): 更新 API 文档
refactor(core): 重构服务依赖注入
test(unit): 添加 FundamentalService 单元测试
chore(deps): 升级 nestjs 版本
```

**Pull Request 规范**:

- 每个 PR 必须关联 Issue
- 需要 2 个 Code Review 批准
- CI 流水线通过后才能合并
- 合并后自动触发 Staging 部署

### 代码质量

**TypeScript 配置**:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

**ESLint 规则**:

```javascript
// .eslintrc.js
module.exports = {
  parser: "@typescript-eslint/parser",
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:prettier/recommended",
  ],
  rules: {
    "no-console": "warn",
    "@typescript-eslint/explicit-function-return-types": "warn",
    "@typescript-eslint/no-unused-vars": "error",
  },
};
```

**测试覆盖率目标**:

- 后端: > 80% (关键业务逻辑 100%)
- 前端: > 70% (主要组件 > 80%)
- API 集成: 100% 主要端点

### API 设计规范

**请求 / 响应格式**:

```typescript
// 请求
interface ApiRequest {
  method: "GET" | "POST" | "PUT" | "DELETE";
  headers: {
    Authorization: "Bearer {token}";
    "Content-Type": "application/json";
  };
  body?: object;
}

// 响应
interface ApiResponse<T> {
  code: 200 | 400 | 401 | 404 | 500;
  message: string;
  data?: T;
  errors?: Array<{ field: string; message: string }>;
  timestamp: string;
}
```

**错误代码定义**:

```plaintext
200 - 成功
400 - 请求参数错误
401 - 认证失败
403 - 权限不足
404 - 资源不存在
422 - 业务逻辑验证失败
429 - 请求过于频繁
500 - 服务器错误
503 - 服务暂时不可用
```

### 日志规范

**日志级别**:

```
DEBUG - 开发调试信息
INFO  - 关键业务事件 (登录、创建警示等)
WARN  - 警告级别 (缓存失败、降级处理)
ERROR - 错误事件 (需要人工干预)
FATAL - 致命错误 (应立即告警)
```

**日志示例**:

```typescript
this.logger.info("Alert triggered", {
  userId: user.id,
  alertId: alert.id,
  symbol: "2330",
  timestamp: new Date(),
  triggerValue: marketData.price,
});
```

---

## 测试策略

### 单元测试

**框架**: Jest (后端) / Vitest (前端)

**后端单元测试示例**:

```typescript
describe("FundamentalService", () => {
  let service: FundamentalService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [FundamentalService],
    }).compile();

    service = module.get<FundamentalService>(FundamentalService);
  });

  it("should calculate health score correctly", async () => {
    const metrics = {
      roe: 0.25,
      fcf: 1000000000,
      debt_ratio: 0.35,
      eps_growth: 0.15,
      dividend_yield: 0.04,
    };

    const score = await service.calculateHealthScore(metrics);

    expect(score.score).toBeGreaterThan(3.0);
    expect(score.level).toBe("green");
  });
});
```

### 集成测试

**框架**: Jest + Supertest (API 测试)

```typescript
describe("Fundamental API (e2e)", () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it("GET /fundamentals/:symbol (200)", () => {
    return request(app.getHttpServer())
      .get("/fundamentals/2330")
      .set("Authorization", `Bearer ${validToken}`)
      .expect(200)
      .expect((res) => {
        expect(res.body.data.symbol).toBe("2330");
        expect(res.body.data.health_score).toBeDefined();
      });
  });
});
```

### E2E 测试

**框架**: Cypress

```typescript
describe("Stock Detail Flow", () => {
  beforeEach(() => {
    cy.login("test@example.com", "password");
  });

  it("should load fundamental data", () => {
    cy.visit("/stocks/2330");

    // 等待财报卡片加载
    cy.get('[data-testid="health-score"]').should("exist");
    cy.get('[data-testid="health-score"]').contains(/\d\.\d/);

    // 验证图表存在
    cy.get('[data-testid="trend-chart"]').should("be.visible");
  });

  it("should create alert successfully", () => {
    cy.get('[data-testid="create-alert-btn"]').click();
    cy.get('input[name="symbol"]').type("2330");
    cy.get('select[name="condition"]').select("price_above");
    cy.get('input[name="value"]').type("500");
    cy.get('button[type="submit"]').click();

    cy.get(".success-message").should("contain", "警示创建成功");
  });
});
```

### 性能测试

**工具**: Apache JMeter / K6

```javascript
// k6 性能测试脚本
import http from "k6/http";
import { check } from "k6";

export let options = {
  stages: [
    { duration: "2m", target: 100 }, // 2 分钟增长到 100 用户
    { duration: "5m", target: 100 }, // 保持 5 分钟
    { duration: "2m", target: 0 }, // 2 分钟降低到 0
  ],
  thresholds: {
    http_req_duration: ["p(99)<200"], // 99% 请求在 200ms 内完成
    http_req_failed: ["rate<0.1"], // 失败率 < 10%
  },
};

export default function () {
  let res = http.get("https://api.nexvest.com/fundamentals/2330");
  check(res, {
    "status is 200": (r) => r.status === 200,
    "response time < 200ms": (r) => r.timings.duration < 200,
  });
}
```

---

## 部署与上线计划

### 环境配置

**三环境架构**:

| 环境           | 用途              | 配置          | 部署      |
| -------------- | ----------------- | ------------- | --------- |
| **Dev**        | 本地开发测试      | 本地或 Docker | 手动      |
| **Staging**    | Beta 测试、预发布 | 接近生产      | 自动 (CI) |
| **Production** | 生产环境          | 高可用        | 蓝绿部署  |

### 部署流程

```plaintext
开发完成
  ↓
Push 到 develop 分支
  ↓
GitHub Actions CI 流水线
  ├─ 代码检查 (ESLint)
  ├─ 单元测试
  ├─ 构建 Docker 镜像
  └─ 推送到 Docker Registry
  ↓
(Pass) → 自动部署到 Staging
  ↓
Staging 测试 (5-24h)
  ↓
创建 Release PR (develop → main)
  ↓
Code Review (2 个批准)
  ↓
合并到 main
  ↓
GitHub Actions
  ├─ 生成版本标签
  ├─ 构建生产镜像
  └─ 触发蓝绿部署
  ↓
蓝绿部署 (Kubernetes)
  ├─ 部署新版本 (Green 环境)
  ├─ 健康检查
  ├─ 流量切换 (Blue → Green)
  └─ 保留旧版本 (Blue) 用于快速回滚
  ↓
监控 (30 分钟)
  ├─ 错误率
  ├─ 性能指标
  ├─ 用户反馈
  ↓
成功 ✓ / 失败 ✗ (回滚到 Blue)
```

### 发布检查清单

发布前需要完成以下检查 (Go / No-Go 决策):

- [ ] 所有单元测试通过 (100%)
- [ ] 集成测试通过 (100%)
- [ ] E2E 测试通过 (关键场景)
- [ ] 性能基准测试通过 (满足 SLA)
- [ ] 安全审计完成 (无高风险漏洞)
- [ ] 文档已更新 (API / 用户手册)
- [ ] 监控告警已配置
- [ ] 回滚计划已准备
- [ ] 利益相关者批准
- [ ] Staging 环境最终验证

### 灾难恢复计划

**故障恢复流程**:

1. **故障检测** (自动告警 < 1 分钟)
   - 错误率 > 5%
   - P99 延迟 > 5 秒
   - 服务不可用

2. **快速通知** (< 2 分钟)
   - 触发告警 (Slack / Email)
   - 召集应急小队

3. **初步诊断** (< 5 分钟)
   - 检查日志
   - 查看监控面板
   - 确认是否需要回滚

4. **回滚决策** (< 10 分钟)
   - 如果确认新版本有 Bug → 立即回滚到旧版本
   - Kubernetes 蓝绿部署支持 1 键回滚

5. **事后分析** (< 24 小时)
   - 详细的故障复盘
   - 根本原因分析 (RCA)
   - 改进措施 & 预防方案

**RTO / RPO 目标**:

- RTO (恢复时间): < 5 分钟
- RPO (恢复点): < 1 分钟 (数据丢失 < 1 分钟的交易)

---

## 总结

**Phase 1 的核心交付物**:

1. ✅ 稳定可靠的 MVP 应用
2. ✅ 完整的后端 API & 前端 UI
3. ✅ 自动化测试框架与持续集成
4. ✅ 监控告警与灾难恢复
5. ✅ 清晰的文档与运维手册

**下一阶段 (Phase 2)** 的准备:

- 基础架构已稳定，支持快速功能迭代
- 开发流程已建立，可平稳扩展团队
- 数据管道已就绪，支持新数据源集成

---

---

## 📝 Changelog (變更紀錄)

### 版本歷史

| 版本 | 日期       | 撰寫人   | 審核人 | 變更內容 |
| ---- | ---------- | -------- | ------ | -------- |
| 1.0  | 2026-04-10 | 技術團隊 | 待審核 | 初始版本 |

### 詳細變更記錄

#### v1.0 (2026-04-10)

**撰寫人**: 技術團隊 | **審核人**: 待審核

**內容**:

- 新增文檔頭部 (Front Matter) 規範資訊
- 轉換簡體中文至繁體中文
- 優化所有程式碼塊的語言標記
- 新增繁體技術術語一致性檢查
- 新增完整的 Changelog 部分

### 下次更新預計

- 開發中期檢查 (2026-04-24)
- 計劃新增: 實際開發進度追蹤、問題解決記錄、經驗總結
