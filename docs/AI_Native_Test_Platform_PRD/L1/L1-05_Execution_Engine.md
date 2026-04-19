# L1-05：测试执行引擎需求文档

## 文档信息

| 项目 | 内容 |
|------|------|
| 模块名称 | 测试执行引擎 |
| 模块编号 | M5 |
| 文档版本 | L1 v1.0 |
| 上级文档 | [L0_PRD.md](../L0_PRD.md) |

---

## 1. 模块概述

### 1.1 模块定位

测试执行引擎是平台的运行时基础设施，负责在受控环境中**调度、执行、观测 Python 测试脚本**，并收集现场证据（截图、日志、请求记录）。

**核心设计原则**：
- 以 Python + Pytest 为核心执行器，不感知业务逻辑
- 执行过程对 AI（Qoder CLI）可观测：提供结构化日志、截图、实时状态
- 支持 WebSocket 实时推送执行状态，供平台 Web UI 实时展示
- 执行记录写入文件系统（测试现场），同时更新数据库索引

### 1.2 与相关模块的关系

| 交互方向 | 交互对象 | 交互内容 |
|---------|---------|---------|
| CLI（M1）→ 引擎 | Qoder CLI | 触发执行请求 |
| 平台（M8）→ 引擎 | 测试计划执行 | 通过平台 API 触发 |
| 引擎 → CLI（M1） | 执行结果 | 结构化执行报告供 Analyzer 分析 |
| 引擎 → 平台（M8） | WebSocket | 实时执行状态推送 |
| 引擎 → 文件系统 | Git 工程 | 写入截图、日志、报告 Markdown |
| 引擎 → Bug 管理（M6）| 触发 | 通知有失败，待 Analyzer 处理 |

---

## 2. 功能详细描述

### 2.1 F1：任务调度

#### 功能描述

接收执行请求，管理执行队列，支持并行执行多个脚本。

#### 执行请求格式

```python
class ExecutionRequest:
    scripts: list[str]       # 脚本路径列表
    env: str                 # 环境名称（dev/staging/prod）
    parallel: int = 4        # 并行数
    browser: str = "chromium"# UI 测试浏览器
    timeout: int = 300       # 单脚本超时（秒）
    report_dir: str          # 报告输出目录
    tags: list[str] = []     # 执行标签（用于过滤）
```

#### 调度逻辑

```
接收执行请求
    │
    ├── 验证脚本路径合法性
    ├── 读取环境变量（.env.<env> 文件）
    ├── 创建执行记录（DB：status=pending）
    │
    └── 提交到执行队列（Celery Task）
         │
         ├── 按 parallel 参数，创建 N 个并行 Worker
         │   每个 Worker 依次从队列取脚本执行
         └── 所有脚本完成后，汇总结果
```

#### 验收标准

- [ ] 支持最多 8 个脚本并行执行（单机）
- [ ] 执行队列满时，新请求进入等待队列（不丢失）
- [ ] 单脚本执行超时时，自动终止并标记为 TIMEOUT

---

### 2.2 F2：脚本执行

#### 功能描述

在隔离的子进程中执行单个 Python 测试脚本，收集执行结果。

#### 执行过程

```python
# 执行单个脚本的核心逻辑
import subprocess, json, os

def execute_script(script_path: str, env_vars: dict, config: RunConfig) -> ScriptResult:
    """在子进程中执行单个 Pytest 脚本"""
    
    # 构建环境变量
    env = {**os.environ, **env_vars}
    
    # 构建 Pytest 命令
    cmd = [
        "python", "-m", "pytest",
        script_path,
        "--json-report",                    # 结构化 JSON 报告
        f"--json-report-file={report_path}",
        "--tb=short",                       # 简短的错误堆栈
        f"--timeout={config.timeout}",      # 超时控制
        "-v",                               # 详细输出
    ]
    
    # Playwright 相关参数（UI 测试）
    if config.browser:
        env["PLAYWRIGHT_BROWSER"] = config.browser
    
    # 执行
    result = subprocess.run(
        cmd, env=env,
        capture_output=True, text=True,
        timeout=config.timeout + 30
    )
    
    return parse_result(result, report_path)
```

#### Pytest 配置（conftest.py 模板）

```python
# tests/conftest.py（由 qoder config init 生成）
import pytest
from playwright.sync_api import sync_playwright
import os

@pytest.fixture(scope="session")
def browser_context():
    """Playwright 浏览器上下文"""
    with sync_playwright() as p:
        browser_type = os.getenv("PLAYWRIGHT_BROWSER", "chromium")
        browser = getattr(p, browser_type).launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=None,  # 不录制视频（性能考虑）
        )
        yield context
        context.close()
        browser.close()

@pytest.fixture
def page(browser_context):
    """每个测试用例使用独立的 Page"""
    page = browser_context.new_page()
    yield page
    page.close()

# 自动截图（失败时）
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page")
        if page:
            screenshot_dir = os.getenv("QODER_SCREENSHOT_DIR", "tests/reports/screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = f"{screenshot_dir}/{item.name}_fail.png"
            page.screenshot(path=screenshot_path)
            # 将截图路径附加到报告
            rep.screenshot = screenshot_path
```

#### 验收标准

- [ ] 执行环境变量通过子进程环境传递，不修改全局环境
- [ ] UI 测试失败时自动截图，截图路径记录在执行报告中
- [ ] API 测试记录请求/响应文本（通过 httpx 的日志捕获）
- [ ] 执行结果包含：状态（PASSED/FAILED/ERROR/TIMEOUT）、耗时、错误信息、截图路径

---

### 2.3 F3：实时执行观测（WebSocket）

#### 功能描述

通过 WebSocket 实时推送执行状态，供平台 Web UI 实时展示进度。

#### WebSocket 消息格式

```typescript
// 事件类型
type ExecutionEvent =
  | { type: "execution_started"; execution_id: string; total: number }
  | { type: "script_started"; script: string; index: number }
  | { type: "script_completed"; script: string; status: "PASSED"|"FAILED"|"ERROR"|"TIMEOUT"; duration: number; error?: string }
  | { type: "execution_completed"; summary: ExecutionSummary }

// 示例消息序列
{ type: "execution_started", execution_id: "run_001", total: 8 }
{ type: "script_started", script: "TC_001_valid_login.py", index: 1 }
{ type: "script_completed", script: "TC_001_valid_login.py", status: "PASSED", duration: 0.8 }
{ type: "script_started", script: "TC_002_invalid_password.py", index: 2 }
{ type: "script_completed", script: "TC_002_invalid_password.py", status: "PASSED", duration: 1.2 }
{ type: "script_completed", script: "TC_003_locked_account.py", status: "FAILED", duration: 2.1,
  error: "AssertionError: Expected text '账号已锁定', not found on page" }
{ type: "execution_completed", summary: { total: 8, passed: 6, failed: 2, duration: 12.4 } }
```

#### WebSocket API

```
连接：ws://{platform}/ws/execution/{execution_id}
认证：查询参数 ?token={api_key}
```

#### 验收标准

- [ ] WebSocket 消息延迟 < 500ms（从脚本状态变更到客户端收到消息）
- [ ] 断线重连后，客户端可通过 HTTP API 获取当前执行状态快照
- [ ] Web UI 基于 WebSocket 消息实时更新执行进度条

---

### 2.4 F4：现场记录

#### 功能描述

在测试执行过程中，自动收集测试现场证据，写入报告目录。

#### 现场记录规则

| 测试类型 | 记录内容 | 存储格式 |
|---------|---------|---------|
| UI 自动化（Playwright）| 失败截图 | PNG 图片 |
| UI 自动化（Playwright）| 控制台日志（console.error）| 文本 |
| UI 自动化（Playwright）| 页面 URL 和标题 | 文本 |
| API 自动化（Pytest+httpx）| HTTP 请求（方法、URL、Headers、Body）| 文本 |
| API 自动化（Pytest+httpx）| HTTP 响应（状态码、Headers、Body）| 文本 |
| 通用 | Python 异常堆栈 | 文本 |
| 通用 | 测试用时、环境信息 | 文本 |

**注意**：UI 测试截图仅在失败时触发，不为每步操作截图（性能考虑）。

#### 执行报告目录结构

```
tests/reports/run_20260412_143022/
├── summary.md              # 执行摘要（人类可读 + AI 可分析）
├── summary.json            # 结构化执行数据（机器可读）
├── screenshots/            # UI 测试失败截图
│   ├── TC_003_locked_account_fail.png
│   └── TC_007_sql_injection_fail.png
└── logs/                   # 详细日志
    ├── TC_001_valid_login.log
    ├── TC_003_locked_account.log
    └── ...
```

#### summary.md 格式

```markdown
---
execution_id: run_20260412_143022
project: My Project
env: staging
started_at: 2026-04-12T14:30:22Z
completed_at: 2026-04-12T14:30:34Z
duration: 12.4s
total: 8
passed: 6
failed: 2
status: failed
---

# 执行摘要：2026-04-12 14:30

## 统计

| 指标 | 数值 |
|------|------|
| 总用例 | 8 |
| 通过 | 6 |
| 失败 | 2 |
| 通过率 | 75% |
| 总耗时 | 12.4s |
| 环境 | staging |

## 失败详情

### TC_003_locked_account — FAILED (2.1s)

**错误**：`AssertionError: Expected text '账号已锁定' not found`

**截图**：`screenshots/TC_003_locked_account_fail.png`

**日志摘要**：
```
FAILED tests/scripts/login/TC_003_locked_account.py::test_TC_003_locked_account
AssertionError: Expected page to contain text '账号已锁定'
  Actual page title: 登录
  Current URL: http://staging.example.com/login
```

### TC_007_sql_injection — FAILED (1.8s)

**错误**：`AssertionError: Expected status 400, got 500`

**请求**：
```
POST http://staging.example.com/api/auth/login
Content-Type: application/json
{"email": "' OR 1=1 --", "password": "test"}
```

**响应**：
```
HTTP/1.1 500 Internal Server Error
{"error": "Internal Server Error"}
```

## 通过用例

| 用例 | 耗时 |
|------|------|
| TC_001_valid_login | 0.8s |
| TC_002_invalid_password | 1.2s |
| ...（其余 4 个）| ... |
```

#### 验收标准

- [ ] 每次执行后自动生成 `summary.md` 和 `summary.json`
- [ ] UI 测试失败时截图自动保存，路径正确写入 summary.md
- [ ] API 测试失败时，请求/响应文本完整记录（包含 Headers 和 Body）
- [ ] 执行日志可通过 `tests/reports/run_xxx/logs/` 访问完整输出

---

### 2.5 F5：执行记录管理（平台侧）

#### 功能描述

平台存储所有执行记录的索引，支持历史查询和趋势分析。

#### 数据模型

```sql
CREATE TABLE execution_records (
    id          VARCHAR(50) PRIMARY KEY,   -- run_20260412_143022
    project_id  UUID NOT NULL,
    plan_id     UUID,                       -- 关联测试计划（可为空）
    env         VARCHAR(50),
    status      VARCHAR(20),               -- running/passed/failed/error
    total       INT,
    passed      INT,
    failed      INT,
    duration    FLOAT,                     -- 执行总耗时（秒）
    report_dir  VARCHAR(500),              -- 报告目录路径
    triggered_by VARCHAR(100),            -- cli/platform/ci
    started_at  TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ
);

CREATE TABLE script_results (
    id              UUID PRIMARY KEY,
    execution_id    VARCHAR(50) REFERENCES execution_records(id),
    case_id         VARCHAR(20),          -- TC_001
    script_path     VARCHAR(500),
    status          VARCHAR(20),          -- PASSED/FAILED/ERROR/TIMEOUT
    duration        FLOAT,
    error_message   TEXT,
    screenshot_path VARCHAR(500),         -- 截图相对路径
    log_path        VARCHAR(500),
    created_at      TIMESTAMPTZ
);
```

#### 验收标准

- [ ] 平台展示历史执行记录列表，支持按时间、环境、状态过滤
- [ ] 点击执行记录可查看 summary.md 渲染内容和截图
- [ ] 支持 30 天执行趋势图表（通过率变化曲线）

---

## 3. 与其他模块的接口规范

### 3.1 执行引擎 HTTP API

```
# 触发执行（CLI 或平台调用）
POST /api/v1/execute
Body: {
  "scripts": ["tests/scripts/login/TC_001.py"],
  "env": "staging",
  "parallel": 4,
  "browser": "chromium",
  "report_dir": "tests/reports/run_20260412_001"
}
Response: { "execution_id": "run_20260412_143022", "status": "queued" }

# 查询执行状态
GET /api/v1/execute/{execution_id}
Response: {
  "execution_id": "run_20260412_143022",
  "status": "running",
  "total": 8, "passed": 3, "failed": 1, "remaining": 4,
  "duration": 5.2
}

# WebSocket 实时事件
WS /ws/execute/{execution_id}
```

---

## 4. 验收标准汇总

| 编号 | 验收标准 | 优先级 |
|------|---------|--------|
| AC-01 | 支持 Playwright Python 和 Pytest+httpx 两种脚本框架 | P0 |
| AC-02 | 支持最多 8 个脚本并行执行 | P0 |
| AC-03 | UI 测试失败时自动截图，截图路径写入报告 | P0 |
| AC-04 | API 测试记录完整的请求/响应文本 | P0 |
| AC-05 | 每次执行后生成 summary.md 和 summary.json | P0 |
| AC-06 | WebSocket 消息延迟 < 500ms | P1 |
| AC-07 | 单脚本超时自动终止，标记为 TIMEOUT | P0 |
| AC-08 | 执行历史在平台中可查询，支持 30 天趋势图 | P1 |
