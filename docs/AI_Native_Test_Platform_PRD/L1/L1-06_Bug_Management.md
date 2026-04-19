# L1-06：Bug 管理需求文档

## 文档信息

| 项目 | 内容 |
|------|------|
| 模块名称 | Bug 管理 |
| 模块编号 | M6 |
| 文档版本 | L1 v1.0 |
| 上级文档 | [L0_PRD.md](../L0_PRD.md) |

---

## 1. 模块概述

### 1.1 模块定位

Bug 管理模块以 **Markdown 文件为核心存储**，以 **Git 工程为版本控制**，提供缺陷的全生命周期管理。AI（Qoder CLI Analyzer）是 Bug 的主要创建者，人工作为审核和跟踪者。

**核心设计原则**：
- Bug 内容存储在 Git 工程的 Markdown 文件中，人类可直接阅读编辑
- AI 自动截图 + AI 自动生成分析，减少人工填写 Bug 的负担
- 平台数据库只存储状态、指派、元数据（不存储内容）
- 对外集成（Jira/禅道）通过独立的集成管道实现，不耦合核心逻辑

### 1.2 与相关模块的关系

| 交互方向 | 交互对象 | 交互内容 |
|---------|---------|---------|
| CLI（M1）→ M6 | Qoder CLI Analyzer | 自动创建 Bug Markdown 文件 |
| 执行引擎（M5）→ M6 | 执行失败事件 | 通知有失败，触发 Analyzer |
| M6 ↔ 用例管理（M2）| 双向关联 | Bug 关联测试用例 |
| M6 → 集成管道 | Jira/禅道 | 外部同步（V1.5+）|

---

## 2. 功能详细描述

### 2.1 F1：Bug 创建

#### 功能描述

支持两种 Bug 创建方式：AI 自动创建（主要）和人工手动创建。

#### 方式 A：AI 自动创建（qoder test analyze）

通过 CLI Analyzer 分析执行结果，自动生成 Bug Markdown 文件（详见 L1-01 F6）。

**自动化程度**：
- 执行失败 → 自动触发 Analyzer → 自动创建 Bug 文件 → `qoder sync push` 同步到平台

**Bug ID 生成规则**：
```
BUG_<三位递增序号>_<slug>
例：BUG_001_login_locked_account_not_shown
```

#### 方式 B：人工手动创建（平台 Web）

适用于手动测试中发现的问题，在平台上填写 Bug 信息，平台自动生成对应 Markdown 文件并写回 Git 仓库。

**创建表单字段**：

| 字段 | 必填 | 说明 |
|------|------|------|
| 标题 | ✓ | 简明描述问题 |
| 严重程度 | ✓ | P0 紧急 / P1 严重 / P2 一般 / P3 轻微 |
| 所属模块 | ✓ | 下拉选择（对应用例模块树） |
| 复现步骤 | ✓ | Markdown 格式文本 |
| 期望结果 | ✓ | |
| 实际结果 | ✓ | |
| 关联测试用例 | 可选 | 从用例库选择 |
| 截图/附件 | 可选 | 上传图片 |
| 指派给 | 可选 | 从项目成员选择 |

#### 验收标准

- [ ] AI 自动创建的 Bug 文件包含截图引用（UI 测试）或请求/响应文本（API 测试）
- [ ] 人工创建 Bug 后，平台自动生成 Markdown 文件并同步到 Git 仓库（通过 API 提交）
- [ ] Bug ID 自动递增，不与已有 ID 冲突

---

### 2.2 F2：Bug 内容格式规范（完整版）

#### Markdown 格式规范

```markdown
---
id: BUG_001
title: 登录页面：连续错误5次后账号未锁定
severity: P1
status: open
module: 用户认证/登录
related_case: TC_003
related_script: tests/scripts/login/TC_003_locked_account.py
reporter: qoder-cli
assignee: null
created_at: 2026-04-12T14:30:34Z
updated_at: 2026-04-12T14:30:34Z
verified_at: null
closed_at: null
tags: [login, security, p1]
---

# BUG_001：登录页面：连续错误5次后账号未锁定

## 问题描述

使用错误密码连续登录 5 次后，系统应显示"账号已锁定"并阻止继续登录，
但实际上仍显示"用户名或密码错误"，账号未被锁定。

## 环境信息

| 项目 | 值 |
|------|-----|
| 测试环境 | staging |
| 浏览器 | Chromium 124 |
| 测试时间 | 2026-04-12 14:30 |
| 执行记录 | tests/reports/run_20260412_143022/ |

## 复现步骤

| 步骤 | 操作 | 期望结果 | 实际结果 |
|------|------|----------|----------|
| 1 | 打开登录页面 `/login` | 页面正常显示 | ✓ 正常 |
| 2 | 输入正确用户名，错误密码，点击登录 | 显示错误提示 | ✓ 显示"用户名或密码错误" |
| 3 | 重复步骤 2，共 5 次 | 第 5 次后显示"账号已锁定" | ✗ 仍显示"用户名或密码错误" |
| 4 | 第 6 次尝试登录 | 应被阻止，提示账号锁定 | ✗ 仍可尝试登录 |

## 测试现场

### 截图（第 5 次失败时）

![第5次登录失败截图](../reports/run_20260412_143022/screenshots/TC_003_locked_account_fail.png)

### 错误日志

```
FAILED tests/scripts/login/TC_003_locked_account.py::test_TC_003_locked_account
AssertionError: Expected page to contain text '账号已锁定'
  Actual text found: "用户名或密码错误，请重试"
  Current URL: http://staging.example.com/login
  Test duration: 2.1s
```

## AI 分析

**根因推断**：
登录页面未正确触发账号锁定逻辑。可能原因：
1. 用户服务中的失败次数计数器未正确累积（Redis 缓存 Key 设计问题）
2. 锁定阈值配置错误（配置值不是 5 次）
3. 前端未正确展示后端返回的锁定状态

**建议排查步骤**：
1. 检查 Redis 中 `login_fail_count:test@example.com` 的值是否正确递增
2. 确认用户服务中的锁定阈值配置 `MAX_LOGIN_ATTEMPTS=5`
3. 检查登录 API 响应，在第 5 次失败时是否返回了不同的错误码

## 处理记录

| 时间 | 操作人 | 操作 | 备注 |
|------|--------|------|------|
| 2026-04-12 14:30 | qoder-cli | 创建 Bug | 自动创建 |
```

---

### 2.3 F3：Bug 生命周期管理

#### Bug 状态流转

```
open（新建）
  │
  ├──→ in_progress（处理中）   [开发接手]
  │         │
  │         ├──→ resolved（已解决）   [开发完成修复]
  │         │         │
  │         │         ├──→ verified（已验证）  [测试工程师验证通过]
  │         │         │         │
  │         │         │         └──→ closed（已关闭）
  │         │         │
  │         │         └──→ reopened（重新打开）[验证失败]
  │         │                   │
  │         │                   └──→ in_progress（再次处理）
  │         │
  │         └──→ wont_fix（不修复）  [已确认，不处理]
  │
  └──→ duplicate（重复）
```

#### 状态变更操作

| 当前状态 | 允许的操作 | 操作后状态 | 操作人 |
|---------|---------|---------|------|
| open | 指派给开发 | in_progress | 测试工程师/测试经理 |
| open | 标记重复 | duplicate | 任意 |
| in_progress | 标记已解决 | resolved | 开发工程师 |
| in_progress | 不修复 | wont_fix | 测试经理 |
| resolved | 验证通过 | verified | 测试工程师 |
| resolved | 验证失败 | reopened | 测试工程师 |
| reopened | 重新处理 | in_progress | 开发工程师 |
| verified | 关闭 | closed | 测试工程师/测试经理 |

#### Bug 状态在 Markdown Front Matter 中的同步

每次状态变更，平台自动更新对应 Markdown 文件的 Front Matter：

```markdown
---
status: resolved      # 由 open 变更为 resolved
assignee: dev@example.com
updated_at: 2026-04-13T09:00:00Z
---
```

通过 `qoder sync pull` 可拉取最新状态到本地文件。

#### 验收标准

- [ ] 状态变更记录在 Bug Markdown 文件的"处理记录"表格中
- [ ] 状态变更后平台自动更新 Markdown Front Matter
- [ ] 每次状态变更通知相关人员（可配置：平台通知 / 邮件）

---

### 2.4 F4：Bug 列表与搜索

#### 列表功能

| 功能点 | 描述 | 优先级 |
|--------|------|--------|
| Bug 列表 | 展示项目下所有 Bug，默认按创建时间倒序 | P0 |
| 多维过滤 | 按严重程度、状态、模块、指派人过滤 | P0 |
| 关键词搜索 | 搜索 Bug 标题和描述 | P0 |
| Bug 详情 | 渲染 Markdown 内容，含截图展示 | P0 |
| 统计看板 | 按状态/严重程度/模块的分布图表 | P1 |
| 趋势分析 | 30 天 Bug 新增/关闭趋势折线图 | P2 |

#### Bug 列表字段

| 字段 | 说明 |
|------|------|
| Bug ID | BUG_001 格式 |
| 标题 | 来自 Front Matter `title` |
| 严重程度 | P0-P3 彩色标签 |
| 状态 | 状态标签（彩色） |
| 所属模块 | 模块路径 |
| 关联用例 | TC_XXX 链接 |
| 指派给 | 用户名 |
| 创建时间 | 相对时间（"2小时前"）|
| 最后更新 | 相对时间 |

#### 验收标准

- [ ] Bug 详情页正确渲染 Markdown，截图内联展示（不跳转）
- [ ] 过滤和搜索响应时间 < 1s

---

### 2.5 F5：Bug 验证工作流

#### 功能描述

测试工程师通过 CLI 快速验证 Bug 修复是否有效。

#### 工作流

```bash
# 开发修复后，测试工程师执行：
qoder test run --bug tests/bugs/BUG_001_locked_account.md

# 执行引擎自动：
# 1. 读取 Bug Markdown 中的 related_script 字段
# 2. 执行对应脚本：tests/scripts/login/TC_003_locked_account.py
# 3. 输出执行结果

# 如果通过：
qoder bug close BUG_001
# → 更新 Markdown Front Matter：status=verified, verified_at=now
# → qoder sync push 同步到平台

# 如果仍失败：
# → 自动更新 Markdown：status=reopened
# → 附新的执行记录链接
# → qoder sync push 同步到平台
```

#### CLI Bug 命令

```bash
qoder bug list                      # 列出所有 open Bug
qoder bug list --status open        # 按状态过滤
qoder bug show BUG_001              # 查看 Bug 详情
qoder bug close BUG_001             # 关闭 Bug（设为 verified）
qoder bug reopen BUG_001 --reason "仍然复现"  # 重新打开
```

#### 验收标准

- [ ] `qoder test run --bug <bug.md>` 自动执行关联脚本
- [ ] 执行通过时，`qoder bug close` 更新 Markdown 状态并同步平台
- [ ] 执行失败时，自动创建新的执行记录并附加到 Bug 的处理历史

---

### 2.6 F6：集成管道（V1.5+）

#### 功能描述

将平台 Bug 同步到外部缺陷管理系统（Jira / 禅道）。采用插件化的集成管道架构，核心模块不耦合具体外部系统。

#### 集成管道架构

```
Bug 状态变更事件（平台内部）
    │
    ▼
集成管道触发器
    │
    ├── Jira 适配器（插件）
    │   ├── 创建 Jira Issue（Bug open 时）
    │   ├── 更新 Jira Issue 状态（Bug 状态变更时）
    │   └── 关联 Jira Issue ID 写回 Bug Markdown
    │
    └── 禅道适配器（插件，预留）
```

#### 配置（.qoder/config.toml）

```toml
[integrations.jira]
enabled = true
url = "https://company.atlassian.net"
project_key = "TEST"
api_token = ""  # 从环境变量 JIRA_API_TOKEN 读取
username = "qa@company.com"

# Bug 严重程度映射
[integrations.jira.severity_map]
P0 = "Blocker"
P1 = "Critical"
P2 = "Major"
P3 = "Minor"
```

#### 验收标准（V1.5+）

- [ ] Bug 创建后自动在 Jira 创建对应 Issue
- [ ] Jira Issue ID 回写到 Bug Markdown Front Matter
- [ ] Bug 状态变更后 Jira Issue 状态同步更新
- [ ] 集成失败时记录错误，不影响平台核心功能

---

## 3. 数据模型

### 3.1 数据库模型（平台侧，仅元数据）

```sql
CREATE TABLE bugs (
    id          VARCHAR(20) PRIMARY KEY,  -- BUG_001
    project_id  UUID NOT NULL,
    title       VARCHAR(500),
    severity    VARCHAR(5),               -- P0/P1/P2/P3
    status      VARCHAR(20),             -- open/in_progress/resolved/verified/closed/wont_fix/duplicate/reopened
    module      VARCHAR(200),
    related_case_id VARCHAR(20),         -- TC_001
    reporter    VARCHAR(100),
    assignee_id UUID,
    file_path   VARCHAR(500),            -- Git 仓库中的文件路径
    jira_issue_id VARCHAR(50),          -- Jira 集成 ID
    created_at  TIMESTAMPTZ,
    updated_at  TIMESTAMPTZ,
    verified_at TIMESTAMPTZ,
    closed_at   TIMESTAMPTZ
);

CREATE TABLE bug_status_history (
    id          UUID PRIMARY KEY,
    bug_id      VARCHAR(20) REFERENCES bugs(id),
    from_status VARCHAR(20),
    to_status   VARCHAR(20),
    changed_by  UUID,
    comment     TEXT,
    changed_at  TIMESTAMPTZ
);
```

---

## 4. 与其他模块的接口规范

### 4.1 平台 REST API

```
# Bug 同步（CLI push）
POST /api/v1/projects/{project_id}/bugs/sync
Body: {
  "bugs": [
    {"id": "BUG_001", "file_path": "...", "content": "...", "updated_at": "..."}
  ]
}

# Bug 状态变更
PATCH /api/v1/bugs/{bug_id}/status
Body: { "status": "in_progress", "assignee_id": "uuid", "comment": "开始处理" }

# Bug 列表
GET /api/v1/projects/{project_id}/bugs
  ?status=open&severity=P1&module=用户认证

# Bug 详情（含 Markdown 内容）
GET /api/v1/bugs/{bug_id}
```

---

## 5. 验收标准汇总

| 编号 | 验收标准 | 优先级 |
|------|---------|--------|
| AC-01 | AI 自动创建 Bug 时，Markdown 内含截图引用和 AI 分析 | P0 |
| AC-02 | Bug 状态流转正确，不允许非法状态跳转 | P0 |
| AC-03 | 状态变更同步更新 Markdown Front Matter | P0 |
| AC-04 | `qoder test run --bug` 自动执行关联脚本验证 Bug | P0 |
| AC-05 | Bug 列表支持多维过滤和关键词搜索 | P0 |
| AC-06 | Bug 详情页内联展示截图（不跳转外链）| P1 |
| AC-07 | Bug 处理记录表格自动记录每次状态变更 | P1 |
| AC-08 | Jira 集成管道可配置，失败时不影响核心功能 | P2 |
