# L1-02：测试用例管理需求文档

## 文档信息

| 项目 | 内容 |
|------|------|
| 模块名称 | 测试用例管理 |
| 模块编号 | M2 |
| 文档版本 | L1 v1.0 |
| 上级文档 | [L0_PRD.md](../L0_PRD.md) |

---

## 1. 模块概述

### 1.1 模块定位

测试用例管理是平台侧的核心模块，负责对 Git 工程中的测试用例 Markdown 文件进行**索引、展示、协作和生命周期管理**。

**核心设计原则**：
- 平台不是用例内容的主存储，Git 仓库文件才是
- 平台提供用例的可视化浏览、搜索和协作（评审、审批）
- 用例内容变更以 Git 提交为准，平台通过同步钩子更新索引

### 1.2 与相关模块的关系

| 交互方向 | 交互对象 | 交互内容 |
|---------|---------|---------|
| M2 ← CLI（M1） | Qoder CLI | 接收用例同步（push），更新索引 |
| M2 → 执行引擎（M5） | 执行平台 | 创建测试计划，关联用例到执行任务 |
| M2 ← Git Webhook | Git 仓库 | 监听文件变更，自动刷新索引 |
| M2 ↔ Bug 管理（M6） | Bug 模块 | 用例关联 Bug，Bug 关联用例 |

---

## 2. 功能详细描述

### 2.1 F1：用例库（Case Library）

#### 功能描述

以树形目录结构展示项目下所有测试用例，镜像 Git 工程中 `tests/cases/` 的目录结构。

#### 界面功能

| 功能点 | 描述 | 优先级 |
|--------|------|--------|
| 树形模块导航 | 左侧展示模块树（对应 cases/ 目录结构） | P0 |
| 用例列表 | 右侧展示当前模块下的用例列表 | P0 |
| 用例详情 | 点击用例，右侧/弹窗展示完整 Markdown 内容（渲染态） | P0 |
| 全文搜索 | 在用例标题和内容中搜索关键词 | P0 |
| 多维过滤 | 按优先级、测试类型、状态、标签过滤 | P1 |
| 用例状态 | 展示 draft / approved / deprecated 状态标签 | P0 |
| 关联脚本 | 展示用例是否有对应脚本（绿色：有，灰色：无） | P1 |
| 关联 Bug | 展示用例关联的 Bug 数量和状态 | P1 |
| 批量操作 | 批量更改状态、批量加入测试计划 | P1 |

#### 用例列表字段

| 字段 | 说明 |
|------|------|
| 用例 ID | TC_001 格式 |
| 用例标题 | 来自 Front Matter `title` |
| 所属模块 | 来自 Front Matter `module` |
| 优先级 | P0-P3 标签 |
| 测试类型 | functional / boundary / exception 等 |
| 状态 | draft / approved / deprecated |
| 脚本状态 | 有脚本 / 无脚本 |
| 最后更新 | `updated_at` 字段 |
| 创建者 | `created_by` 字段 |

#### 验收标准

- [ ] 树形结构与 Git 工程 `tests/cases/` 目录结构完全一致
- [ ] 用例详情以 Markdown 渲染展示（表格、代码块正确渲染）
- [ ] 全文搜索响应时间 < 1s（1000 个用例以内）
- [ ] 用例状态实时反映 Markdown Front Matter 中的 `status` 字段

---

### 2.2 F2：用例评审（Case Review）

#### 功能描述

为 AI 生成的测试用例提供团队评审工作流。评审通过后，用例状态从 `draft` 变为 `approved`。

#### 评审流程

```
[CLI] qoder test generate → 生成 draft 用例
         ↓
[CLI] qoder sync --push → 用例同步到平台
         ↓
[平台] 测试用例管理 → 待评审列表
         ↓
[测试工程师/测试经理] 逐条审核：
  ├── 通过：状态 → approved
  ├── 修改后通过：在平台添加评审意见，通知编写者修改
  └── 拒绝：状态 → deprecated，记录原因
         ↓
[平台] 同步状态变更 → CLI 可通过 qoder sync pull 获取最新状态
```

#### 评审界面功能

| 功能点 | 描述 | 优先级 |
|--------|------|--------|
| 待评审列表 | 过滤 status=draft 的用例，按模块分组 | P0 |
| 用例详情展示 | 渲染 Markdown 内容，清晰展示步骤和预期 | P0 |
| 一键审批 | 通过 / 拒绝 按钮，支持批量操作 | P0 |
| 评审意见 | 添加文字评论，支持 @提及 | P1 |
| 评审历史 | 展示用例的评审历史记录 | P1 |

#### 验收标准

- [ ] draft 用例在评审通过后，平台自动更新对应 Markdown 文件的 Front Matter `status` 为 `approved`（通过 Git Commit 或 sync push）
- [ ] 评审人和评审时间记录在审计日志中
- [ ] 批量审批支持对当前模块下所有 draft 用例一次性操作

---

### 2.3 F3：测试计划（Test Plan）

#### 功能描述

从用例库中选取用例，组成测试计划，关联到特定版本/里程碑，并跟踪执行进度。

**注意**：此处的"测试计划"是平台概念（执行组织），区别于 CLI 生成的测试计划 Markdown（需求分析产物）。

#### 测试计划功能

| 功能点 | 描述 | 优先级 |
|--------|------|--------|
| 创建测试计划 | 设置计划名称、版本、开始/结束日期 | P0 |
| 关联用例 | 从用例库中选择用例加入计划（支持批量、按模块） | P0 |
| 执行进度跟踪 | 展示计划中用例的通过/失败/未执行比例 | P0 |
| 执行测试计划 | 一键触发计划中所有用例对应脚本的执行 | P0 |
| 测试报告 | 生成测试计划的汇总报告（通过率、缺陷数、执行耗时） | P0 |
| 计划归档 | 测试完成后归档计划，保留历史记录 | P1 |
| 基线对比 | 与上一个测试计划的结果对比（通过率变化、新增/消除 Bug） | P2 |

#### 测试计划数据结构

```
测试计划
├── 基本信息：名称、版本号、状态、负责人、时间范围
├── 用例集合：[用例 ID 列表]
├── 执行记录：[execution_id 列表]
└── 统计信息：用例总数、通过数、失败数、通过率
```

#### 验收标准

- [ ] 支持从用例库多选/按模块批量添加用例到测试计划
- [ ] 执行测试计划时，自动解析每个用例关联的脚本路径并提交执行
- [ ] 测试计划报告包含：通过率、执行时间、失败用例列表、关联 Bug 列表

---

### 2.4 F4：用例同步机制

#### 功能描述

保持平台用例索引与 Git 仓库文件内容的一致性。

#### 两种同步触发方式

**方式 A：CLI 主动推送**
```bash
qoder sync --push --types cases
# → 调用平台 /api/v1/sync/push 接口
# → 平台解析接收到的 Markdown 内容，更新数据库索引
```

**方式 B：Git Webhook（自动）**
```
Git Push → Webhook → 平台接收通知
→ 平台调用 Git API 拉取变更文件
→ 解析 Markdown Front Matter 更新索引
```

#### 同步数据模型

平台数据库中的用例表只存储索引和元数据：

```sql
CREATE TABLE test_cases (
    id          VARCHAR(20) PRIMARY KEY,  -- TC_001
    project_id  UUID NOT NULL,
    title       VARCHAR(500),
    module      VARCHAR(200),
    priority    VARCHAR(5),               -- P0/P1/P2/P3
    type        VARCHAR(50),
    status      VARCHAR(20),             -- draft/approved/deprecated
    tags        JSON,
    script_path VARCHAR(500),            -- 关联脚本的相对路径
    file_path   VARCHAR(500),            -- Git 仓库中的文件路径
    created_by  VARCHAR(100),
    created_at  TIMESTAMPTZ,
    updated_at  TIMESTAMPTZ,
    content_hash VARCHAR(64)             -- 文件内容 MD5，用于变更检测
);
```

#### 验收标准

- [ ] CLI push 后，平台在 5s 内完成索引更新
- [ ] Git Webhook 触发的自动同步延迟 < 30s
- [ ] 文件删除时，平台对应记录标记为 deprecated（不删除，保留历史）

---

## 3. 输入输出定义

### 3.1 输入

| 输入 | 来源 | 格式 |
|------|------|------|
| 用例 Markdown 文件 | Git 仓库 / CLI push | `.md` with Front Matter |
| 同步请求 | CLI `qoder sync push` | HTTP POST JSON |
| Git Webhook 事件 | Git 服务器 | JSON |

### 3.2 输出

| 输出 | 目标 | 格式 |
|------|------|------|
| 用例列表页面 | 测试工程师 | Web UI |
| 测试计划报告 | 测试经理/项目经理 | Web UI + 可导出 Markdown |
| 状态变更同步 | CLI（通过 sync pull） | JSON |

---

## 4. 与其他模块的接口规范

### 4.1 平台 REST API

```
# 用例同步接口（供 CLI 调用）
POST /api/v1/projects/{project_id}/cases/sync
Body: {
  "cases": [
    {
      "id": "TC_001",
      "file_path": "tests/cases/login/TC_001_valid_login.md",
      "content": "...(Markdown 全文)...",
      "updated_at": "2026-04-12T10:00:00Z"
    }
  ]
}

# 用例列表查询
GET /api/v1/projects/{project_id}/cases
  ?module=用户认证/登录
  &status=approved
  &priority=P0
  &page=1&page_size=20

# 测试计划创建
POST /api/v1/projects/{project_id}/test-plans
Body: {
  "name": "V1.0 回归测试",
  "version": "1.0",
  "case_ids": ["TC_001", "TC_002"]
}

# 触发测试计划执行
POST /api/v1/test-plans/{plan_id}/execute
Body: { "env": "staging", "parallel": 4 }
```

---

## 5. 技术实现要点

### 5.1 Markdown 解析

使用 `python-frontmatter` 解析用例元数据，`markdown-it-py` 渲染展示内容：

```python
import frontmatter
from mdit_py_plugins.tasklists import tasklists_plugin

def parse_test_case(markdown_content: str) -> dict:
    post = frontmatter.loads(markdown_content)
    return {
        "id": post.metadata.get("id"),
        "title": post.metadata.get("title"),
        "module": post.metadata.get("module"),
        "priority": post.metadata.get("priority"),
        "status": post.metadata.get("status", "draft"),
        "script_path": post.metadata.get("script"),
        "content": post.content,
        "content_hash": hashlib.md5(markdown_content.encode()).hexdigest()
    }
```

### 5.2 树形模块结构构建

从文件路径反推模块树：

```python
def build_module_tree(cases: list[TestCase]) -> dict:
    """从用例的 module 字段构建树形结构"""
    tree = {}
    for case in cases:
        parts = case.module.split("/")
        node = tree
        for part in parts:
            node = node.setdefault(part, {"_cases": [], "_children": {}})["_children"]
    return tree
```

---

## 6. 验收标准汇总

| 编号 | 验收标准 | 优先级 |
|------|---------|--------|
| AC-01 | 用例库树形结构与 Git 仓库目录结构一致 | P0 |
| AC-02 | 用例 Markdown 内容在平台正确渲染（表格、代码块）| P0 |
| AC-03 | 支持按优先级、类型、状态多维过滤 | P1 |
| AC-04 | 评审通过后，用例状态同步更新（Markdown + 平台数据库）| P0 |
| AC-05 | 测试计划支持关联用例、触发执行、查看汇总报告 | P0 |
| AC-06 | CLI push 后平台 5s 内完成索引更新 | P1 |
| AC-07 | 用例删除后平台标记为 deprecated，不丢失历史 | P1 |
