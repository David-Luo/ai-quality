# AI Native 测试平台产品需求文档（L0 顶层需求）

## 文档信息

| 项目 | 内容 |
|------|------|
| 产品名称 | AI Native 测试平台（工程中心化方案） |
| 版本 | V1.0 |
| 文档版本 | L0 v1.0 |
| 更新日期 | 2026-04-12 |
| 产品类型 | AI Native 工程中心化测试平台 |
| 参考方案 | 方案 B：工程中心化 |

---

## 目录

1. [产品概述](#1-产品概述)
2. [设计原则](#2-设计原则)
3. [功能模块划分](#3-功能模块划分)
4. [核心业务流程](#4-核心业务流程)
5. [用户角色定义](#5-用户角色定义)
6. [使用场景分析](#6-使用场景分析)
7. [系统架构概览](#7-系统架构概览)
8. [非功能性需求](#8-非功能性需求)
9. [产品路线图](#9-产品路线图)
10. [L1 需求索引](#10-l1-需求索引)
11. [术语表](#11-术语表)

---

## 1. 产品概述

### 1.1 产品定位

AI Native 测试平台（工程中心化方案）是一个以 **Git 工程为核心资产存储**、以 **Qoder CLI Test Agent 为核心 AI 生产力**的新一代测试平台。

平台的核心理念：**测试资产属于工程，AI 是测试工程师的协作伙伴，平台是协作和可视化的基础设施。**

与传统测试平台（MeterSphere 等）的根本差异：

| 维度 | 传统平台中心化 | 本平台（工程中心化） |
|------|--------------|-------------------|
| 资产存储 | 数据库（平台强依赖） | Git 仓库（Markdown 文件） |
| 主要工作入口 | 浏览器 Web 界面 | 终端 + IDE（CLI 优先） |
| AI 定位 | 辅助功能（按钮触发） | 核心生产力（Test Agent） |
| 协作方式 | 平台账号权限 | Git PR + Code Review |
| 离线能力 | 无（强依赖平台） | 支持（离线生成，异步同步） |
| CI/CD 集成 | Webhook / API 适配 | 原生 Git Actions |

### 1.2 产品愿景

让测试工程师像软件工程师一样工作：**用 AI 生成测试资产，用 Git 管理版本，用平台做协作和可视化，用 CI/CD 做持续质量保障。**

### 1.3 目标用户

- **主要用户**：测试工程师（优先）
- **次要用户**：开发工程师、测试经理、项目经理

### 1.4 核心价值

1. **AI 生产力最大化**：Qoder CLI Test Agent 完成测试用例生成→脚本生成→执行→分析的完整闭环
2. **减少工作习惯改变**：测试工程师在熟悉的终端/IDE 环境中工作，CLI 交互模式对齐现代 AI Coding Agent
3. **资产可靠性**：测试资产存储在 Git 仓库，版本可追溯，平台故障不影响测试执行
4. **AI 友好的闭环**：执行引擎以 Python 脚本为核心，AI 可读取执行过程、分析结果、自动修复
5. **Markdown 原生**：测试用例、Bug 报告均以 Markdown 格式存储，AI 可直接读写，人类可直接编辑

---

## 2. 设计原则

### 2.1 工程中心原则

- 所有测试资产（测试用例、测试脚本、测试数据、Bug 报告）以文件形式存储在 Git 仓库
- 平台数据库只存储索引、元数据、统计信息，不存储资产内容本身
- 任何时候工程师可以不依赖平台，直接通过 CLI 和文件系统工作

### 2.2 CLI 优先原则

- Qoder CLI 是平台的第一公民，所有核心功能均可通过 CLI 完成
- Web 平台是 CLI 产出物的展示和协作层，不是必须的依赖
- CLI 支持离线工作，通过 API Key 异步同步到平台

### 2.3 AI 友好原则

- 测试资产格式对 AI 可读写友好（Markdown + Python）
- 执行引擎提供结构化的观测接口，AI 可以实时读取执行状态
- 失败现场以文本 + 截图形式保存，AI 可以直接分析
- 知识库以工程内 Markdown 文件为来源，无需额外维护

### 2.4 人机协作原则

- AI 生成，人工审核：测试计划、测试用例生成后，工程师可以完整地增删改
- 关键节点确认：AI 执行到关键节点（计划生成完成、批量脚本生成完成）等待工程师审批
- 所有 AI 交付物均是可编辑的普通文件，无黑盒

### 2.5 测试资产分层原则

```
测试用例（Test Case）          ← Markdown 文件，描述业务场景
    ↓ 1:1 对应
测试脚本（Test Script）        ← Python 文件，可执行实现
    ↓ 执行时使用
测试数据（Test Data）          ← 内嵌在脚本中，是脚本的一部分
    ↓ 执行产出
执行记录（Execution Record）   ← 数据库索引 + Markdown 报告文件
    ↓ 失败时产出
Bug 报告（Bug Report）         ← Markdown 文件，含截图/日志
```

---

## 3. 功能模块划分

### 3.1 模块全景图

```
┌─────────────────────────────────────────────────────────────────┐
│                    Qoder CLI Test Agent                          │
│  （核心 AI 生产力层：生成、执行、分析、修复）                        │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌─────────────┐  │
│  │ 测试计划    │ │ 用例生成   │ │ 脚本生成   │ │  执行分析   │  │
│  │ Planner   │ │ Generator │ │ Scripter  │ │  Analyzer  │  │
│  └────────────┘ └────────────┘ └────────────┘ └─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↕ 文件系统 / API Key 同步
┌─────────────────────────────────────────────────────────────────┐
│                    Git 工程（测试资产仓库）                        │
│  /tests/cases/    /tests/scripts/    /tests/bugs/               │
│  /docs/knowledge/ /tests/reports/    /tests/data/               │
└─────────────────────────────────────────────────────────────────┘
                              ↕ 异步同步
┌─────────────────────────────────────────────────────────────────┐
│                    测试平台（Web 展示与协作层）                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ 用例管理  │ │执行平台  │ │Bug 管理  │ │  知识库管理       │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              项目管理 / 用户管理 / 统计报表                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↕ 调用
┌─────────────────────────────────────────────────────────────────┐
│                    执行引擎（Python 核心）                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  UI 自动化   │  │ API 自动化   │  │    调度 & 观测        │  │
│  │ (Playwright) │  │  (Pytest)    │  │  (WebSocket 实时)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 模块边界与职责

#### M1：Qoder CLI Test Agent

**职责**：AI 核心生产力，测试资产的主要生成入口

| 子模块 | 职责 | 输入 | 输出 |
|--------|------|------|------|
| Planner | 分析需求，生成测试计划 | 需求文档 / 自然语言 | Markdown 测试计划 |
| Case Generator | 将测试计划转化为测试用例 | 测试计划 Markdown | Markdown 测试用例文件组 |
| Script Generator | 将测试用例转化为 Python 脚本 | 测试用例 Markdown | Python 测试脚本 |
| Executor | 触发执行引擎，观测执行过程 | 脚本路径 / 测试套件 | 执行记录 |
| Analyzer | 分析执行结果，生成 Bug 报告 | 执行记录 + 现场文件 | Bug Markdown / 修复建议 |

**模块边界**：
- CLI 只操作本地文件系统和执行引擎
- 通过 API Key 与平台进行异步同步（可选）
- 不依赖平台即可完成全部本地工作流

#### M2：测试用例管理

**职责**：测试用例的全生命周期管理（平台侧展示和协作）

| 子模块 | 职责 |
|--------|------|
| 用例库 | 树形模块结构，索引 Git 仓库中的用例 Markdown 文件 |
| 用例评审 | 工程师对 AI 生成用例的审核、修改、批准流程 |
| 测试计划 | 从用例库中组织测试套件，关联执行记录 |
| 用例同步 | 监听 Git 仓库变更，自动更新平台索引 |

**模块边界**：
- 平台只存储索引和元数据，内容以 Git 仓库文件为准
- 不提供独立的用例编辑器，编辑通过 CLI 或直接编辑 Markdown 文件完成

#### M3：UI 自动化测试

**职责**：Web UI 和移动端 UI 的自动化测试能力

| 子模块 | 职责 |
|--------|------|
| 脚本规范 | 定义 Playwright Python 脚本的生成规范和质量标准 |
| AI 脚本生成 | CLI 将测试用例 Markdown 转化为 Playwright Python 脚本 |
| 浏览器环境配置 | 管理浏览器类型（Chromium/Firefox/WebKit）、基础 URL 等 |
| 现场记录 | 失败自动截图、控制台日志收集，与 Bug 管理联动 |
| 脚本健康检查 | 识别腐化脚本（V1.5）；自动修复选择器失效（Healer，V1.5） |

**模块边界**：
- UI 脚本以 Playwright Python 为唯一框架
- 截图自动保存到 Git 工程的 `tests/reports/screenshots/` 目录

#### M4：API 自动化测试

**职责**：HTTP API 的自动化测试能力

| 子模块 | 职责 |
|--------|------|
| 脚本规范 | 定义 Pytest + httpx 脚本的生成规范和质量标准 |
| AI 脚本生成 | CLI 将测试用例 Markdown 转化为 Pytest + httpx 脚本 |
| 环境与认证配置 | 管理 Base URL、API Key/Bearer Token 等环境配置 |
| 请求/响应记录 | 记录每次请求的详情和响应，支持 Bug 现场重现 |
| 契约测试（V1.5） | 基于 OpenAPI Schema 验证响应结构；链路测试（多步 API） |

**模块边界**：
- API 脚本以 Pytest + httpx 为主要框架
- 请求/响应日志以文本形式保存到执行记录

#### M5：测试执行引擎

**职责**：统一的 Python 脚本执行、调度、观测基础设施

| 子模块 | 职责 |
|--------|------|
| 任务调度 | 接收执行请求，管理执行队列 |
| 脚本执行 | 在隔离环境中执行 Python 测试脚本 |
| 实时观测 | 通过 WebSocket 推送实时执行状态 |
| 现场记录 | 自动收集截图、日志、请求记录等现场证据 |
| 结果存储 | 将执行记录写入文件系统和数据库索引 |

**模块边界**：
- 只执行 Python 脚本，不感知业务逻辑
- AI（Qoder CLI Analyzer）读取执行结果进行分析，引擎不做 AI 分析

#### M6：Bug 管理

**职责**：缺陷的全生命周期管理，以 Markdown 为核心

| 子模块 | 职责 |
|--------|------|
| Bug 创建 | AI 自动创建（执行失败时）或手动创建 |
| Bug 内容 | Markdown 格式，含步骤、截图、日志、AI 分析 |
| Bug 状态流转 | open → in_progress → resolved → verified → closed；支持 wont_fix / duplicate / reopened |
| 集成管道 | 向外部系统（Jira / 禅道）同步 Bug |

**模块边界**：
- Bug 内容以 Git 仓库中的 Markdown 文件为主
- 平台存储状态、元数据、分配信息（不存储内容）
- 截图直接嵌入 Markdown（相对路径引用工程内图片文件）

#### M7：知识库管理

**职责**：为 AI 生成提供业务上下文的知识检索服务

| 子模块 | 职责 |
|--------|------|
| 文档索引 | 自动扫描工程内 `.md` 文件，建立向量索引 |
| 语义检索 | 根据查询语义检索相关文档片段 |
| 上下文注入 | 将检索结果注入 CLI 的 AI 生成上下文 |
| 索引刷新 | 监听 Git 提交，自动更新索引 |

**模块边界**：
- 知识库来源只有工程内 `.md` 文件，不支持外部文档上传（区别于 WHartTest）
- 向量数据库作为索引缓存，源文件始终是 Git 仓库中的 Markdown

#### M8：平台门户（展示与协作层）

**职责**：团队协作、数据可视化、项目管理

| 子模块 | 职责 |
|--------|------|
| 工作台 | 个人待办、近期执行结果、质量趋势看板 |
| 项目管理 | 项目创建、Git 仓库绑定、成员管理 |
| 用户管理 | 账号管理、API Key 管理、角色权限 |
| 统计报表 | 测试覆盖率、缺陷趋势、执行历史统计 |

---

## 4. 核心业务流程

### 4.1 主流程：需求驱动的测试生命周期

```
[1. 准备阶段]
产品需求文档（.md / PDF / OpenAPI）
    │
    ▼
知识库索引（自动扫描工程内 .md）
    │
    ▼
[2. AI 生成阶段]（Qoder CLI）
qoder test plan --from requirements/login.md
    │
    ├── 读取知识库上下文
    ├── AI 生成测试计划（Markdown）
    └── 输出 tests/plans/login_test_plan.md
         │
         ▼  [工程师审核，可编辑]
qoder test generate --from tests/plans/login_test_plan.md
    │
    ├── 逐条生成测试用例（Markdown）
    └── 输出 tests/cases/login/TC_001_xxx.md ... 
         │
         ▼  [工程师审核，可增删改]
qoder test script --cases tests/cases/login/
    │
    ├── 为每个用例生成对应 Python 脚本
    └── 输出 tests/scripts/login/TC_001_xxx.py ...
         │
         ▼  [工程师可检查脚本]

[3. 执行阶段]
qoder test run --suite tests/scripts/login/
    │
    ├── 执行引擎调度执行
    ├── 实时观测（截图/日志/请求记录）
    └── 输出 tests/reports/run_20260412_001/
         │
         ▼

[4. 分析阶段]（Qoder CLI）
qoder test analyze --report tests/reports/run_20260412_001/
    │
    ├── AI 读取执行结果
    ├── 分析失败原因
    ├── 自动创建 Bug Markdown（有失败时）
    │   └── 输出 tests/bugs/BUG_001_xxx.md
    └── 输出分析摘要

[5. 同步阶段]（可选）
qoder sync --push
    │
    └── 将本地资产同步到平台（API Key 认证）

[6. 缺陷跟踪阶段]（平台或 CLI）
    ├── 平台：查看 Bug 列表，分配给开发
    ├── 开发修复后更新 Bug 状态
    └── 触发回归：qoder test run --bugs tests/bugs/BUG_001_xxx.md
```

### 4.2 子流程：回归测试流程

```
代码变更（Git Push）
    │
    ▼
CI/CD 触发（GitHub Actions / Jenkins）
    │
    ▼
qoder test run --suite tests/scripts/ --env staging
    │
    ▼
执行引擎并行执行
    │
    ▼
qoder test analyze --report <latest>
    │
    ├── 无失败 → 生成通过报告，通知团队
    └── 有失败 → 创建/更新 Bug，通知相关人员
```

### 4.3 子流程：单 Bug 验证流程

```
Bug 修复提交
    │
    ▼
qoder test run --bug tests/bugs/BUG_001_xxx.md
    │  （自动关联到对应测试脚本）
    ▼
执行结果
    │
    ├── 通过 → 更新 Bug 状态为"已验证"
    └── 仍失败 → Bug 状态重置为"重新打开"，附新的执行记录
```

---

## 5. 用户角色定义

### 5.1 测试工程师（主要用户）

**特征**：具备 Python 编程能力，熟悉测试方法论，是平台的核心使用者

**主要工作场景**：
- 使用 Qoder CLI 生成和维护测试资产
- 审核 AI 生成的测试计划和用例
- 执行测试，分析结果，管理 Bug
- 维护知识库（工程内 `.md` 文档）

**操作权限**：
- 完整的 CLI 读写权限（在已授权项目范围内）
- 平台：用例管理、执行管理、Bug 管理的读写权限
- 不能修改项目配置、不能管理其他用户

**典型 CLI 工作流**：
```bash
# 生成测试
qoder test plan --from requirements/feature_x.md
qoder test generate --from tests/plans/feature_x_plan.md
qoder test script --cases tests/cases/feature_x/

# 执行测试
qoder test run --suite tests/scripts/feature_x/ --env staging

# 分析结果
qoder test analyze --report tests/reports/latest/

# 同步到平台
qoder sync --push
```

### 5.2 开发工程师（次要用户）

**特征**：主要关注接口正确性和测试覆盖，偶尔参与测试工作

**主要工作场景**：
- 查看 API 测试的执行结果，确认接口符合预期
- 查看和处理指派给自己的 Bug
- 在 CI/CD 中触发 API 测试

**操作权限**：
- 平台：只读查看用例和执行结果
- Bug：可更新指派给自己的 Bug 状态
- CLI：有限权限（只能执行，不能生成）

### 5.3 测试经理（次要用户）

**特征**：关注测试进度、质量指标和团队效率，不直接操作 CLI

**主要工作场景**：
- 查看测试进度和覆盖率报告
- 管理测试计划和里程碑
- 分配 Bug 给开发人员
- 审视 AI 生成质量

**操作权限**：
- 平台：所有模块的读取权限 + 测试计划管理权限
- 不使用 CLI

### 5.4 项目经理（次要用户）

**特征**：关注产品质量整体状态，用于决策发布

**主要工作场景**：
- 查看质量看板和缺陷趋势
- 查看测试报告

**操作权限**：
- 平台：只读权限（统计报表、Bug 状态）

### 5.5 系统管理员

**特征**：负责平台部署和维护

**主要工作场景**：
- 管理用户和项目
- 配置 Git 仓库绑定
- 管理执行引擎资源
- 配置 AI 模型（LLM Provider）

**操作权限**：
- 全平台管理权限

---

## 6. 使用场景分析

### 6.1 场景一：新功能测试（需求驱动）

**背景**：产品发布新功能，需要从零建立测试套件

**触发条件**：需求文档（.md / PRD）已存在于 Git 工程

**工作流程**：

```
测试工程师
    │
    ├── 1. 确认需求文档已在工程内（或编写简要需求 .md）
    ├── 2. qoder test plan --from requirements/feature.md
    │      AI 分析需求，生成测试计划（含测试范围、用例分类）
    ├── 3. 审核测试计划，调整优先级和范围
    ├── 4. qoder test generate --from tests/plans/feature_plan.md
    │      AI 逐条生成测试用例 Markdown 文件
    ├── 5. 快速浏览用例，删除不合适的，补充遗漏的
    ├── 6. qoder test script --cases tests/cases/feature/
    │      AI 为每个用例生成对应 Python 脚本
    ├── 7. 配置测试环境变量（.env.test）
    ├── 8. qoder test run --suite tests/scripts/feature/ --env staging
    ├── 9. qoder test analyze --report tests/reports/latest/
    └── 10. git commit -m "feat: add test suite for feature X"
```

**预期结果**：
- 测试用例从需求到可执行，耗时从 2 天降至 2 小时
- 所有资产纳入 Git 版本管理

### 6.2 场景二：回归测试（CI/CD 驱动）

**背景**：每次代码合并触发自动回归

**触发条件**：Git Push / PR Merge

**工作流程**：

```
CI/CD Pipeline (GitHub Actions)
    │
    ├── 1. Checkout 测试工程仓库
    ├── 2. qoder test run --suite tests/scripts/ --env staging --parallel
    │      执行引擎并行执行所有脚本
    ├── 3. qoder test analyze --report tests/reports/latest/ --auto-bug
    │      自动创建 Bug Markdown（有失败时）
    ├── 4. qoder sync --push（同步到平台）
    └── 5. 平台触发通知：Slack/邮件 → 相关人员
```

**预期结果**：
- 回归测试全自动，无需人工干预
- 失败结果自动创建 Bug，附执行现场

### 6.3 场景三：API 接口测试（接口变更驱动）

**背景**：后端更新了 API，需要验证接口行为

**触发条件**：OpenAPI Spec 文件（swagger.yaml）更新

**工作流程**：

```
测试工程师
    │
    ├── 1. qoder test plan --from api/swagger.yaml --type api
    │      AI 分析 OpenAPI Spec，生成 API 测试计划
    ├── 2. qoder test generate --from tests/plans/api_plan.md
    │      为每个接口生成测试用例（正常/边界/异常场景）
    ├── 3. qoder test script --cases tests/cases/api/ --framework pytest
    │      生成 Pytest + httpx 脚本
    ├── 4. qoder test run --suite tests/scripts/api/ --env staging
    └── 5. qoder test analyze --report tests/reports/latest/
```

**预期结果**：
- 接口变更后，测试用例快速更新覆盖
- API 测试脚本可直接集成到 CI/CD

### 6.4 场景四：Bug 驱动的修复验证

**背景**：开发修复了 Bug，需要验证修复效果

**触发条件**：Bug 状态更新为"待验证"

**工作流程**：

```
测试工程师
    │
    ├── 1. 查看 Bug Markdown 文件（tests/bugs/BUG_001.md）
    │      了解 Bug 描述、关联用例、复现步骤
    ├── 2. qoder test run --bug tests/bugs/BUG_001.md
    │      执行引擎自动找到关联脚本并执行
    ├── 3. 执行结果：
    │      ├── 通过 → qoder bug close BUG_001（更新状态）
    │      └── 仍失败 → Bug 状态变更为"重新打开"，附新执行记录
    └── 4. qoder sync --push
```

### 6.5 场景五：知识库驱动的用例优化

**背景**：AI 生成的用例质量不高，需要利用历史知识库改善

**触发条件**：工程内积累了一定量的需求文档、历史用例

**工作流程**：

```
测试工程师
    │
    ├── 1. qoder kb index（重建知识库索引）
    │      扫描工程内所有 .md 文件，更新向量索引
    ├── 2. qoder test generate --from requirements/xxx.md --with-kb
    │      AI 生成时，自动检索相关历史用例和业务文档作为参考
    └── 3. 生成质量更高，减少人工修改量
```

---

## 7. 系统架构概览

### 7.1 整体技术架构

```
┌────────────────────────────────────────────────────────────────┐
│                    Qoder CLI (Python)                           │
│  LangGraph 工作流 + LLM Provider（OpenAI/Azure/Ollama）         │
│  ├── Test Planner     ├── Case Generator  ├── Script Generator │
│  ├── Test Executor    ├── Result Analyzer └── Bug Creator      │
└────────────────────────────────────────────────────────────────┘
              │ 本地文件读写              │ HTTP API（可选）
              ▼                          ▼
┌──────────────────────┐    ┌───────────────────────────────────┐
│   Git 工程（本地）    │    │         测试平台 Backend           │
│  tests/              │◄──►│  Django REST Framework            │
│  ├── plans/          │    │  ├── 用例管理 API                  │
│  ├── cases/          │    │  ├── 执行管理 API                  │
│  ├── scripts/        │    │  ├── Bug 管理 API                  │
│  ├── reports/        │    │  ├── 知识库 API                    │
│  ├── bugs/           │    │  └── 同步 API                     │
│  └── ...             │    └───────────────────────────────────┘
└──────────────────────┘                │
                                        ▼
                         ┌──────────────────────────┐
                         │   测试平台 Frontend        │
                         │   Vue 3 + TypeScript       │
                         └──────────────────────────┘
                                        │
                         ┌──────────────────────────┐
                         │     执行引擎 (Python)      │
                         │  Playwright + Pytest       │
                         │  WebSocket 实时推送         │
                         └──────────────────────────┘
                                        │
                         ┌──────────────────────────┐
                         │       基础设施             │
                         │  PostgreSQL（元数据）      │
                         │  Redis（任务队列/缓存）     │
                         │  Qdrant（向量索引）        │
                         │  MinIO/本地存储（附件）    │
                         └──────────────────────────┘
```

### 7.2 技术栈选型

#### Qoder CLI

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | CLI 主语言 |
| LangGraph | 0.2+ | AI Agent 工作流编排 |
| LangChain | 0.3+ | LLM 调用抽象层 |
| Typer | 0.12+ | CLI 框架 |
| Rich | 13+ | 终端美化输出 |
| Playwright (Python) | 1.44+ | UI 测试脚本执行 |
| httpx | 0.27+ | HTTP 客户端（API 测试） |
| Pytest | 8+ | 测试运行器 |

#### 平台 Backend

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 后端语言 |
| Django | 5.x | Web 框架 |
| Django REST Framework | 3.15+ | API 框架 |
| Celery | 5.x | 异步任务队列 |
| PostgreSQL | 16+ | 主数据库 |
| Redis | 7+ | 缓存 + Celery Broker |
| Qdrant | 1.9+ | 向量数据库（知识库） |
| FastEmbed | 0.3+ | 向量嵌入模型（BAAI/bge-small-zh-v1.5） |
| Channels | 4.x | WebSocket |

#### 平台 Frontend

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue.js | 3.4+ | 前端框架 |
| TypeScript | 5.x | 类型系统 |
| Vite | 5.x | 构建工具 |
| Element Plus | 2.8+ | UI 组件库（与 WHartTest 保持一致） |
| ECharts | 5.x | 图表库 |

### 7.3 Git 工程目录规范

```
<project-root>/
├── requirements/           # 需求文档（知识库来源之一）
│   ├── features/
│   └── api/
├── docs/                   # 项目文档（知识库来源）
│   └── *.md
├── tests/
│   ├── .qoder/             # Qoder CLI 配置
│   │   ├── config.toml     # 项目配置（LLM、环境等）
│   │   └── skills/         # AI 生成技能文件
│   ├── plans/              # 测试计划（AI 生成 + 人工审核）
│   │   └── *.md
│   ├── cases/              # 测试用例（Markdown）
│   │   ├── login/
│   │   │   ├── TC_001_valid_login.md
│   │   │   └── TC_002_invalid_password.md
│   │   └── ...
│   ├── scripts/            # 测试脚本（Python）
│   │   ├── login/
│   │   │   ├── TC_001_valid_login.py
│   │   │   └── TC_002_invalid_password.py
│   │   └── ...
│   ├── data/               # 共享测试数据（可选）
│   ├── bugs/               # Bug 报告（Markdown）
│   │   ├── BUG_001_xxx.md
│   │   └── ...
│   ├── reports/            # 执行报告（自动生成）
│   │   └── run_20260412_001/
│   │       ├── summary.md
│   │       ├── screenshots/
│   │       └── logs/
│   └── conftest.py         # Pytest 全局配置
├── .env.test               # 测试环境变量（不入 Git）
└── .env.test.example       # 环境变量模板
```

### 7.4 测试用例 Markdown 格式规范

```markdown
---
id: TC_001
title: 有效用户名和密码登录成功
module: 用户认证 / 登录
priority: P0
type: functional
created_by: qoder-cli
created_at: 2026-04-12
script: ../scripts/login/TC_001_valid_login.py
tags: [login, smoke]
---

# TC_001：有效用户名和密码登录成功

## 前提条件
- 用户已注册，状态为激活
- 测试账号：test@example.com / Password123

## 测试步骤

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 打开登录页面 `/login` | 登录页面正常显示，包含用户名和密码输入框 |
| 2 | 输入用户名 `test@example.com` | 用户名字段填入成功 |
| 3 | 输入密码 `Password123` | 密码字段以掩码形式显示 |
| 4 | 点击"登录"按钮 | 按钮状态变为加载中 |
| 5 | 等待页面跳转 | 成功跳转至首页 `/dashboard` |
| 6 | 验证欢迎信息 | 页面显示"欢迎，test" |

## 输入数据
- 用户名：`test@example.com`
- 密码：`Password123`

## 备注
- 此用例为冒烟测试核心用例，每次发布必须执行
```

### 7.5 Bug Markdown 格式规范

```markdown
---
id: BUG_001
title: 登录页面：正确密码登录失败
severity: P1
status: open
module: 用户认证 / 登录
related_case: TC_001
related_script: tests/scripts/login/TC_001_valid_login.py
reporter: qoder-cli (auto)
assignee: 
created_at: 2026-04-12T10:30:00
updated_at: 2026-04-12T10:30:00
---

# BUG_001：登录页面：正确密码登录失败

## 问题描述
使用正确的用户名和密码登录时，系统返回"用户名或密码错误"提示，登录失败。

## 复现步骤
1. 打开登录页面 `/login`
2. 输入用户名 `test@example.com`
3. 输入密码 `Password123`
4. 点击"登录"按钮

## 期望结果
跳转至 `/dashboard`，显示"欢迎，test"

## 实际结果
页面显示红色提示："用户名或密码错误，请重试"

## 测试现场

### 截图
![失败截图](../reports/run_20260412_001/screenshots/TC_001_step4_fail.png)

### 错误日志
```
AssertionError: Expected URL to be '/dashboard', got '/login'
Error text on page: "用户名或密码错误，请重试"
Test duration: 3.2s
Browser: Chromium 124
```

## AI 分析
根据截图和日志分析，登录接口返回了 401 错误。可能原因：
1. 测试环境用户数据未正确初始化
2. 密码加密策略变更导致不兼容
3. 测试账号被锁定

**建议**：检查测试环境用户表，确认 `test@example.com` 账号存在且密码哈希正确。
```

---

## 8. 非功能性需求

### 8.1 性能需求

| 指标 | 要求 |
|------|------|
| CLI 用例生成速度 | 单次生成 ≤ 20 个用例，响应时间 < 60s |
| CLI 脚本生成速度 | 单次生成 ≤ 20 个脚本，响应时间 < 90s |
| 执行引擎并发 | 单机支持 ≥ 8 个并行脚本执行 |
| 平台 API 响应时间 | 95% 的请求 < 500ms |
| 知识库检索延迟 | 单次检索 < 2s |
| 平台并发用户 | 支持 50+ 并发用户 |

### 8.2 可用性需求

| 指标 | 要求 |
|------|------|
| 平台可用性 | 99%（允许计划内维护） |
| CLI 离线可用性 | 100%（不依赖平台） |
| 数据备份 | Git 仓库提供天然备份；平台 DB 每日备份 |

### 8.3 安全性需求

- **API Key 安全**：CLI 使用 API Key 认证，Key 不存储在 Git 仓库（通过环境变量注入）
- **LLM 数据安全**：CLI 配置支持指定私有化部署的 LLM，敏感业务数据不必发送到公共 LLM
- **权限控制**：平台采用 RBAC，项目隔离
- **审计日志**：所有平台操作记录审计日志

### 8.4 可扩展性需求

- **LLM 多供应商**：支持 OpenAI、Azure OpenAI、Ollama（本地）、通义千问等
- **测试框架扩展**：执行引擎支持插件化接入新的测试框架
- **外部集成**：Bug 管理支持集成管道（Jira、禅道），通过插件机制扩展

---

## 9. 产品路线图

### V1.0（MVP）—— CLI 优先，平台基础

**目标**：验证工程中心化模式的可行性，测试工程师可以端到端工作

- Qoder CLI：Planner + Case Generator + Script Generator
- 执行引擎：单机 Pytest + Playwright 执行
- 平台：用例管理（只读展示）+ 执行记录查看
- Bug 管理：本地 Markdown 创建，平台列表展示
- 知识库：基础向量索引（工程内 `.md`）

### V1.5 —— 协作增强

- CLI Analyzer：AI 自动分析执行结果，自动创建 Bug
- CLI Health Check：脚本健康度检查，识别腐化脚本
- 平台：Bug 状态流转、开发人员协作、测试计划管理
- 平台：统计报表（执行趋势、Bug 解决情况）、知识库浏览
- Git Webhook 自动同步（GitHub/GitLab）
- CI/CD 集成示例（GitHub Actions）

### V2.0 —— 协作与质量增强

- CLI Healer：AI 自动修复失败脚本（参考 Playwright Healer）
- 平台：测试计划管理、覆盖率统计、质量趋势看板
- 外部集成：Jira Bug 同步管道
- 性能测试模块（Locust）

### V3.0 —— 企业级

- 分布式执行引擎
- 多 Git 仓库支持
- 高级权限管理（组织层级）
- 完整的 CI/CD 生态集成

---

## 10. L1 需求索引

| L1 文档 | 对应模块 | 文件路径 |
|---------|---------|---------|
| L1-01：Qoder CLI Test Agent | M1 | [L1/L1-01_CLI_Test_Agent.md](./L1/L1-01_CLI_Test_Agent.md) |
| L1-02：测试用例管理 | M2 | [L1/L1-02_Test_Case_Management.md](./L1/L1-02_Test_Case_Management.md) |
| L1-03：UI 自动化测试 | M3 | [L1/L1-03_UI_Automation.md](./L1/L1-03_UI_Automation.md) |
| L1-04：API 自动化测试 | M4 | [L1/L1-04_API_Automation.md](./L1/L1-04_API_Automation.md) |
| L1-05：测试执行引擎 | M5 | [L1/L1-05_Execution_Engine.md](./L1/L1-05_Execution_Engine.md) |
| L1-06：Bug 管理 | M6 | [L1/L1-06_Bug_Management.md](./L1/L1-06_Bug_Management.md) |
| L1-07：知识库管理 | M7 | [L1/L1-07_Knowledge_Base.md](./L1/L1-07_Knowledge_Base.md) |
| L1-08：平台门户 | M8 | [L1/L1-08_Platform_Portal.md](./L1/L1-08_Platform_Portal.md) |

---

## 11. 术语表

| 术语 | 定义 |
|------|------|
| **Qoder CLI** | 本平台的命令行 AI Agent，集成 LangGraph 工作流 |
| **Test Agent** | Qoder CLI 在测试场景下的工作模式 |
| **测试计划（Test Plan）** | AI 生成的 Markdown 文件，描述测试范围、用例分类和优先级 |
| **测试用例（Test Case）** | Markdown 文件，描述单一业务场景的完整测试步骤和预期结果，无分支 |
| **测试脚本（Test Script）** | Python 文件，1:1 对应测试用例的可执行实现，包含测试数据 |
| **执行记录（Execution Record）** | 测试脚本执行后产生的结果，含通过/失败状态、日志、截图 |
| **Bug 报告（Bug Report）** | Markdown 文件，AI 自动或人工创建，描述缺陷现象和现场证据 |
| **测试现场（Test Scene）** | UI 测试：截图 + 文本日志；API 测试：请求/响应文本；通用：控制台日志 |
| **知识库（Knowledge Base）** | 工程内 `.md` 文件的向量索引，为 AI 生成提供业务上下文 |
| **工程中心化** | 测试资产以 Git 仓库文件为主，平台为辅的架构模式 |
| **Planner** | CLI 子命令，分析需求文档生成测试计划 |
| **Generator** | CLI 子命令，将测试计划转化为测试用例 Markdown 文件 |
| **Scripter** | CLI 子命令，将测试用例转化为 Python 测试脚本 |
| **Analyzer** | CLI 子命令，分析执行结果，自动创建 Bug |
| **Healer** | CLI 子命令（V2.0），自动修复失败的测试脚本 |

---

---

## 12. L1 汇总后的架构一致性说明

> 本章节基于所有 L1 文档（v1.0）编写完成后的反向审视结果，记录与初版 L0 的差异和更新要点。

### 12.1 设计决策确认

| 维度 | L0 初版 | L1 细化后确认 |
|------|---------|-------------|
| 前端 UI 组件库 | Arco Design Vue | **Element Plus**（与 WHartTest 保持一致，降低维护成本） |
| 嵌入模型 | FastEmbed（通用） | **BAAI/bge-small-zh-v1.5**（中文优化，256MB，CPU 可运行） |
| 知识库向量存储 | Qdrant（服务器） | **Qdrant 本地模式**（零依赖，数据文件在工程内，V1.0 首选） |
| UI 自动化对象仓库 | 计划中 | **不纳入 V1.0**（选择器内联在脚本中，降低维护复杂度） |
| WebSocket 实时推送 | V1.5 | **V1.0 必须**（执行监控是 V1.0 核心体验） |

### 12.2 V1.0 MVP 范围最终确认

**V1.0 必须包含**：
- M1：Qoder CLI（Planner + Generator + Scripter）
- M2：测试用例管理（同步 + 审核 + 列表展示）
- M3：UI 自动化（Playwright 脚本规范 + 失败截图）
- M4：API 自动化（Pytest + httpx 脚本规范 + 请求日志）
- M5：执行引擎（单机执行 + **WebSocket 实时推送** + 现场记录）
- M6：Bug 管理（AI 自动创建 + 状态管理 + Markdown 格式）
- M7：知识库（本地 Qdrant + BAAI 嵌入 + 增量更新）
- M8：平台门户（仪表盘 + 用例/执行/Bug 界面 + API Key 管理）

### 12.3 跨模块关键约定

1. **选择器规范统一**（M3 → M1）：CLI 生成 UI 脚本时必须优先使用 `get_by_role()`，禁止 XPath
2. **conftest.py 双模板**（M3 + M4 → M5）：UI 和 API 各有标准 conftest 模板，执行引擎统一用 `pytest --json-report` 收集结果
3. **截图路径约定**（M3 → M6）：失败截图存 `tests/reports/<exec-id>/screenshots/<test_name>_fail.png`，Bug Markdown 用相对路径引用
4. **环境变量注入约定**（M4 → M5）：敏感配置（Token、Key）通过执行引擎注入环境变量，不写入脚本文件
5. **知识库自动触发**（M7 → M1）：`qoder test generate` 前自动检测变更文件并增量更新知识库索引
6. **Bug ID 格式统一**（M6）：`BUG-{项目前缀}-{三位数字}`，如 `BUG-SHOP-001`，从工程内已有 Bug 文件自动递增

**文档版本**：L0 v1.1（L1 汇总后更新）
