# L1-08：平台门户模块需求

**文档版本**：v1.0  
**所属模块**：M8 - 平台门户（展示层）  
**依赖模块**：M2~M7（所有业务模块的 API）  
**最后更新**：2026-04-12

---

## 1. 模块定位

平台门户是面向全体用户的 Web 协作界面，提供测试资产的可视化管理、执行监控和协作审批功能。

**核心职责**：
- 提供测试用例、Bug、执行记录的浏览和管理界面
- 提供实时执行监控（WebSocket 推送）
- 提供团队协作功能（评审、权限、通知）
- 提供统计报表和项目仪表盘
- 作为 CLI 生成内容的"同步展示层"

**设计原则**：
- **工程为主，平台为辅**：平台展示的一切来自 Git 工程同步，平台不是主要创作工具
- **CLI 优先，Web 补充**：创建/生成由 CLI 完成；审批、评审、报表由 Web 完成
- **轻量低维护**：平台只存索引和元数据，不存 Markdown 文件内容的副本（存内容 Hash）

---

## 2. 功能清单

| 编号 | 功能 | 优先级 | 版本 |
|------|------|--------|------|
| F8.1 | 项目仪表盘 | P0 | V1.0 |
| F8.2 | 测试用例管理界面 | P0 | V1.0 |
| F8.3 | 执行监控界面 | P0 | V1.0 |
| F8.4 | Bug 管理界面 | P0 | V1.0 |
| F8.5 | 用户和权限管理 | P0 | V1.0 |
| F8.6 | 测试计划管理 | P1 | V1.5 |
| F8.7 | 统计报表 | P1 | V1.5 |
| F8.8 | 知识库浏览 | P1 | V1.5 |
| F8.9 | Git Webhook 集成 | P1 | V1.5 |
| F8.10 | 通知中心 | P2 | V2.0 |

---

## 3. F8.1 项目仪表盘

### 3.1 功能描述

每个项目（对应一个 Git 工程）有独立的仪表盘，展示项目整体测试健康状况。

### 3.2 仪表盘组件

**顶部指标卡（Overview Cards）**：

| 指标 | 说明 |
|------|------|
| 用例总数 | 所有已同步用例数 |
| 通过率 | 最近一次执行的通过率（Pass/Total） |
| 开放 Bug 数 | status = open 或 in_progress 的 Bug 数 |
| 最近执行时间 | 最近一次执行任务的结束时间 |

**测试趋势图（近 30 天）**：
- 折线图：每日执行通过率趋势
- 柱状图：每日 Bug 新增/修复数量

**最近执行记录（Recent Executions）**：
- 表格展示最近 10 次执行记录
- 列：执行时间、触发方式（CLI/平台/CI）、Suite、通过/失败/跳过数、耗时、状态

**待审核用例（Pending Review）**：
- 列表展示 status = draft 的用例
- 快速审核按钮（approve）

**开放 Bug 优先级分布**：
- 饼图：P0/P1/P2/P3 Bug 数量分布

### 3.3 API 规范

```
GET /api/projects/{project_id}/dashboard
Response: {
  overview: {
    total_cases: number,
    latest_pass_rate: number,      // 0~1
    open_bug_count: number,
    last_execution_time: string,   // ISO 8601
  },
  trend: {
    dates: string[],               // 近30天日期
    pass_rates: number[],
    bug_added: number[],
    bug_fixed: number[],
  },
  recent_executions: ExecutionRecord[],
  pending_review_cases: TestCase[],
  bug_priority_distribution: {P0: n, P1: n, P2: n, P3: n},
}
```

---

## 4. F8.2 测试用例管理界面

### 4.1 用例列表页

**布局**：左侧目录树 + 右侧用例列表

**左侧目录树**：
- 按 Git 工程目录结构展示（`tests/cases/` 目录树）
- 支持展开/折叠
- 显示每个目录下的用例数量
- 节点颜色：绿（全通过）/ 黄（部分失败）/ 红（全失败）/ 灰（未执行）

**右侧用例列表**：

| 列 | 说明 |
|----|------|
| 用例 ID | TC-001 等，可点击进入详情 |
| 标题 | 用例标题 |
| 类型 | UI / API |
| 优先级 | P0 / P1 / P2 |
| 状态 | draft / approved |
| 最近执行结果 | pass / fail / skip / — |
| 关联 Bug | 当前开放 Bug 数量（红色徽标） |
| 最后更新 | Git 提交时间 |

**操作**：
- 搜索：标题、ID、标签全文搜索
- 筛选：类型、优先级、状态、执行结果
- 批量选择 → 创建执行任务
- 单行右键菜单：查看详情、审核通过、创建执行、查看关联 Bug

### 4.2 用例详情页

**页面结构**：

```
[面包屑导航] 项目 > tests/cases/auth > TC-001

[左侧]                         [右侧]
用例元数据                      Markdown 内容渲染
  ID: TC-001                    # 用户登录 - 有效凭证
  模块: auth                    
  类型: UI                      ## 前提条件
  优先级: P1                    ...
  状态: approved [改为草稿]      
  标签: login, auth             ## 测试步骤
  创建时间: 2026-04-01          ...
  最后同步: 2026-04-12          
                                ## 预期结果
执行历史（最近5次）             ...
  ✓ 2026-04-12 10:00 通过
  ✓ 2026-04-11 14:30 通过      
  ✗ 2026-04-10 09:15 失败 [查看]
  
关联 Bug
  BUG-003 [open] 登录跳转延迟
  
关联脚本
  tests/scripts/ui/test_auth_tc_001.py
  [在平台查看] [下载]
```

### 4.3 用例评审工作流

```
[draft] 
    ↓ 测试工程师 / 测试经理点击"审核通过"
[approved]
    ↓ 用例有改动（通过 Git Webhook 检测到 content_hash 变化）
[draft]（自动降级）
```

**评审操作 API**：

```
PATCH /api/cases/{case_id}/status
Body: {"status": "approved", "reviewer": "user_id", "comment": "符合要求"}
```

---

## 5. F8.3 执行监控界面

### 5.1 执行任务列表页

**列表字段**：

| 列 | 说明 |
|----|------|
| 执行 ID | exec-001 等 |
| 触发方式 | CLI / 平台手动 / CI（Webhook） |
| Suite/用例 | 执行范围描述 |
| 状态 | pending / running / completed / failed / cancelled |
| 进度 | 进行中显示 "3/10 完成" |
| 通过/失败/跳过 | 结果统计 |
| 耗时 | 秒/分钟 |
| 触发时间 | |
| 操作 | [查看详情] [停止]（进行中） |

**操作**：
- 从平台创建新执行：选择用例范围 + 环境配置 → 提交（调用 CLI 或直接调度执行引擎）
- 搜索和筛选

### 5.2 执行详情页（实时监控）

**页面结构**：

```
[执行 ID: exec-001]  状态: 运行中 ●  进度: 4/10  通过: 3  失败: 1

[实时日志流]                          [脚本结果列表]
─────────────────────────────         ──────────────────────────────
[10:00:01] 开始执行 Suite: regression  ✓ test_login_tc_001         0.8s
[10:00:01] 启动 pytest 子进程          ✓ test_register_tc_002      1.2s
[10:00:02] RUNNING: test_login_tc_001  ✗ test_checkout_tc_012      2.1s [查看]
[10:00:03] PASSED: test_login_tc_001   ⏳ test_search_tc_031       running
[10:00:03] RUNNING: test_register_...  ○ test_payment_tc_041       pending
...（WebSocket 实时追加）              ○ ...（共10个）
```

**WebSocket 连接**：
- 连接端点：`ws://platform/ws/executions/{execution_id}`
- 前端订阅后，实时接收日志行和状态更新
- 连接断开后自动重连（3秒间隔）

**失败脚本详情抽屉**：
点击"查看"展开侧边抽屉：
- 失败原因（断言错误消息）
- 截图（UI 测试）或请求/响应日志（API 测试）
- "创建 Bug"按钮（预填失败信息）
- "在 CLI 修复"提示（显示 `qoder test heal TC-012`）

### 5.3 API 规范

```
GET /api/executions                          → 执行列表
POST /api/executions                         → 创建执行任务
GET /api/executions/{id}                     → 执行详情
DELETE /api/executions/{id}                  → 取消执行（running 状态）
GET /api/executions/{id}/scripts             → 脚本结果列表
GET /api/executions/{id}/scripts/{script_id} → 单脚本详情（含日志、截图）
WS  /ws/executions/{id}                      → 实时日志推送
```

---

## 6. F8.4 Bug 管理界面

### 6.1 Bug 列表页

**列表字段**：

| 列 | 说明 |
|----|------|
| Bug ID | BUG-001 等 |
| 标题 | Bug 简要描述 |
| 状态 | open / in_progress / resolved / verified / closed 等 |
| 优先级 | P0~P3（颜色标识：P0=红，P1=橙，P2=黄，P3=灰） |
| 关联用例 | TC-001 等 |
| 负责人 | 开发工程师 |
| 报告人 | 创建者（CLI 自动创建则显示"自动" + 测试工程师名） |
| 创建时间 | |
| 最近更新 | |

**视图切换**：
- 列表视图（默认）
- 看板视图（Kanban）：按状态分列（open / in_progress / resolved / verified）

**筛选**：状态、优先级、负责人、报告人、关联用例、创建时间范围

### 6.2 Bug 详情页

**页面结构**：

```
[BUG-001] 登录按钮在 Firefox 下无响应  [open ▼]  P1  负责人: @developer

[标签页: 详情 | 历史 | 关联]

详情标签页：
─────────────────────────────────────────────
[左侧：Markdown 渲染]
  ## 问题描述
  在 Firefox 浏览器下，点击登录按钮无任何响应...

  ## 复现步骤
  1. 使用 Firefox 打开登录页...

  ## 附件
  [截图: login_fail_firefox.png]

[右侧：元数据]
  状态：open [修改]
  优先级：P1 [修改]
  负责人：@developer [修改]
  关联用例：TC-001
  环境：Firefox 128
  创建时间：2026-04-10 09:15
  最近更新：2026-04-11 14:30
  
  [操作]
  [开始处理]  →  in_progress
  [标记已修复] → resolved
  [关闭 Bug]  → closed
  [标记重复]  → duplicate
```

**历史标签页**：
- 时间线展示 Bug 状态变更历史（谁在何时将状态从 X 改为 Y，附备注）

**关联标签页**：
- 关联的测试用例
- 关联的执行记录（哪次执行发现了此 Bug）

### 6.3 Bug 工作流操作 API

```
PATCH /api/bugs/{bug_id}/status
Body: {
  "status": "in_progress",
  "assignee": "developer_user_id",
  "comment": "已定位问题，预计明天修复"
}

Response: {
  "bug_id": "BUG-001",
  "old_status": "open",
  "new_status": "in_progress",
  "updated_by": "developer_user_id",
  "updated_at": "2026-04-12T10:00:00Z"
}
```

---

## 7. F8.5 用户和权限管理

### 7.1 用户角色定义

| 角色 | 英文标识 | 说明 |
|------|---------|------|
| 系统管理员 | admin | 管理全局配置、用户账号、项目 |
| 测试经理 | test_manager | 管理测试计划、审核用例、查看报表 |
| 测试工程师 | tester | 使用 CLI 生成测试资产，管理用例、Bug |
| 开发工程师 | developer | 查看 Bug、更新 Bug 状态 |
| 只读访客 | viewer | 只读访问所有内容 |

### 7.2 权限矩阵

| 操作 | admin | test_manager | tester | developer | viewer |
|------|-------|-------------|--------|-----------|--------|
| 查看用例/Bug/报告 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 审核用例 | ✓ | ✓ | — | — | — |
| 创建执行任务 | ✓ | ✓ | ✓ | — | — |
| 修改 Bug 状态 | ✓ | ✓ | ✓ | ✓（自己负责的）| — |
| 管理 API Key | ✓ | ✓ | ✓（自己的）| — | — |
| 管理用户 | ✓ | — | — | — | — |
| 管理项目 | ✓ | ✓ | — | — | — |
| 触发知识库重建 | ✓ | ✓ | — | — | — |

### 7.3 API Key 管理界面

测试工程师通过平台生成 API Key，用于 CLI 认证：

```
我的 API Keys

  名称           创建时间        最后使用         操作
  ─────────────  ─────────────  ───────────────  ───────────
  laptop-work    2026-04-01     2026-04-12       [撤销]
  ci-server      2026-04-05     2026-04-11       [撤销]
  
  [+ 生成新 Key]
```

**生成 Key 时仅展示一次完整 Key**，后续只显示末4位（安全策略）。

### 7.4 用户管理 API

```
GET    /api/users                  → 用户列表（admin）
POST   /api/users                  → 创建用户（admin）
PATCH  /api/users/{id}             → 修改用户信息/角色（admin）
DELETE /api/users/{id}             → 停用用户（admin）

GET    /api/api-keys               → 当前用户的 API Key 列表
POST   /api/api-keys               → 生成新 API Key
DELETE /api/api-keys/{key_id}      → 撤销 API Key
```

---

## 8. F8.6 测试计划管理（V1.5）

### 8.1 功能描述

测试计划是平台侧的组织概念，用于将一批测试用例组合为一个有目标、有时间线的测试活动。

**测试计划与 CLI 计划文件的区别**：
- CLI 生成的 `plans/TC-PLAN-001.md`：偏技术，描述执行策略和用例清单
- 平台测试计划：偏管理，包含目标、进度追踪、里程碑

### 8.2 测试计划字段

```
计划名称：v2.1.0 回归测试
状态：进行中
开始日期：2026-04-15
截止日期：2026-04-18
测试经理：@test_manager
描述：v2.1.0 版本全量回归，重点验证支付模块

用例范围：
  [+] 从目录选择  [+] 按标签筛选
  已选：47 个用例（auth: 10, order: 20, payment: 17）

进度：
  总计 47 个用例
  ✓ 已通过 32  ✗ 失败 3  ○ 未执行 12
  进度：74%
```

---

## 9. F8.7 统计报表（V1.5）

### 9.1 支持的报表类型

| 报表 | 说明 | 维度 |
|------|------|------|
| 测试覆盖率报表 | 用例覆盖需求的比例 | 按模块/优先级 |
| 执行结果趋势 | 每日/每周通过率变化 | 按 Suite/时间 |
| Bug 解决情况 | Bug 生命周期统计 | 按优先级/负责人 |
| 缺陷密度 | Bug 数 / 用例数 | 按模块 |
| 用例健康度 | 成功率/执行频率/最近执行时间 | 按用例 |

### 9.2 报表导出

- 格式：PDF、CSV、PNG（图表截图）
- 触发：手动导出或定时发送（V2.0）

---

## 10. F8.9 Git Webhook 集成（V1.5）

### 10.1 功能描述

配置 Git 仓库的 Webhook，当代码推送时自动触发平台同步。

### 10.2 Webhook 事件

| 事件 | 触发动作 |
|------|---------|
| Push（含 `tests/cases/` 变更） | 增量同步测试用例 |
| Push（含 `tests/bugs/` 变更） | 增量同步 Bug |
| Pull Request Merged | 触发回归测试套件执行（可配置） |
| Tag Created | 触发完整测试套件执行（可配置） |

### 10.3 Webhook 配置界面

```
项目设置 > Webhook 集成

Git 平台：[GitHub ▼]
Webhook URL：https://platform.example.com/webhooks/github/project-001
Secret Token：[生成]  ●●●●●●●●

事件配置：
  ☑ Push：自动同步 tests/cases/ 和 tests/bugs/ 变更
  ☑ PR Merged：触发 Suite 执行（Suite: regression）
  □ Tag Created：触发完整测试执行

[保存]  [测试 Webhook]
```

---

## 11. 技术实现要点

### 11.1 前端技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| 框架 | Vue 3 + TypeScript | 与 WHartTest 保持一致 |
| UI 组件库 | Element Plus | 企业级组件库 |
| 状态管理 | Pinia | Vue 3 官方推荐 |
| 路由 | Vue Router 4 | |
| HTTP 客户端 | Axios | |
| WebSocket | 原生 WebSocket API | 自动重连封装 |
| Markdown 渲染 | markdown-it + highlight.js | |
| 图表 | ECharts | 支持趋势图、饼图、柱状图 |
| 代码构建 | Vite | |

### 11.2 后端技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| 框架 | Django 5 + DRF | 与 WHartTest 保持一致 |
| 数据库 | PostgreSQL | 主数据库 |
| 缓存 | Redis | Session、WebSocket 状态 |
| 任务队列 | Celery + Redis | 执行调度 |
| WebSocket | Django Channels | 实时日志推送 |
| 认证 | JWT + API Key | 双模式认证 |

### 11.3 WebSocket 集成

前端 WebSocket 封装：

```typescript
// useExecution.ts
import { ref, onUnmounted } from 'vue'

export function useExecutionWS(executionId: string) {
  const logs = ref<string[]>([])
  const scriptResults = ref<ScriptResult[]>([])
  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout>

  const connect = () => {
    ws = new WebSocket(`ws://${location.host}/ws/executions/${executionId}`)
    
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      if (msg.type === 'log') {
        logs.value.push(msg.data)
      } else if (msg.type === 'script_result') {
        updateScriptResult(msg.data)
      }
    }
    
    ws.onclose = () => {
      reconnectTimer = setTimeout(connect, 3000)
    }
  }
  
  const disconnect = () => {
    clearTimeout(reconnectTimer)
    ws?.close()
  }
  
  onUnmounted(disconnect)
  connect()
  
  return { logs, scriptResults, disconnect }
}
```

### 11.4 页面路由结构

```
/login                              登录页
/                                   跳转到默认项目
/projects                           项目列表
/projects/{id}/dashboard            项目仪表盘
/projects/{id}/cases                用例列表
/projects/{id}/cases/{case_id}      用例详情
/projects/{id}/executions           执行列表
/projects/{id}/executions/{exec_id} 执行详情（实时监控）
/projects/{id}/bugs                 Bug 列表
/projects/{id}/bugs/{bug_id}        Bug 详情
/projects/{id}/plans                测试计划（V1.5）
/projects/{id}/reports              报表（V1.5）
/projects/{id}/kb                   知识库浏览（V1.5）
/projects/{id}/settings             项目设置
/admin/users                        用户管理（管理员）
/profile/api-keys                   API Key 管理
```

---

## 12. 与其他模块的接口规范

### 12.1 → M2（测试用例管理）

| 接口 | 方向 | 说明 |
|------|------|------|
| `GET /api/cases` | 平台调用 | 用例列表和搜索 |
| `PATCH /api/cases/{id}/status` | 平台调用 | 审核用例 |
| Webhook 同步触发 | 平台接收 | Git Push 触发用例同步 |

### 12.2 → M5（执行引擎）

| 接口 | 方向 | 说明 |
|------|------|------|
| `POST /api/executions` | 平台调用 | 创建执行任务 |
| `GET /api/executions/{id}` | 平台调用 | 查询执行状态 |
| `DELETE /api/executions/{id}` | 平台调用 | 停止执行 |
| `WS /ws/executions/{id}` | 平台订阅 | 实时日志推送 |

### 12.3 → M6（Bug 管理）

| 接口 | 方向 | 说明 |
|------|------|------|
| `GET /api/bugs` | 平台调用 | Bug 列表和搜索 |
| `PATCH /api/bugs/{id}/status` | 平台调用 | 修改 Bug 状态 |

### 12.4 → M7（知识库）

| 接口 | 方向 | 说明 |
|------|------|------|
| `GET /api/kb/files` | 平台调用 | 知识文件列表 |
| `GET /api/kb/search` | 平台调用 | 语义搜索 |
| `POST /api/kb/reindex` | 平台调用 | 触发重建（V1.5） |

---

## 13. 验收标准汇总

### MVP（V1.0）必须满足

- [ ] 项目仪表盘展示4个核心指标卡和最近执行记录
- [ ] 用例列表支持目录树浏览、状态筛选和搜索
- [ ] 用例详情展示 Markdown 渲染内容和执行历史
- [ ] 执行监控页 WebSocket 实时展示日志（延迟 < 1秒）
- [ ] 失败脚本详情可查看截图（UI 测试）或日志（API 测试）
- [ ] Bug 列表支持看板视图和列表视图
- [ ] API Key 生成和管理功能
- [ ] 基于角色的页面访问控制

### V1.5 满足

- [ ] 测试计划创建、进度追踪
- [ ] 执行结果趋势报表（近30天）
- [ ] Bug 解决情况报表
- [ ] Git Webhook 自动同步配置界面
- [ ] 知识库浏览和语义搜索页面

### V2.0 满足

- [ ] 报表 PDF/CSV 导出
- [ ] 定时报表邮件发送
- [ ] 通知中心（站内通知 + 企业微信/钉钉可选集成）

---

## 14. 附录：关键页面线框图描述

### A. 执行监控页（实时）

```
┌─────────────────────────────────────────────────────────┐
│ ← 执行列表  exec-001  [running ●]  进度: 4/10           │
├────────────────────────┬────────────────────────────────│
│ 实时日志                │ 脚本结果                       │
│ ─────────────────────  │ ─────────────────────────────  │
│ [10:00:01] 开始执行... │ ✓ test_login_tc_001     0.8s  │
│ [10:00:02] RUNNING:... │ ✓ test_register_tc_002  1.2s  │
│ [10:00:03] PASSED:...  │ ✗ test_checkout_tc_012  2.1s  │
│ [10:00:04] RUNNING:... │   └─[查看失败详情]             │
│ ...（自动滚动到底部）   │ ⏳ test_search_tc_031  running│
│                        │ ○  test_payment_tc_041  —      │
│                        │ ○  （共10个）                  │
│                        │                                │
│                        │ [停止执行]                     │
└────────────────────────┴────────────────────────────────┘
```

### B. Bug 看板视图

```
┌──────────────────────────────────────────────────────────────┐
│ Bug 管理  [列表 | 看板●]  [+ 创建 Bug]  [筛选]              │
├──────────────┬──────────────┬──────────────┬─────────────────│
│ Open (5)     │ 处理中 (3)   │ 已修复 (2)   │ 已验证 (1)     │
│ ──────────── │ ──────────── │ ──────────── │ ─────────────   │
│ ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐ │ ┌───────────┐  │
│ │P0 BUG-007│ │ │P1 BUG-003│ │ │P2 BUG-001│ │ │P1 BUG-002 │  │
│ │登录崩溃  │ │ │FF按钮无响│ │ │样式错位  │ │ │注册404    │  │
│ └──────────┘ │ └──────────┘ │ └──────────┘ │ └───────────┘  │
│ ┌──────────┐ │ ...          │ ...          │                 │
│ │P1 BUG-008│ │              │              │                 │
│ │...       │ │              │              │                 │
│ └──────────┘ │              │              │                 │
└──────────────┴──────────────┴──────────────┴─────────────────┘
```
