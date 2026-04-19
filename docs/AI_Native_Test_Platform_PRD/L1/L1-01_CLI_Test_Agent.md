# L1-01：Qoder CLI Test Agent 需求文档

## 文档信息

| 项目 | 内容 |
|------|------|
| 模块名称 | Qoder CLI Test Agent |
| 模块编号 | M1 |
| 文档版本 | L1 v1.0 |
| 上级文档 | [L0_PRD.md](../L0_PRD.md) |

---

## 1. 模块概述

### 1.1 模块定位

Qoder CLI Test Agent 是整个平台的核心 AI 生产力层。它是一个运行在测试工程师本地的命令行工具，集成 LangGraph 多节点工作流，以**意图驱动**的方式完成测试资产的生成、执行触发和结果分析。

**核心特征**：
- 测试工程师描述意图，Agent 自主完成多步骤任务
- 所有产出物是普通文件（Markdown + Python），人工可完整编辑
- 离线可工作，可选通过 API Key 异步同步到平台
- 减少对工程师工作习惯的改变（终端 + 自然语言）

### 1.2 与相关模块的关系

| 交互方向 | 交互对象 | 交互内容 |
|---------|---------|---------|
| CLI → 文件系统 | Git 工程本地文件 | 读取需求 .md，写入用例/脚本/Bug |
| CLI → 执行引擎（M5） | 本地执行进程 | 触发执行，读取实时输出 |
| CLI → 知识库（M7） | Qdrant 本地服务 | 查询相关知识片段 |
| CLI → 平台 API | 平台后端（M8） | 异步同步资产（可选） |

---

## 2. 功能详细描述

### 2.1 子命令总览

```
qoder
├── auth          # 认证管理
│   ├── login     # 登录平台，获取 API Key
│   └── logout    # 退出登录
├── config        # 项目配置
│   ├── init      # 初始化 Qoder 配置（.qoder/config.toml）
│   ├── show      # 查看当前配置
│   └── set       # 修改配置项
├── test          # 测试资产生成与执行（核心命令组）
│   ├── plan      # 生成测试计划
│   ├── generate  # 生成测试用例
│   ├── script    # 生成测试脚本
│   ├── run       # 执行测试
│   ├── analyze   # 分析执行结果
│   └── heal      # 自动修复失败脚本（V2.0）
├── bug           # Bug 管理
│   ├── list      # 列出 Bug
│   ├── show      # 查看 Bug 详情
│   ├── close     # 关闭 Bug
│   └── reopen    # 重新打开 Bug
├── kb            # 知识库管理
│   ├── index     # 重建知识库索引
│   └── search    # 搜索知识库
└── sync          # 与平台同步
    ├── push      # 推送本地资产到平台
    └── pull      # 从平台拉取最新状态
```

### 2.2 F1：`qoder config init` —— 项目初始化

#### 功能描述

在测试工程根目录初始化 Qoder 配置，生成 `.qoder/config.toml` 文件和标准目录结构。

#### 交互流程

```
$ qoder config init

? 项目名称：My Project
? LLM 供应商：[OpenAI / Azure / Ollama / 通义千问]
? API Key（留空则从环境变量读取）：
? 平台地址（留空则跳过平台同步）：https://test-platform.example.com
? 测试框架：[UI自动化(Playwright) / API测试(Pytest+httpx) / 两者]

✓ 已创建 .qoder/config.toml
✓ 已创建目录结构：
  tests/plans/  tests/cases/  tests/scripts/
  tests/bugs/   tests/reports/ tests/data/
✓ 已创建 .env.test.example
✓ 已创建 tests/conftest.py

完成！运行 `qoder test plan --help` 开始生成测试。
```

#### 输出文件

```toml
# .qoder/config.toml
[project]
name = "My Project"
platform_url = "https://test-platform.example.com"

[llm]
provider = "openai"
model = "gpt-4o"
# api_key 从环境变量 OPENAI_API_KEY 读取

[test]
case_dir = "tests/cases"
script_dir = "tests/scripts"
plan_dir = "tests/plans"
bug_dir = "tests/bugs"
report_dir = "tests/reports"
default_framework = "playwright"  # or "pytest"

[knowledge]
enabled = true
source_dirs = ["requirements", "docs", "tests/cases"]
```

#### 验收标准

- [ ] 执行后生成标准目录结构
- [ ] `config.toml` 格式正确，必填项不为空
- [ ] `.env.test.example` 包含所有必要的环境变量模板
- [ ] 重复执行时提示确认，不覆盖已有内容

---

### 2.3 F2：`qoder test plan` —— 生成测试计划

#### 功能描述

分析输入的需求文档或自然语言描述，由 AI 生成结构化的测试计划 Markdown 文件。测试计划是后续用例生成的输入，工程师应在生成后审核并调整。

#### 命令语法

```bash
qoder test plan [OPTIONS]

Options:
  --from PATH      输入文件路径（.md / .pdf / swagger.yaml）[必填]
  --output PATH    输出路径（默认：tests/plans/<name>_plan.md）
  --type TEXT      测试类型：ui / api / both（默认：自动判断）
  --scope TEXT     测试范围描述（补充说明）
  --with-kb        是否使用知识库增强（默认：true）
  --no-interactive 非交互模式，跳过确认步骤
```

#### LangGraph 工作流

```
[Node 1: 文档解析]
读取输入文件 → 提取结构化内容（功能点、接口、流程）

[Node 2: 知识库检索]（如启用）
查询相关历史用例和业务背景 → 注入上下文

[Node 3: 测试计划生成]
LLM 生成测试计划草稿（含模块划分、用例分类、优先级建议）

[Node 4: 人工审核节点]（交互模式）
展示计划摘要 → 工程师确认或修改 → 写入文件
```

#### 输出示例

```markdown
---
source: requirements/login.md
generated_at: 2026-04-12
generator: qoder-cli v1.0
status: draft  # 工程师审核后改为 approved
---

# 用户登录模块 测试计划

## 测试范围
- 登录功能（用户名密码认证）
- 会话管理（Token 有效期）
- 异常处理（错误提示、账号锁定）

## 测试模块划分

### 1. 正常登录流程（Priority: P0）
- 有效用户名和密码登录成功
- 记住登录状态（Remember Me）

### 2. 登录异常场景（Priority: P1）
- 错误密码登录失败
- 不存在的用户名
- 密码连续错误 5 次账号锁定
- 空用户名/密码提交

### 3. 安全性测试（Priority: P2）
- SQL 注入尝试
- XSS 尝试

## 预计用例数量：8-12 个
## 建议测试类型：UI 自动化（登录页面交互） + API 测试（接口层）
```

#### 验收标准

- [ ] 支持 `.md`、`.pdf`、`swagger.yaml` 三种输入格式
- [ ] 生成的计划包含模块划分、优先级分类、预计用例数量
- [ ] 启用知识库时，相关历史知识被正确引用
- [ ] 交互模式下，工程师确认前不写入文件
- [ ] 生成时间 < 60s（20 个场景以内）

---

### 2.4 F3：`qoder test generate` —— 生成测试用例

#### 功能描述

读取测试计划 Markdown 文件，逐条生成符合规范的测试用例 Markdown 文件（1 个用例 = 1 个文件）。

#### 命令语法

```bash
qoder test generate [OPTIONS]

Options:
  --from PATH       输入测试计划文件（.md）[必填]
  --output-dir PATH 用例输出目录（默认：tests/cases/<module>/）
  --types TEXT      测试类型过滤（smoke/functional/boundary/exception/security）
  --priority TEXT   优先级过滤（P0/P1/P2/P3）
  --count INT       最大生成数量（默认：计划中全部）
  --with-kb         使用知识库增强（默认：true）
  --no-interactive  非交互模式
```

#### LangGraph 工作流

```
[Node 1: 计划解析]
读取测试计划 → 提取所有待生成的测试场景列表

[Node 2: 批量用例生成]
对每个场景：
  ├── 知识库检索相关用例模板
  ├── LLM 生成单个用例（步骤 + 预期结果 + 输入数据）
  └── 写入 Markdown 文件（TC_XXX_<slug>.md）

[Node 3: 批量审核节点]（交互模式）
展示生成的用例列表和摘要
工程师选择：全部保留 / 逐个审核 / 删除指定
```

#### 测试用例 Markdown 格式（完整规范）

```markdown
---
id: TC_001
title: 有效用户名和密码登录成功
module: 用户认证/登录
priority: P0
type: functional
created_by: qoder-cli
created_at: 2026-04-12
updated_at: 2026-04-12
script: ../../scripts/login/TC_001_valid_login.py
tags: [login, smoke, p0]
status: draft  # draft | approved | deprecated
---

# TC_001：有效用户名和密码登录成功

## 前提条件

- 用户 `test@example.com` 已注册，状态为激活
- 服务正常运行，登录页面可访问

## 测试步骤

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 打开登录页面 `/login` | 页面正常显示，包含用户名、密码输入框和登录按钮 |
| 2 | 在用户名输入框输入 `test@example.com` | 输入框显示输入内容 |
| 3 | 在密码输入框输入 `Password123` | 密码以掩码形式（●）显示 |
| 4 | 点击"登录"按钮 | 按钮进入 loading 状态，发起登录请求 |
| 5 | 等待页面响应（最多 5s）| 页面跳转至 `/dashboard` |
| 6 | 检查欢迎消息 | 页面顶部显示"欢迎，test" |

## 输入数据

| 字段 | 值 |
|------|-----|
| 用户名 | `test@example.com` |
| 密码 | `Password123` |

## 备注

此用例为冒烟测试必执行用例。
```

#### ID 命名规范

- 格式：`TC_<三位数字>_<slug>`
- 例：`TC_001_valid_login`、`TC_002_invalid_password`
- 同模块下序号连续，跨模块重新起编

#### 验收标准

- [ ] 每个场景生成独立的 Markdown 文件
- [ ] 文件 Front Matter 中的 `script` 字段自动指向对应脚本路径（脚本未生成时留空）
- [ ] 测试步骤表格格式正确，包含操作和预期结果两列
- [ ] 支持批量生成后的交互审核（全选/逐个/删除）
- [ ] 生成 20 个用例的时间 < 90s

---

### 2.5 F4：`qoder test script` —— 生成测试脚本

#### 功能描述

读取测试用例 Markdown 文件，生成对应的 Python 测试脚本（Playwright 或 Pytest）。脚本与用例 1:1 对应。

#### 命令语法

```bash
qoder test script [OPTIONS]

Options:
  --cases PATH      输入用例目录或单个用例文件（.md）[必填]
  --output-dir PATH 脚本输出目录（默认：tests/scripts/<module>/）
  --framework TEXT  脚本框架：playwright / pytest（默认：从 config 读取）
  --env TEXT        目标环境（用于生成环境变量引用）
  --no-interactive  非交互模式
```

#### LangGraph 工作流

```
[Node 1: 用例读取]
读取用例 Markdown 文件 → 解析步骤、预期结果、输入数据

[Node 2: 框架选择]
根据用例类型和配置，选择 Playwright 或 Pytest 框架

[Node 3: 脚本生成]
LLM 参考：
  ├── 用例步骤（直接映射到代码步骤）
  ├── 测试数据（内嵌在脚本中）
  ├── 框架最佳实践（Page Object 模式等）
  └── conftest.py 中的 fixture 定义
生成 Python 测试脚本

[Node 4: 验证节点]
尝试 dry-run 验证脚本语法（不执行，只检查语法）
有语法错误则自动修复后重试（最多 3 次）

[Node 5: 更新用例文件]
将脚本路径回写到用例 Markdown 的 Front Matter `script` 字段
```

#### UI 自动化脚本示例（Playwright Python）

```python
"""
Test Case: TC_001 - 有效用户名和密码登录成功
Generated by: qoder-cli v1.0
Generated at: 2026-04-12
Case file: ../../cases/login/TC_001_valid_login.md
"""
import pytest
from playwright.sync_api import Page, expect
import os


# ---- 测试数据 ----
TEST_USER = "test@example.com"
TEST_PASSWORD = "Password123"
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:3000")


def test_TC_001_valid_login(page: Page):
    """有效用户名和密码登录成功"""
    # 步骤 1：打开登录页面 /login
    page.goto(f"{BASE_URL}/login")
    expect(page.get_by_role("textbox", name="用户名")).to_be_visible()
    expect(page.get_by_role("textbox", name="密码")).to_be_visible()
    expect(page.get_by_role("button", name="登录")).to_be_visible()

    # 步骤 2：输入用户名
    page.get_by_role("textbox", name="用户名").fill(TEST_USER)

    # 步骤 3：输入密码
    page.get_by_role("textbox", name="密码").fill(TEST_PASSWORD)

    # 步骤 4：点击登录按钮
    page.get_by_role("button", name="登录").click()

    # 步骤 5：等待页面跳转
    page.wait_for_url(f"{BASE_URL}/dashboard", timeout=5000)

    # 步骤 6：验证欢迎消息
    expect(page.get_by_text("欢迎，test")).to_be_visible()
```

#### API 测试脚本示例（Pytest + httpx）

```python
"""
Test Case: TC_010 - POST /api/auth/login 正确凭证返回 Token
Generated by: qoder-cli v1.0
Generated at: 2026-04-12
Case file: ../../cases/api/TC_010_api_login_success.md
"""
import pytest
import httpx
import os

BASE_URL = os.getenv("TEST_API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("TEST_API_KEY", "")


def test_TC_010_api_login_success():
    """POST /api/auth/login 正确凭证返回 Token"""
    # 步骤 1：发送登录请求
    response = httpx.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "Password123"
        }
    )

    # 步骤 2：验证响应状态码
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. Body: {response.text}"

    # 步骤 3：验证响应体包含 token
    body = response.json()
    assert "token" in body, f"Response missing 'token' field: {body}"
    assert len(body["token"]) > 0, "Token is empty"

    # 步骤 4：验证 token 类型
    assert "token_type" in body
    assert body["token_type"].lower() == "bearer"
```

#### 验收标准

- [ ] 生成的脚本可以直接被 Pytest 执行（无语法错误）
- [ ] 测试数据内嵌在脚本中（不依赖外部文件）
- [ ] UI 脚本使用 `get_by_role` / `get_by_label` 等语义化选择器，避免 CSS 选择器
- [ ] 环境变量（URL、密码等）通过 `os.getenv` 读取
- [ ] 脚本头部注释包含用例 ID、标题、生成时间、关联用例文件路径
- [ ] 生成后自动更新用例 Markdown 的 `script` 字段
- [ ] 脚本生成 20 个的时间 < 90s

---

### 2.6 F5：`qoder test run` —— 执行测试

#### 功能描述

触发执行引擎执行指定的测试脚本，实时展示执行状态，等待完成后输出摘要。

#### 命令语法

```bash
qoder test run [OPTIONS]

Options:
  --suite PATH      测试套件目录（执行目录下所有 .py 文件）
  --case PATH       单个测试脚本文件
  --bug PATH        关联 Bug 的 Markdown 文件（执行关联脚本）
  --env TEXT        环境名称（dev/staging/prod，读取对应 .env 文件）
  --parallel INT    并行执行数量（默认：4）
  --browser TEXT    浏览器类型（chromium/firefox/webkit，UI 测试用）
  --report-dir PATH 报告输出目录（默认：tests/reports/run_<timestamp>/）
  --no-interactive  非交互模式（CI/CD 用）
```

#### 执行流程

```
1. 收集执行目标（脚本文件列表）
2. 读取环境变量（.env.<env> 文件）
3. 调用执行引擎 API（本地 HTTP 或进程调用）
4. 实时展示执行进度（Rich 进度条）：
   ┌──────────────────────────────────────────────┐
   │ 执行进度：12/20  ████████████░░░░░░  60%     │
   │ ✓ TC_001_valid_login          0.8s           │
   │ ✓ TC_002_invalid_password     1.2s           │
   │ ✗ TC_003_locked_account       2.1s  FAILED   │
   │ ⟳ TC_004_remember_me          running...     │
   └──────────────────────────────────────────────┘
5. 执行完成，输出摘要：
   总计：20  通过：18  失败：2  跳过：0
   耗时：45.3s  报告：tests/reports/run_20260412_001/
6. 写入执行记录到 tests/reports/run_<timestamp>/summary.md
```

#### 终端输出格式

```
$ qoder test run --suite tests/scripts/login/ --env staging

🚀 开始执行测试套件：tests/scripts/login/ (环境：staging)
   共 8 个脚本，并行数：4，浏览器：chromium

✓ TC_001_valid_login              0.8s  PASSED
✓ TC_002_invalid_password         1.2s  PASSED
✗ TC_003_locked_account           2.1s  FAILED
  └── AssertionError: 页面未显示"账号已锁定"提示
✓ TC_004_remember_me              3.5s  PASSED
✓ TC_005_empty_username           0.9s  PASSED
✓ TC_006_empty_password           1.0s  PASSED
✗ TC_007_sql_injection            1.8s  FAILED
  └── Expected status 400, got 500
✓ TC_008_xss_attempt              2.2s  PASSED

─────────────────────────────────────────
总计：8 │ 通过：6 │ 失败：2 │ 跳过：0
耗时：12.4s（并行）

报告已保存：tests/reports/run_20260412_001/
运行 `qoder test analyze` 分析失败原因。
```

#### 验收标准

- [ ] 支持目录（批量）和单文件执行
- [ ] 实时展示每个脚本的执行状态（Rich 输出）
- [ ] `--bug` 参数可自动解析 Bug Markdown 中的关联脚本并执行
- [ ] 执行报告自动写入 `tests/reports/run_<timestamp>/` 目录
- [ ] 非交互模式（`--no-interactive`）下，退出码反映执行结果（0=全通过，1=有失败）

---

### 2.7 F6：`qoder test analyze` —— 分析执行结果

#### 功能描述

读取执行报告，AI 分析失败原因，自动创建 Bug Markdown 文件，并提供修复建议。

#### 命令语法

```bash
qoder test analyze [OPTIONS]

Options:
  --report PATH   执行报告目录（默认：最新一次执行报告）
  --auto-bug      自动为所有失败创建 Bug 文件（默认：交互确认）
  --no-interactive 非交互模式（CI/CD 用，自动创建 Bug）
```

#### LangGraph 工作流

```
[Node 1: 报告读取]
读取 summary.md、各脚本日志、截图列表

[Node 2: 失败分类]（针对每个失败）
  ├── 分析错误类型（选择器失效 / 断言失败 / 超时 / 环境问题）
  └── 提取关键错误信息

[Node 3: Bug 生成]（针对每个失败）
  ├── 读取关联的测试用例 Markdown（还原复现步骤）
  ├── 关联截图（UI 测试）或请求日志（API 测试）
  ├── LLM 撰写 Bug 描述和 AI 分析
  └── 写入 tests/bugs/BUG_<id>_<slug>.md

[Node 4: 汇总报告]
生成分析摘要，更新 summary.md 的分析部分

[Node 5: 确认节点]（交互模式）
展示将要创建的 Bug 列表 → 工程师确认
```

#### 分析输出示例

```
$ qoder test analyze

🔍 分析执行报告：tests/reports/run_20260412_001/

分析中... ████████████████████ 100%

─────────────────────────────────────
执行摘要：8 个测试，6 通过，2 失败
─────────────────────────────────────

[失败 1] TC_003_locked_account
  错误类型：断言失败（UI 元素未找到）
  根因分析：页面上未显示"账号已锁定"提示文本，
           实际显示为"用户名或密码错误"，
           可能是连续失败次数计数未触发锁定逻辑。
  建议修复：检查用户服务中的账号锁定逻辑，
           确认连续失败阈值配置是否正确。

[失败 2] TC_007_sql_injection
  错误类型：HTTP 状态码断言失败
  根因分析：期望返回 400（拒绝非法输入），
           实际返回 500（服务端未捕获异常），
           属于安全漏洞，SQL 注入未被正确处理。
  建议修复：检查登录接口的输入验证逻辑，
           添加参数化查询或输入净化。

─────────────────────────────────────
? 是否为以上 2 个失败创建 Bug 报告？[Y/n] Y

✓ 已创建 tests/bugs/BUG_001_locked_account.md
✓ 已创建 tests/bugs/BUG_002_sql_injection_500.md

提示：运行 `qoder sync --push` 将 Bug 同步到平台。
```

#### 验收标准

- [ ] 能正确识别常见失败类型（元素未找到、断言失败、超时、HTTP 错误）
- [ ] AI 分析包含根因推断和修复建议
- [ ] 自动创建的 Bug Markdown 包含截图引用（UI 测试）或请求/响应文本（API 测试）
- [ ] 非交互模式下，默认自动创建所有 Bug
- [ ] Bug ID 自动递增，不与已有 Bug 重复

---

### 2.8 F7：`qoder sync` —— 与平台同步

#### 功能描述

将本地生成的测试资产（用例、脚本、执行记录、Bug）推送到平台，或从平台拉取最新的状态变更（Bug 状态等）。

#### 命令语法

```bash
qoder sync push [OPTIONS]   # 推送本地 → 平台
qoder sync pull [OPTIONS]   # 拉取平台 → 本地

Options:
  --types TEXT   同步类型：cases/scripts/bugs/reports/all（默认：all）
  --project TEXT 目标项目（默认：从 config 读取）
  --dry-run      预览同步内容，不实际执行
```

#### 同步规则

- **Push 策略**：本地文件为准，平台侧合并更新（基于文件 ID 和 `updated_at`）
- **Pull 策略**：平台侧状态（Bug 状态、指派人）覆盖本地 Markdown Front Matter
- **冲突处理**：若本地和平台的内容都有修改，提示工程师手动解决

#### 验收标准

- [ ] `--dry-run` 输出将要同步的文件列表，不执行实际同步
- [ ] 同步失败时，给出清晰的错误提示（网络问题 / 认证失败 / 冲突）
- [ ] 支持断点续传（大批量同步中断后可继续）
- [ ] 同步完成后输出统计（新增 X，更新 X，跳过 X）

---

## 3. 输入输出定义

### 3.1 输入

| 输入类型 | 格式 | 说明 |
|---------|------|------|
| 需求文档 | `.md` / `.pdf` | 产品需求文档，作为测试计划生成的输入 |
| OpenAPI Spec | `.yaml` / `.json` | API 定义文件，用于 API 测试计划生成 |
| 测试计划 | `.md` | AI 生成或人工编写的测试计划 |
| 测试用例 | `.md` | 用于脚本生成的输入 |
| 执行报告目录 | 目录 | 包含 `summary.md` 和日志文件 |
| Bug Markdown | `.md` | 用于关联脚本执行验证 |
| 环境变量文件 | `.env.*` | 测试环境配置 |

### 3.2 输出

| 输出类型 | 格式 | 存储位置 |
|---------|------|---------|
| 测试计划 | `.md` | `tests/plans/` |
| 测试用例 | `.md` | `tests/cases/<module>/` |
| 测试脚本 | `.py` | `tests/scripts/<module>/` |
| 执行报告 | 目录（含 `.md`、截图、日志） | `tests/reports/run_<timestamp>/` |
| Bug 报告 | `.md` | `tests/bugs/` |

---

## 4. 与其他模块的接口规范

### 4.1 与执行引擎（M5）的接口

CLI 通过以下方式与执行引擎交互：

**方式 A：本地进程调用（V1.0 MVP）**
```python
# CLI 内部直接调用 pytest
import subprocess
result = subprocess.run(
    ["pytest", script_path, "--json-report", "--json-report-file=report.json"],
    capture_output=True, text=True
)
```

**方式 B：HTTP API 调用（V1.5+）**
```
POST http://localhost:8888/api/execute
{
  "scripts": ["tests/scripts/login/TC_001.py"],
  "env": "staging",
  "parallel": 4,
  "browser": "chromium"
}
→ 返回 execution_id
GET http://localhost:8888/api/execute/{execution_id}/status
→ WebSocket: ws://localhost:8888/ws/execute/{execution_id}
```

### 4.2 与知识库（M7）的接口

```python
# CLI 内部调用 Qdrant 本地服务
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)
results = client.search(
    collection_name="project_knowledge",
    query_vector=embed(query_text),
    limit=5
)
```

### 4.3 与平台（M8）的接口

```
# 同步接口
POST {platform_url}/api/v1/sync/push
Headers: Authorization: Bearer {api_key}
Body: {
  "project_id": "xxx",
  "resources": [
    {"type": "test_case", "id": "TC_001", "content": "...", "updated_at": "..."},
    {"type": "bug", "id": "BUG_001", "content": "...", "updated_at": "..."}
  ]
}
```

---

## 5. 技术实现要点

### 5.1 LangGraph 工作流设计

每个主要命令对应一个 LangGraph Graph：

```python
from langgraph.graph import StateGraph

# 以 test generate 为例
class CaseGenerationState(TypedDict):
    plan_content: str          # 输入的测试计划内容
    kb_context: str            # 知识库检索结果
    generated_cases: list      # 已生成的用例列表
    current_scene: int         # 当前处理的场景索引
    approved_cases: list       # 工程师审核后保留的用例

graph = StateGraph(CaseGenerationState)
graph.add_node("parse_plan", parse_plan_node)
graph.add_node("search_kb", search_kb_node)
graph.add_node("generate_case", generate_case_node)
graph.add_node("human_review", human_review_node)
graph.add_node("write_files", write_files_node)

graph.add_edge("parse_plan", "search_kb")
graph.add_edge("search_kb", "generate_case")
graph.add_conditional_edges("generate_case", route_to_review_or_next)
graph.add_edge("human_review", "write_files")
```

### 5.2 Markdown Front Matter 解析

使用 `python-frontmatter` 库读写 YAML Front Matter：

```python
import frontmatter

# 读取
post = frontmatter.load("tests/cases/login/TC_001.md")
case_id = post.metadata["id"]
script_path = post.metadata["script"]

# 更新
post.metadata["script"] = "../../scripts/login/TC_001_valid_login.py"
post.metadata["updated_at"] = "2026-04-12"
frontmatter.dump(post, "tests/cases/login/TC_001.md")
```

### 5.3 LLM Provider 抽象

支持多 LLM 供应商，通过 LangChain 抽象：

```python
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama

def get_llm(config):
    if config.provider == "openai":
        return ChatOpenAI(model=config.model, api_key=config.api_key)
    elif config.provider == "ollama":
        return Ollama(model=config.model, base_url=config.base_url)
    elif config.provider == "qwen":
        return ChatOpenAI(
            model=config.model,
            api_key=config.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
```

### 5.4 Bug ID 自动递增

```python
import glob, re

def next_bug_id(bug_dir: str) -> str:
    """扫描 bug_dir，找到最大 ID，返回下一个"""
    existing = glob.glob(f"{bug_dir}/BUG_*.md")
    ids = [int(re.search(r'BUG_(\d+)', f).group(1)) for f in existing if re.search(r'BUG_(\d+)', f)]
    next_id = max(ids, default=0) + 1
    return f"BUG_{next_id:03d}"
```

---

## 6. 验收标准汇总

| 编号 | 验收标准 | 优先级 |
|------|---------|--------|
| AC-01 | `qoder config init` 完成后生成完整目录结构和配置文件 | P0 |
| AC-02 | `qoder test plan` 从 .md 输入生成结构化测试计划，< 60s | P0 |
| AC-03 | `qoder test generate` 生成符合格式规范的用例 Markdown，< 90s | P0 |
| AC-04 | `qoder test script` 生成可直接执行的 Python 脚本，无语法错误 | P0 |
| AC-05 | `qoder test run` 实时展示执行进度，执行结果写入报告目录 | P0 |
| AC-06 | `qoder test analyze` 对失败用例生成 Bug Markdown，含 AI 分析 | P0 |
| AC-07 | `qoder sync push` 将本地资产同步到平台，基于 API Key 认证 | P1 |
| AC-08 | 所有命令支持 `--no-interactive` 模式，可在 CI/CD 中使用 | P0 |
| AC-09 | 支持 OpenAI、Ollama、通义千问三种 LLM 供应商 | P1 |
| AC-10 | 离线模式下（无网络），生成和执行功能正常工作 | P1 |
