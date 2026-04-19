# AI Native 质量管理平台产品需求文档 (PRD)

## 文档信息

| 属性 | 值 |
|------|-----|
| **文档名称** | AI Native 质量管理平台产品需求文档 |
| **版本号** | V1.2（职责分离重构版） |
| **创建日期** | 2026-04-19 |
| **修订日期** | 2026-04-19 |
| **文档状态** | 职责分离重构完成 |
| **产品经理** | QualityAI 产品团队 |
| **技术负责人** | QualityAI 技术团队 |

## 文档审批

| 角色 | 姓名 | 签字 | 日期 |
|------|------|------|------|
| 产品总监 | | | |
| 技术总监 | | | |
| 业务负责人 | | | |

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [产品愿景与定位](#2-产品愿景与定位)
3. [目标用户与使用场景](#3-目标用户与使用场景)
4. [工程中心化架构设计](#4-工程中心化架构设计)
5. [产品能力框架](#5-产品能力框架)
6. [核心功能需求](#6-核心功能需求)
7. [非功能需求](#7-非功能需求)
8. [技术架构与集成设计](#8-技术架构与集成设计)
9. [用户体验与设计原则](#9-用户体验与设计原则)
10. [商业模式与定价策略](#10-商业模式与定价策略)
11. [产品路线图与里程碑](#11-产品路线图与里程碑)
12. [成功指标与度量标准](#12-成功指标与度量标准)
13. [风险与缓解策略](#13-风险与缓解策略)
14. [团队与资源配置](#14-团队与资源配置)
15. [附录](#15-附录)

---

## 1. 执行摘要

### 1.1 产品概述

AI Native 质量管理平台（QualityAI）是一款以AI为核心设计理念、工程为中心化的现代化质量管理平台。平台通过AI Agent自动化测试生命周期，显著降低测试门槛，提升测试效率10倍以上。

### 1.2 核心价值主张

- **AI First**：AI不是辅助功能，而是核心生产力，贯穿测试全生命周期
- **工程中心化**：测试资产属于Git工程，而非平台数据库
- **Self-Healing自愈**：行业领先的UI自动化自愈技术，降低脚本维护成本80%
- **CLI优先**：命令行+IDE为主要工作入口，支持离线操作
- **开源生态**：Community版本免费，建立开放生态

### 1.3 市场定位

| 维度 | 定位 |
|------|------|
| **目标市场** | 全球软件测试市场（2025年预计$56B） |
| **目标客户** | 中大型互联网企业、SaaS公司、金融科技、AI原生团队 |
| **价格区间** | 免费版 ~ $299/月 |
| **竞争优势** | 开源 + AI原生 + Self-Healing + 工程中心化 |

### 1.4 关键目标

| 目标类型 | 指标 | 目标值 |
|---------|------|--------|
| **北极星指标** | AI赋能的测试效率提升倍数 | >10x |
| **用户增长** | MAU（12个月） | 10,000+ |
| **商业化** | 付费转化率 | >5% |
| **技术能力** | Self-Healing成功率 | >85%（Phase 3） |

---

## 2. 产品愿景与定位

> 产品愿景、定位、市场分析与产品原则详见 [BRD第2章](../BRD.md#2-产品愿景与业务目标)。

本文档聚焦于技术实现方案，核心设计原则：
- **AI First**：AI能力是核心，而非附加功能
- **工程中心化**：测试资产属于Git工程，而非平台数据库
- **CLI优先**：命令行操作效率 > Web界面操作效率
- **开放标准**：基于Markdown、Git、Python等开放标准

---

## 3. 目标用户与使用场景

### 3.1 用户画像

#### 3.1.1 主要用户角色

| 角色 | 占比 | 核心诉求 | 使用频率 |
|------|------|---------|---------|
| **测试工程师** | 45% | 快速生成用例、自动修复脚本、减少重复劳动 | 每日8小时 |
| **开发工程师** | 30% | 快速编写测试、AI辅助调试、CI/CD集成 | 每日2-4小时 |
| **QA Lead/Manager** | 15% | 质量度量、团队效率、风险预警 | 每日1-2小时 |
| **产品经理** | 10% | 需求覆盖度、质量趋势、Bug分析 | 每周2-3小时 |

> 用户痛点分析详见 [BRD第1.2节](../BRD.md#12-当前痛点分析)。

### 3.2 核心使用场景

#### 场景1：AI辅助测试生成（每日高频）

**用户**：测试工程师

**流程**：
```bash
# 1. 从需求文档生成测试计划
qoder test plan --from requirements/feature_x.md

# 2. 从测试计划生成测试用例
qoder test generate --from tests/plans/feature_x_plan.md

# 3. 从测试用例生成测试脚本
qoder test script --cases tests/cases/feature_x/

# 4. 执行测试
qoder test run --suite tests/scripts/feature_x/ --env staging

# 5. 分析结果
qoder test analyze --report tests/reports/latest/
```

**预期效果**：
- 传统方式：需求→用例→脚本 = 2-3天
- AI辅助方式：需求→用例→脚本 = 2-3小时
- 效率提升：**10倍**

#### 场景2：Self-Healing自愈（变更触发）

**用户**：测试工程师

**触发条件**：UI自动化脚本执行失败（定位器失效）

**自愈流程**：
```
第一层：Locator Fallback（<1秒）
  → 尝试备用定位器（data-testid, CSS, XPath）
  → 单层的成功率：90-95%
  → 覆盖场景：约80%的定位器失效
  
第二层：Intent-Based AI推理（2-5秒）[V1.5+]
  → 分析Accessibility Tree
  → LLM语义理解元素意图
  → 匹配历史知识库
  → 单层的成功率：75-85%
  → 覆盖场景：约15%的复杂失效
  
第三层：人工告警
  → 生成Bug报告（Markdown）
  → 通知测试工程师
  → 等待人工修复
  → 覆盖场景：约5%的极端情况
```

**整体成功率计算**（Phase 1）：
```
Phase 1 整体成功率 = 第一层覆盖率×第一层成功率 + 第二层覆盖率×第二层成功率
                   = 80%×90% + 15%×0%（V1.0无第二层）
                   = 72% ≈ 70-75%
```

**预期效果**：
- 脚本维护时间减少：80%
- 自动化测试稳定性提升：3倍

#### 场景3：CI/CD集成（每次提交）

**用户**：开发工程师/DevOps

**流程**：
```yaml
# .gitlab-ci.yml 示例
test:
  stage: test
  script:
    - qoder test run --suite tests/scripts/smoke/ --env production
    - qoder test analyze --report tests/reports/ci/
    - qoder sync --push  # 同步结果到平台
```

**预期效果**：
- 测试执行完全自动化
- 质量门禁自动拦截
- 实时质量报告推送

---

## 4. 工程中心化架构设计

### 4.1 架构对比

| 维度 | 传统平台中心化 | 工程中心化（QualityAI） |
|------|--------------|----------------------|
| **资产存储** | 平台数据库 | Git仓库（Markdown文件） |
| **主要工作入口** | 浏览器Web界面 | 终端+IDE（CLI优先） |
| **AI定位** | 辅助功能（可选插件） | 核心生产力（默认启用） |
| **协作方式** | 平台账号权限管理 | Git PR + Code Review |
| **版本控制** | 平台内置版本历史 | Git原生版本控制 |
| **离线能力** | 不可用 | 完全支持 |
| **CI/CD集成** | 通过API调用 | 直接调用CLI命令 |
| **数据迁移** | 困难（平台锁定） | 简单（Git clone即可） |

### 4.2 Git工程目录规范

```
<project-root>/
├── requirements/                    # 需求文档（Markdown）
│   ├── feature_a.md
│   └── feature_b.md
├── docs/                           # 项目文档
│   ├── architecture.md
│   └── api-specs.md
├── tests/
│   ├── .qoder/                     # Qoder CLI配置
│   │   ├── config.yaml             # Agent配置
│   │   └── prompts/                # 自定义提示词
│   ├── plans/                      # 测试计划（Markdown）
│   │   └── feature_a_plan.md
│   ├── cases/                      # 测试用例（Markdown）
│   │   ├── feature_a/
│   │   │   ├── TC_001.md
│   │   │   └── TC_002.md
│   │   └── feature_b/
│   │       └── TC_003.md
│   ├── scripts/                    # 测试脚本（Python）
│   │   ├── feature_a/
│   │   │   ├── TC_001_valid_login.py
│   │   │   └── TC_002_invalid_login.py
│   │   └── conftest.py             # Pytest配置
│   ├── data/                       # 共享测试数据
│   │   ├── test_users.json
│   │   └── test_orders.csv
│   ├── bugs/                       # Bug报告（Markdown）
│   │   ├── BUG_001.md
│   │   └── BUG_002.md
│   └── reports/                    # 执行报告（JSON/HTML）
│       ├── execution_001.json
│       └── summary.html
├── .env.test                       # 测试环境变量
├── pyproject.toml                  # Python项目配置
└── requirements-test.txt           # 测试依赖
```

### 4.3 测试用例Markdown格式规范

```markdown
---
id: TC_001
title: 有效用户名和密码登录成功
module: 用户认证 / 登录
priority: P0
type: functional
author: 张三
created: 2026-04-19
updated: 2026-04-19
tags: [login, authentication, smoke]
script: ../scripts/feature_a/TC_001_valid_login.py
---

# TC_001：有效用户名和密码登录成功

## 测试目标
验证用户使用有效的用户名和密码能够成功登录系统。

## 前提条件
1. 用户已注册账户（username: testuser, password: Test123!）
2. 系统处于正常运行状态
3. 浏览器已打开登录页面

## 测试步骤

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| 1 | 输入用户名 `testuser` | 输入框显示 `testuser` |
| 2 | 输入密码 `Test123!` | 输入框显示掩码字符 |
| 3 | 点击"登录"按钮 | 跳转到首页，显示用户信息 |

## 输入数据
- 用户名：`testuser`
- 密码：`Test123!`

## 预期结果
1. 登录成功，跳转到首页
2. 页面右上角显示用户名 `testuser`
3. 浏览器URL包含 `/dashboard`

## 实际结果
（执行时自动填充）

## 执行状态
- [ ] 未执行
- [ ] 通过
- [ ] 失败
- [ ] 阻塞

## 备注
- 关联需求：requirements/feature_a.md#L15-L25
- Self-Healing：已启用（Locator Fallback + Intent-Based）
```

### 4.4 Bug报告Markdown格式规范

```markdown
---
id: BUG_001
title: 登录页面在移动端布局错乱
severity: P1
priority: High
type: ui
module: 用户认证 / 登录
reporter: AI Agent
assignee: 李四
created: 2026-04-19
status: open
test_case: ../cases/feature_a/TC_001.md
execution_id: execution_001
---

# BUG_001：登录页面在移动端布局错乱

## 问题描述
在执行TC_001时，AI检测到登录页面在移动端（375x812）布局异常，用户名输入框与密码输入框重叠。

## 复现步骤
1. 打开登录页面（https://example.com/login）
2. 调整浏览器窗口为移动端尺寸（375x812）
3. 观察页面布局

## 预期行为
用户名输入框和密码输入框应垂直排列，间距合理。

## 实际行为
两个输入框重叠，无法正常使用。

## 环境信息
- 浏览器：Chrome 120.0.6099.109
- 操作系统：macOS 14.2
- 屏幕尺寸：375x812（iPhone X）
- 测试环境：Staging

## 截图/录屏
- 截图：![login_mobile_bug](../reports/execution_001/screenshots/BUG_001.png)
- 录屏：[video](../reports/execution_001/videos/BUG_001.mp4)

## 日志信息
```
[2026-04-19 10:30:15] ERROR: Element overlap detected
  - username_input: bounds=(10, 100, 355, 50)
  - password_input: bounds=(10, 120, 355, 50)
  - overlap_area: 345x30 pixels
```

## AI分析
**根因推测**：CSS媒体查询未正确处理375px宽度断点。

**修复建议**：
```css
@media (max-width: 375px) {
  .login-form .input-group {
    margin-bottom: 20px;
  }
}
```

## 关联信息
- 关联测试用例：TC_001
- 关联需求：requirements/feature_a.md#L15-L25
- 相似Bug：BUG_000（已修复）

## 修复验证
- [ ] 开发已修复
- [ ] 测试已验证
- [ ] 已关闭
```

### 4.5 CLI工作流规范

#### 4.5.1 测试生成工作流

```bash
# 1. 从需求文档生成测试计划
qoder test plan \
  --from requirements/feature_x.md \
  --output tests/plans/feature_x_plan.md \
  --coverage goal:90%

# 2. 评审测试计划（人工+AI）
qoder test review tests/plans/feature_x_plan.md

# 3. 从测试计划生成测试用例
qoder test generate \
  --from tests/plans/feature_x_plan.md \
  --output tests/cases/feature_x/ \
  --format markdown

# 4. 从测试用例生成测试脚本
qoder test script \
  --cases tests/cases/feature_x/ \
  --output tests/scripts/feature_x/ \
  --framework playwright \
  --language python

# 5. 代码审查（Git PR流程）
git add tests/
git commit -m "feat: add test cases and scripts for feature_x"
git push origin feature/test-x
# 创建Pull Request，触发CI检查
```

#### 4.5.2 测试执行工作流

```bash
# 1. 本地执行测试
qoder test run \
  --suite tests/scripts/feature_x/ \
  --env staging \
  --parallel 4 \
  --retries 2 \
  --self-healing

# 2. 查看实时结果
qoder test status

# 3. 分析测试报告
qoder test analyze \
  --report tests/reports/latest/ \
  --format html \
  --output tests/reports/summary.html

# 4. 查看Self-Healing详情
qoder test healing-report \
  --execution execution_001

# 5. 同步结果到平台
qoder sync --push
```

#### 4.5.3 持续集成工作流

```bash
# CI/CD Pipeline（GitLab CI / GitHub Actions）
# 每次提交自动触发

qoder test run \
  --suite tests/scripts/smoke/ \
  --env production \
  --ci-mode

# 失败时自动创建Bug报告
qoder bug create \
  --from-failed-tests \
  --auto-assign

# 同步到质量平台
qoder sync --push --dashboard
```

---

## 5. 产品能力框架

### 5.1 能力全景图

```
AI Native 质量管理平台能力矩阵
├── 智能测试管理
│   ├── AI测试计划生成
│   ├── AI测试用例生成
│   ├── AI测试脚本生成
│   ├── 需求覆盖率分析
│   └── 测试资产版本控制
├── 自动化测试执行
│   ├── UI自动化（Playwright）
│   ├── API自动化（Pytest + httpx）
│   ├── 移动端自动化（Appium）
│   ├── 并行执行引擎
│   └── 多环境管理
├── Self-Healing自愈技术
│   ├── Locator Fallback（第一层）
│   ├── Intent-Based AI推理（第二层）
│   ├── 自愈知识库
│   ├── 自愈报告与分析
│   └── 自愈策略配置
├── 缺陷智能管理
│   ├── AI自动创建Bug
│   ├── Bug去重与关联
│   ├── 根因分析
│   ├── 修复建议生成
│   └── Bug趋势预测
├── 知识库与AI服务
│   ├── 测试模式学习
│   ├── 最佳实践推荐
│   ├── 风险预警
│   ├── 智能问答
│   └── 向量索引与检索
└── 协作与集成
    ├── Git工程协作
    ├── CI/CD集成
    ├── 第三方工具集成
    ├── 质量Dashboard
    └── 团队度量分析
```

> 能力优先级矩阵与RICE分析详见 [BRD第10.4节](../BRD.md#104-功能优先级-rice分析)。

---

## 6. 核心功能需求

### 6.1 功能测试管理

#### US-TC-001：AI生成测试计划

**作为** 测试工程师  
**我希望** 从需求文档自动生成测试计划  
**以便** 快速理解测试范围和覆盖率目标

**验收标准**：
- [ ] 支持从Markdown需求文档解析功能点
- [ ] AI自动生成测试策略（功能、边界、异常）
- [ ] 输出测试计划Markdown文件（包含测试范围、优先级、覆盖率目标）
- [ ] 支持人工评审和修改
- [ ] 生成时间：<5分钟（100页需求文档）

**技术规格**：
- 输入：需求文档（Markdown格式）
- 输出：测试计划（Markdown格式，符合Git工程规范）
- AI模型：LLM（支持GPT-4、Claude、本地模型）
- 处理流程：
  1. 解析需求文档结构
  2. 提取功能点和验收标准
  3. 生成测试策略（等价类、边界值、场景法）
  4. 输出测试计划Markdown

---

#### US-TC-002：AI生成测试用例

**作为** 测试工程师  
**我希望** 从测试计划自动生成测试用例  
**以便** 减少手工编写用例的时间

**验收标准**：
- [ ] 支持从测试计划Markdown解析测试策略
- [ ] AI自动生成测试用例（包含前置条件、步骤、预期结果）
- [ ] 输出测试用例Markdown文件（符合格式规范）
- [ ] 用例覆盖率 ≥90%（基于测试计划）
- [ ] 支持P0/P1/P2/P3优先级自动标注

**技术规格**：
- 输入：测试计划（Markdown）
- 输出：测试用例集（Markdown，按模块分目录）
- 用例格式：符合[测试用例Markdown格式规范](#43-测试用例markdown格式规范)
- 生成策略：
  - 功能测试：等价类划分 + 边界值分析
  - 异常测试：错误路径覆盖
  - 边界测试：极值测试

---

#### US-TC-003a：解析测试用例Markdown

**作为** AI Test Agent  
**我希望** 解析测试用例Markdown文件的结构和内容  
**以便** 提取测试步骤和预期结果用于脚本生成

**验收标准**：
- [ ] 支持解析Markdown Frontmatter（id、title、priority等元数据）
- [ ] 提取测试步骤表格（步骤、操作、预期结果）
- [ ] 提取前提条件和输入数据
- [ ] 解析成功率 ≥95%（符合格式规范的用例）
- [ ] 解析时间：<1秒/用例

**技术规格**：
- 输入：测试用例Markdown文件
- 输出：结构化JSON（包含元数据、步骤、断言）
- 解析库：python-frontmatter + markdown-table-parser

---

#### US-TC-003b：生成Playwright骨架代码

**作为** 测试工程师  
**我希望** 从解析后的测试用例生成Playwright骨架代码  
**以便** 快速搭建测试脚本框架

**验收标准**：
- [ ] 生成标准Pytest测试函数（包含函数名、docstring）
- [ ] 生成页面导航代码（page.goto）
- [ ] 生成基础元素定位代码（getByRole/getByText）
- [ ] 骨架代码可执行率 ≥90%（无语法错误）
- [ ] 生成时间：<5秒/用例

**技术规格**：
- 输入：结构化JSON（来自US-TC-003a）
- 输出：Python测试脚本（骨架）
- 代码模板：Jinja2模板引擎

---

#### US-TC-003c：生成断言逻辑

**作为** 测试工程师  
**我希望** AI自动生成测试断言代码  
**以便** 验证测试结果的正确性

**验收标准**：
- [ ] 从"预期结果"生成Playwright expect断言
- [ ] 支持URL验证、元素可见性、文本内容验证
- [ ] 断言覆盖率 ≥85%（基于预期结果）
- [ ] 不应生成包含硬编码敏感信息（密码、Token）的断言
- [ ] 生成时间：<10秒/用例

**技术规格**：
- 输入：结构化JSON（预期结果部分）
- 输出：Playwright expect语句
- AI模型：LLM（用于语义理解自然语言的预期结果）

---

#### US-TC-003d：集成Self-Healing中间件

**作为** 测试工程师  
**我希望** 生成的测试脚本自动集成Self-Healing能力  
**以便** 脚本具备自动修复定位器失效的能力

**验收标准**：
- [ ] 脚本自动添加@pytest.mark.self_healing装饰器
- [ ] 定位器使用Self-Healing包装器（而非原生Playwright定位器）
- [ ] 支持配置Self-Healing策略（启用/禁用、置信度阈值）
- [ ] 脚本可执行率 ≥75%（首次生成，含Self-Healing）[V1.0目标]
- [ ] 脚本可执行率 ≥85%（V1.5目标）

**技术规格**：
- 输入：Playwright骨架代码 + 断言代码
- 输出：集成Self-Healing的完整测试脚本
- Self-Healing中间件：自定义Playwright Locator包装器

---

**示例脚本**（完整整合版）：
```python
import pytest
from playwright.sync_api import Page, expect
from qoder.self_healing import SelfHealingLocator  # Self-Healing中间件

@pytest.mark.self_healing
def test_TC_001_valid_login(page: Page):
    """TC_001: 有效用户名和密码登录成功"""
    
    # 步骤1：打开登录页面
    page.goto("https://example.com/login")
    
    # 步骤2：输入用户名（使用Self-Healing定位器）
    locator = SelfHealingLocator(page)
    locator.get_by_role("textbox", name="用户名").fill("testuser")
    
    # 步骤3：输入密码
    locator.get_by_role("textbox", name="密码").fill("Test123!")
    
    # 步骤4：点击登录按钮
    locator.get_by_role("button", name="登录").click()
    
    # 验证：跳转到首页
    expect(page).to_have_url("**/dashboard")
    
    # 验证：显示用户名
    expect(page.get_by_text("testuser")).to_be_visible()
```

---

### 6.2 API测试管理

#### US-API-001：API测试脚本生成

**作为** 开发工程师  
**我希望** 从API文档自动生成API测试脚本  
**以便** 快速验证API功能

**验收标准**：
- [ ] 支持OpenAPI/Swagger规范解析
- [ ] AI自动生成Pytest + httpx测试脚本
- [ ] 覆盖正常流程、异常流程、边界值
- [ ] 脚本包含断言（状态码、响应体、响应时间）
- [ ] 支持Mock数据生成

**技术规格**：
- 输入：OpenAPI 3.0规范（YAML/JSON）
- 输出：Pytest测试脚本
- 测试框架：Pytest + httpx
- 测试覆盖：
  - 正常流程：200/201响应
  - 客户端错误：400/401/403/404
  - 服务端错误：500/502/503
  - 边界值：空参数、超长参数、特殊字符

---

### 6.3 UI自动化测试

#### US-UI-001：UI测试脚本执行

**作为** 测试工程师  
**我希望** 执行UI自动化测试脚本  
**以便** 验证UI功能正确性

**验收标准**：
- [ ] 支持本地执行和CI/CD执行
- [ ] 支持并行执行（≥4并发）
- [ ] 支持多浏览器（Chrome、Firefox、Safari）
- [ ] 失败时自动截图和录屏
- [ ] 生成HTML测试报告

**技术规格**：
- 执行引擎：Playwright Test Runner
- 并发模式：多进程并行
- 截图策略：失败时自动截图（PNG格式）
- 录屏策略：失败时自动录屏（WebM格式）
- 报告格式：HTML + JSON（符合JUnit XML标准）

---

#### US-UI-002a：Locator Fallback（第一层自愈）

**作为** 测试工程师  
**我希望** UI脚本定位器失效时能自动尝试备用定位器  
**以便** 快速修复简单的定位器变更

**验收标准**：
- [ ] 自动检测定位器失效（NoSuchElement异常）
- [ ] 按优先级尝试8种备用定位器策略
- [ ] 单层成功率：≥90%
- [ ] 响应时间：<1秒
- [ ] 覆盖场景：≥80%的定位器失效
- [ ] 自愈过程记录到执行日志

**技术规格**：
- 触发条件：Playwright Locator异常
- 定位器策略队列：getByRole → getByText → getByTestId → getByLabel → getByPlaceholder → getByAltText → CSS → XPath
- 实现方式：自定义Playwright Locator包装器

---

#### US-UI-002b：Intent-Based AI推理（第二层自愈）[V1.5+]

**作为** 测试工程师  
**我希望** 当Locator Fallback失败时，AI能语义理解元素意图并推理新定位器  
**以便** 修复复杂的页面结构变更

**验收标准**：
- [ ] 提取页面Accessibility Tree
- [ ] LLM分析原始定位器的测试意图
- [ ] 查询历史知识库匹配相似元素
- [ ] 单层成功率：≥75%
- [ ] 响应时间：2-5秒
- [ ] 覆盖场景：≥15%的复杂失效
- [ ] AI推理过程可追溯（包含决策依据）
- [ ] 低置信度修复（<0.7）标记为"待审核"

**技术规格**：
- 触发条件：Locator Fallback所有策略失败
- AI模型：LLM（GPT-4/Claude/本地模型）
- 知识库：Qdrant向量数据库
- 匹配算法：URL相似度25% + 元素角色20% + 文本相似度20% + 位置15% + 父级容器10% + CSS类名10%

---

#### US-UI-002c：人工告警与Bug生成（第三层）

**作为** 测试工程师  
**我希望** 当Self-Healing完全失败时能自动创建Bug报告  
**以便** 快速定位和修复问题

**验收标准**：
- [ ] 生成Bug报告Markdown文件
- [ ] Bug包含：失败截图、错误日志、AI根因分析
- [ ] Bug关联测试用例和执行记录
- [ ] 覆盖剩余5%极端情况
- [ ] 通知测试工程师（邮件/Slack/企微）

**技术规格**：
- 触发条件：Locator Fallback + Intent-Based均失败
- Bug格式：符合[Bug报告Markdown格式规范](#44-bug报告markdown格式规范)
- 通知方式：可配置（Webhook、Email、Slack）

---

> Self-Healing整体架构流程图、定位器替代策略与分阶段成功率目标详见 [BRD第4.2.3节](../BRD.md#423-self-healing智能维护服务核心竞争力)。

---

### 6.4 Self-Healing自愈技术（详细规格）

#### 6.4.1 架构设计

**整体流程**：

```
测试脚本执行
    ↓
定位器失效？
    ├─ 否 → 继续执行
    └─ 是 → 触发Self-Healing
              ↓
        第一层：Locator Fallback
              ├─ 成功 → 记录修复，继续执行
              └─ 失败 → 进入第二层
                        ↓
                  第二层：Intent-Based AI推理
                        ├─ 成功 → 记录修复，继续执行
                        └─ 失败 → 进入第三层
                                  ↓
                            第三层：人工告警
                                  ↓
                            生成Bug报告
                            通知测试工程师
```

#### 6.4.2 Locator Fallback实现

**定位器优先级队列**：

```python
class LocatorFallbackStrategy:
    """定位器回退策略"""
    
    def __init__(self):
        self.strategies = [
            self._get_by_role,        # 优先级1：语义化角色
            self._get_by_text,        # 优先级2：文本内容
            self._get_by_test_id,     # 优先级3：测试ID
            self._get_by_label,       # 优先级4：表单标签
            self._get_by_placeholder, # 优先级5：占位符
            self._get_by_alt_text,    # 优先级6：图片描述
            self._css_selector,       # 优先级7：CSS选择器
            self._xpath,              # 优先级8：XPath（最低）
        ]
    
    async def find_element(self, page, original_locator):
        """尝试所有定位器策略"""
        for strategy in self.strategies:
            try:
                element = await strategy(page, original_locator)
                if element:
                    self._log_success(strategy.__name__)
                    return element
            except Exception:
                self._log_failure(strategy.__name__)
                continue
        
        # 所有策略失败，进入AI推理层
        return None
```

#### 6.4.3 Intent-Based AI推理实现

**AI推理流程**：

```python
class IntentBasedHealing:
    """基于意图的AI自愈"""
    
    async def heal(self, page, original_locator, context):
        """AI推理修复定位器"""
        
        # 1. 提取页面Accessibility Tree
        a11y_tree = await self._extract_a11y_tree(page)
        
        # 2. 分析原始定位器意图
        intent = await self._analyze_intent(
            original_locator,
            context
        )
        
        # 3. 查询历史知识库
        historical_matches = await self._query_knowledge_base(
            intent,
            a11y_tree
        )
        
        # 4. LLM语义推理
        if not historical_matches:
            llm_suggestion = await self._llm_reasoning(
                intent,
                a11y_tree,
                context
            )
        
        # 5. 验证候选定位器
        best_match = await self._validate_candidates(
            historical_matches + [llm_suggestion]
        )
        
        return best_match
```

**知识库匹配算法**：

| 匹配维度 | 权重 | 说明 |
|---------|------|------|
| 页面URL相似度 | 25% | URL路径匹配度 |
| 元素角色匹配 | 20% | button/input/link等 |
| 文本相似度 | 20% | 按钮文本、标签文本 |
| 位置相似度 | 15% | 元素在页面中的相对位置 |
| 父级容器匹配 | 10% | 父元素、祖先元素 |
| CSS类名相似度 | 10% | 样式类名匹配 |

#### 6.4.4 自愈报告与分析

**自愈报告内容**：

```json
{
  "execution_id": "execution_001",
  "test_case": "TC_001",
  "healing_events": [
    {
      "timestamp": "2026-04-19T10:30:15Z",
      "layer": "locator_fallback",
      "original_locator": "getByRole('button', { name: '登录' })",
      "healed_locator": "getByTestId('login-button')",
      "strategy": "test_id_fallback",
      "confidence": 0.95,
      "duration_ms": 120,
      "success": true
    },
    {
      "timestamp": "2026-04-19T10:31:22Z",
      "layer": "intent_based",
      "original_locator": "getByText('提交订单')",
      "healed_locator": "getByRole('button', { name: '确认支付' })",
      "strategy": "llm_semantic_reasoning",
      "confidence": 0.78,
      "duration_ms": 3200,
      "success": true,
      "ai_analysis": {
        "intent": "用户提交订单操作",
        "reasoning": "页面文案从'提交订单'变更为'确认支付'，但功能相同",
        "evidence": [
          "元素位置相同（表单底部）",
          "元素角色相同（button）",
          "父级容器相同（订单表单）"
        ]
      }
    }
  ],
  "summary": {
    "total_failures": 2,
    "healing_success": 2,
    "healing_rate": 1.0,
    "avg_duration_ms": 1660
  }
}
```

---

### 6.5 AI智能服务

#### US-AI-001：AI智能问答

**作为** 测试工程师  
**我希望** 向AI助手提问测试相关问题  
**以便** 快速获取测试最佳实践和解决方案

**验收标准**：
- [ ] 支持自然语言提问
- [ ] AI基于知识库回答（引用测试资产、历史Bug、最佳实践）
- [ ] 回答包含引用来源（可追溯）
- [ ] 响应时间：<3秒
- [ ] 支持多轮对话

**技术规格**：
- 底层技术：RAG（检索增强生成）
- 知识库：向量数据库（Qdrant）
- 检索策略：语义相似度 + 关键词匹配
- 回答生成：LLM（GPT-4/Claude/本地模型）

---

#### US-AI-002：AI风险预警

**作为** QA Manager  
**我希望** AI自动识别质量风险  
**以便** 提前干预和预防

**验收标准**：
- [ ] 自动分析测试覆盖率趋势
- [ ] 识别高风险模块（变更频率>5次/周 且 Bug密度>3/千行代码）
- [ ] 预测发布风险（基于历史数据）
- [ ] 推送预警通知（邮件/Slack/企微）
- [ ] 提供风险缓解建议
- [ ] 预警准确率：≥80%（历史数据回测）

**技术规格**：
- 数据源：测试执行记录、Bug报告、代码变更
- 算法：时间序列分析 + 聚类分析
- 预警阈值：可配置（覆盖率下降>10%、Bug增长率>20%）
- **高风险模块定义**：变更频率>5次/周 且 Bug密度>3/千行代码

---

### 6.6 缺陷管理

#### US-BUG-001：AI自动创建Bug

**作为** 测试工程师  
**我希望** AI自动检测缺陷并创建Bug报告  
**以便** 减少手工编写Bug的时间

**验收标准**：
- [ ] 测试失败时自动创建Bug（Markdown格式）
- [ ] Bug包含：失败截图、日志、AI根因分析、修复建议
- [ ] Bug关联测试用例和执行记录
- [ ] 支持自动分配给相关开发人员
- [ ] 支持Bug去重（检测相似Bug）

**技术规格**：
- Bug格式：符合[Bug报告Markdown格式规范](#44-bug报告markdown格式规范)
- 根因分析：基于错误日志、页面DOM树、历史Bug
- 修复建议：基于相似Bug的修复方案
- 自动分配：基于代码所有权（Git blame）

---

### 6.7 知识库管理

#### US-KB-001：测试模式学习

**作为** AI系统  
**我希望** 从历史测试数据学习测试模式  
**以便** 提升测试生成和自愈的准确性

**验收标准**：
- [ ] 自动索引测试用例、脚本、执行记录、Bug报告
- [ ] 向量索引支持语义检索
- [ ] 学习测试模式（页面结构、元素特征、交互流程）
- [ ] 知识库版本控制（与Git同步）
- [ ] 支持知识检索（Self-Healing、测试生成调用）
- [ ] 学习有效性：使用新知识库后，Self-Healing成功率提升≥5%
- [ ] 知识更新延迟：执行完成后<5分钟完成索引

**技术规格**：
- 向量数据库：Qdrant
- 索引类型：测试用例、脚本、Bug、执行记录
- 更新策略：每次执行后自动更新
- 检索API：RESTful API（供AI服务调用）
- **学习有效性评判标准**：使用新知识库后，Self-Healing成功率提升≥5%

---

### 6.8 执行引擎

#### US-EXE-001：并行测试执行

**作为** 测试工程师  
**我希望** 并行执行测试用例  
**以便** 缩短测试执行时间

**验收标准**：
- [ ] 支持多进程并行执行（≥4并发）
- [ ] 支持分布式执行（多机器）
- [ ] 自动分配测试用例到并行进程
- [ ] 汇总执行结果（包含截图、日志、报告）
- [ ] 支持失败重试（可配置重试次数）

**技术规格**：
- 并行模式：多进程（Python multiprocessing）
- 分布式：Celery + Redis
- 结果汇总：JUnit XML + HTML报告
- 重试策略：指数退避（1s, 2s, 4s, ...）

---

## 7. 非功能需求

### 7.1 性能需求

| 指标 | 目标值 | 测量方式 |
|------|--------|---------|
| **页面响应时间** | <2秒（95%请求） | 前端性能监控 |
| **API响应时间** | <500ms（95%请求） | APM工具 |
| **CLI命令响应** | <1秒（本地操作） | 命令执行时间 |
| **AI生成时间** | <5分钟（100页需求文档） | 端到端时间 |
| **Self-Healing响应** | <5秒（第二层AI推理） | 自愈日志 |
| **并发执行能力** | ≥200并发（分布式系统上限） | 压力测试 |
| **知识库检索** | <500ms（向量检索） | Qdrant性能指标 |

### 7.2 可用性需求

| 指标 | 目标值 | 说明 |
|------|--------|------|
| **系统可用性** | ≥99.9% | 年度停机时间<8.76小时 |
| **CLI可用性** | 100%（本地执行） | 离线可用 |
| **数据持久化** | 100%（Git仓库） | Git保证 |
| **故障恢复** | <5分钟 | 自动重启 |

### 7.3 安全性需求

| 需求 | 要求 | 实现方式 |
|------|------|---------|
| **认证** | OAuth 2.0 / JWT | 平台登录 |
| **授权** | RBAC（基于角色） | Admin/Tester/Developer/Viewer |
| **数据加密** | TLS 1.3（传输中） | HTTPS强制 |
| **密钥管理** | 环境变量/密钥管理服务 | .env.test不提交Git |
| **审计日志** | 所有AI操作可追溯 | 日志记录到Git |

### 7.4 兼容性需求

| 维度 | 支持范围 |
|------|---------|
| **浏览器** | Chrome 110+, Firefox 110+, Safari 16+ |
| **操作系统** | macOS 13+, Ubuntu 22.04+, Windows 11+ |
| **Python版本** | 3.11+ |
| **Node版本** | 18+（Playwright依赖） |
| **Git版本** | 2.30+ |
| **CI/CD** | GitLab CI, GitHub Actions, Jenkins |

### 7.5 可维护性需求

| 需求 | 要求 |
|------|------|
| **代码规范** | Black + Flake8（Python）, ESLint（TypeScript） |
| **测试覆盖率** | ≥80%（核心模块） |
| **文档完整性** | 所有公开API有文档 |
| **日志规范** | 结构化日志（JSON格式） |
| **监控告警** | 集成Prometheus + Grafana |

---

## 8. 技术架构与集成设计

### 8.1 技术栈选型

#### 8.1.1 CLI Test Agent

| 组件 | 技术选型 | 版本 | 说明 |
|------|---------|------|------|
| **语言** | Python | 3.11+ | 主开发语言 |
| **CLI框架** | Typer + Rich | 最新 | 命令行交互 |
| **AI工作流** | LangChain + LangGraph | 最新 | Agent编排（LangChain提供LLM抽象层，LangGraph负责工作流编排） |
| **测试框架** | Playwright (Python) | 最新 | UI自动化 |
| **API测试** | Pytest + httpx | 最新 | API自动化 |
| **报告生成** | Allure / pytest-html | 最新 | 测试报告 |

#### 8.1.2 后端服务

| 组件 | 技术选型 | 版本 | 说明 |
|------|---------|------|------|
| **框架** | Django | 5.x | Web框架 |
| **API** | Django REST Framework | 最新 | RESTful API |
| **异步任务** | Celery + Redis | 最新 | 任务队列 |
| **数据库** | PostgreSQL | 15+ | 主数据库 |
| **缓存** | Redis | 7+ | 缓存/会话 |
| **向量数据库** | Qdrant | 最新 | 知识库向量索引 |
| **认证** | JWT + OAuth 2.0 | 最新 | 身份认证 |

#### 8.1.3 前端平台

| 组件 | 技术选型 | 版本 | 说明 |
|------|---------|------|------|
| **框架** | Vue 3 | 3.4+ | 前端框架 |
| **语言** | TypeScript | 5.x | 类型安全 |
| **UI库** | Element Plus | 最新 | 组件库 |
| **状态管理** | Pinia | 最新 | 状态管理 |
| **构建工具** | Vite | 5.x | 快速构建 |
| **图表库** | ECharts | 5.x | 数据可视化 |

#### 8.1.4 基础设施

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| **容器化** | Docker + Docker Compose | 本地开发 |
| **编排** | Kubernetes (K8s) | 生产部署 |
| **CI/CD** | GitLab CI / GitHub Actions | 持续集成 |
| **监控** | Prometheus + Grafana | 系统监控 |
| **日志** | ELK Stack | 日志管理 |
| **网关** | Nginx / Traefik | 反向代理 |

### 8.2 系统架构

```
┌──────────────────────────────────────────────────────┐
│                    用户交互层                          │
│  ┌─────────────┐    ┌─────────────┐    ┌──────────┐  │
│  │  CLI (Typer) │    │ Web (Vue 3) │    │   API    │  │
│  │  + Rich UI   │    │ + Element   │    │ Clients  │  │
│  └─────────────┘    └─────────────┘    └──────────┘  │
└──────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│                    API网关层                           │
│  ┌──────────────────────────────────────────────┐   │
│  │  Nginx / Traefik (路由、限流、SSL)             │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│                    业务服务层                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │测试管理服务│ │执行引擎服务│ │缺陷管理服务│ │AI服务      │ │
│  │(Django)  │ │(Celery)  │ │(Django)  │ │(LangChain+ │ │
│  │          │ │          │ │          │ │ LangGraph) │ │
│  └──────────┘ └──────────┘ └──────────┘ └─────────┘ │
└──────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│                    AI能力层                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │测试生成  │ │Self-Heal │ │根因分析  │ │智能问答 │ │
│  │Agent     │ │Agent     │ │Agent     │ │Agent    │ │
│  └──────────┘ └──────────┘ └──────────┘ └─────────┘ │
└──────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│                    执行引擎层                          │
│  ┌──────────────┐  ┌──────────────┐                  │
│  │UI自动化       │  │API自动化      │                  │
│  │(Playwright)  │  │(Pytest+httpx)│                  │
│  └──────────────┘  └──────────────┘                  │
└──────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│                    数据存储层                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │PostgreSQL│ │  Redis   │ │  Qdrant  │ │Git仓库  │ │
│  │(主数据库) │ │(缓存/队列)│ │(向量DB)  │ │(测试资产)│ │
│  └──────────┘ └──────────┘ └──────────┘ └─────────┘ │
└──────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│                    外部集成层                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │GitLab CI │ │GitHub    │ │Slack/    │ │Jira/    │ │
│  │          │ │Actions   │ │企微      │ │飞书     │ │
│  └──────────┘ └──────────┘ └──────────┘ └─────────┘ │
└──────────────────────────────────────────────────────┘
```

### 8.3 Git工程集成

**Git Hooks集成**：

```bash
# .husky/pre-commit
#!/bin/sh
# 提交前自动运行测试
qoder test run --suite tests/scripts/smoke/ --env local

# .husky/pre-push
#!/bin/sh
# 推送前同步测试结果到平台
qoder sync --push
```

**GitHub Actions集成**：

```yaml
name: QualityAI Test Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
          playwright install
      
      - name: Run tests
        run: |
          qoder test run \
            --suite tests/scripts/ \
            --env staging \
            --parallel 4 \
            --self-healing
      
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-report
          path: tests/reports/
      
      - name: Sync to platform
        if: always()
        run: |
          qoder sync --push
```

### 8.4 部署架构

#### 8.4.1 本地开发（Docker Compose）

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: qualityai
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"
  
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
  
  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - qdrant
  
  frontend:
    build: ./frontend
    command: npm run dev
    ports:
      - "3000:3000"
```

#### 8.4.2 生产部署（Kubernetes）

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qualityai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: qualityai-backend
  template:
    metadata:
      labels:
        app: qualityai-backend
    spec:
      containers:
      - name: backend
        image: qualityai/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          value: "redis://redis:6379"
        - name: QDRANT_URL
          value: "http://qdrant:6333"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: qualityai-backend
spec:
  selector:
    app: qualityai-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

---

## 9. 用户体验与设计原则

### 9.1 CLI用户体验

**设计原则**：
1. **渐进式披露**：简单命令默认输出简洁，`--verbose`显示详情
2. **即时反馈**：长时间操作显示进度条和ETA
3. **错误友好**：错误消息包含原因、解决方案、相关链接
4. **命令补全**：支持Tab补全和智能提示
5. **颜色编码**：成功（绿色）、警告（黄色）、错误（红色）

**示例交互**：

```bash
$ qoder test run --suite tests/scripts/feature_a/

🚀 Running tests...
├─ TC_001_valid_login ...... ✅ Passed (2.3s)
├─ TC_002_invalid_password . ✅ Passed (1.8s)
├─ TC_003_locked_account ... 🔄 Self-Healing (3.2s)
│  ├─ Locator Fallback: Failed
│  ├─ Intent-Based AI: Success (confidence: 0.82)
│  └─ Healed: getByRole('button', { name: '确认' })
└─ TC_004_remember_me ...... ❌ Failed (5.1s)
   └─ Bug report created: tests/bugs/BUG_002.md

✅ 3/4 passed (75%)
📊 Report: tests/reports/execution_002/summary.html
🐛 Bugs: tests/bugs/BUG_002.md
```

### 9.2 Web界面设计

**设计原则**：
1. **Dashboard优先**：首页展示关键质量指标
2. **可视化优先**：图表 > 表格 > 文本
3. **快速操作**：高频操作一键可达
4. **上下文关联**：Bug、用例、脚本、执行记录互相关联
5. **实时同步**：Git变更自动同步到平台

**核心页面**：
- **Dashboard**：质量总览、趋势图、风险预警
- **测试资产**：用例库、脚本库、执行记录
- **缺陷管理**：Bug列表、趋势分析、根因分布
- **Self-Healing**：自愈报告、成功率趋势、策略配置
- **知识库**：测试模式、最佳实践、智能问答
- **团队度量**：效率指标、覆盖率、质量趋势

### 9.3 移动端适配

- **响应式设计**：适配手机、平板、桌面
- **核心功能**：查看报告、审批用例、处理Bug
- **推送通知**：质量预警、执行完成、Bug分配

---

## 10. 商业模式与定价策略

> 版本定价策略详见 [BRD第7.2节](../BRD.md#72-版本与定价策略)。

### 10.2 功能对比矩阵

| 功能模块 | Community | Pro | Enterprise | Cloud |
|---------|-----------|-----|-----------|-------|
| CLI Test Agent | ✅ 基础 | ✅ 完整 | ✅ 完整 | ✅ 完整 |
| Self-Healing | ✅ 基础（Locator Fallback） | ✅ 高级（+Intent-Based） | ✅ 高级 | ✅ 高级 |
| AI测试生成 | ✅ 100次/月 | ✅ 1000次/月 | ✅ 无限 | ✅ 无限 |
| 平台Dashboard | ❌ | ✅ | ✅ | ✅ |
| 团队知识库 | ❌ | ✅ | ✅ | ✅ |
| 私有部署 | ❌ | ❌ | ✅ | ❌ |
| SSO/SAML | ❌ | ❌ | ✅ | ❌ |
| 高级权限 | ❌ | ❌ | ✅ | ❌ |
| 定制AI模型 | ❌ | ❌ | ✅ | ❌ |
| SLA保障 | ❌ | ❌ | ✅ 99.9% | ✅ 99.5% |
| 并发执行 | 4 | 20 | 200（系统上限） | 50 |
| 技术支持 | 社区 | 邮件 | 专属顾问 | 邮件 |

### 10.3 免费增值策略

**Community版免费能力**：
- CLI Test Agent完整工作流
- Self-Healing第一层（Locator Fallback）
- 本地测试执行（4并发）
- Git工程完整支持
- Markdown测试资产
- 社区支持

**升级触发点**：
- 需要Self-Healing第二层（Intent-Based AI）
- 需要平台Dashboard和团队协作
- 需要 >100次/月 AI生成
- 需要 >4并发执行
- 需要私有部署和SSO

---

## 11. 产品路线图与里程碑

> 完整产品路线图、V1.0 MVP范围与Self-Healing专项路线详见 [BRD第10章](../BRD.md#10-产品路线图)。

### 11.1 技术实施里程碑（V1.0）

| 里程碑 | 时间 | 技术交付物 | 验收标准 |
|--------|------|-----------|---------|
| **M1: 基础架构** | 4月 | CLI框架、Git工程规范、Markdown格式规范 | 可生成测试计划 |
| **M2: AI测试生成** | 5月 | LangChain Prompt模板、测试用例生成器 | 生成成功率≥70% |
| **M3: UI自动化** | 6月 | Playwright集成、Self-Healing中间件 | 脚本可执行率≥75% |
| **M4: Self-Healing** | 7月 | LocatorFallbackStrategy类、8种策略实现 | 自愈成功率≥70% |
| **M5: Bug管理** | 8月 | Bug Markdown生成器、失败上下文收集 | Bug创建流程打通 |
| **M6: 发布准备** | 9月 | 文档、教程、Docker Compose配置 | 100+内测用户 |

---

## 12. 成功指标与度量标准

> 业务KPI（北极星指标、效率指标、质量指标、用户指标）详见 [BRD第8章](../BRD.md#8-业务成功指标kpi)。

### 12.1 技术指标

| 指标类别 | 指标名称 | V1.0目标 | V2.0目标 | 测量方式 |
|---------|---------|---------|---------|---------|
| **性能** | 页面响应时间 | <2秒 | <1秒 | 性能监控 |
| **性能** | API响应时间 | <500ms | <200ms | APM工具 |
| **性能** | 并发执行能力 | 4并发 | 200并发 | 压力测试 |
| **可用性** | 系统可用性 | 99.5% | 99.9% |  uptime监控 |
| **质量** | Self-Healing成功率 | 70% | 85% | 自愈日志 |
| **质量** | AI生成成功率 | 70% | 90% | 用户反馈 |
| **质量** | 脚本可执行率 | 75% | 95% | 执行记录 |

---

## 13. 风险与缓解策略

> 业务风险、市场风险、合规风险详见 [BRD第9.3节](../BRD.md#93-风险与缓解策略)。

### 13.1 技术风险

| 风险 | 影响 | 概率 | 缓解策略 |
|------|------|------|---------|
| **Self-Healing成功率不达标** | 高 | 中 | 分阶段目标（70%→80%→85%），V1.0仅实现Locator Fallback降低风险 |
| **AI生成质量不稳定** | 中 | 中 | 人工评审环节，收集用户反馈，持续训练模型；V1.0目标调整为≥75% |
| **多模型兼容性** | 中 | 低 | LangChain抽象LLM接口，支持GPT-4/Claude/本地模型 |
| **性能瓶颈** | 中 | 低 | 并行执行优化，分布式架构，缓存策略 |
| **LLM依赖风险** 🔴 | 高 | 中 | GPT-4/Claude API变更、价格上涨、服务中断；缓解：①抽象LLM接口层 ②准备开源模型降级方案（Llama 3、Qwen） ③本地缓存常用AI生成结果 |
| **Playwright兼容性问题** 🟡 | 中 | 中 | 目标应用使用非标准Web技术（Canvas重度应用、Flash）；缓解：①V1.0明确支持范围（标准HTML/CSS/JS） ②列出不支持的技术栈 ③提供手动编写脚本降级方案 |
| **Self-Healing误修复风险** 🔴 | 高 | 中 | AI错误地"修复"正确定位器，导致测试通过但逻辑错误（漏测）；缓解：①Self-Healing记录必须人工审核（首次） ②提供"置信度阈值"配置 ③低置信度修复标记为"待审核" |

---

## 14. 团队与资源配置

### 14.1 核心团队

| 角色 | 人数 | 职责 |
|------|------|------|
| **产品经理** | 1 | 产品规划、需求管理、用户调研 |
| **技术架构师** | 1 | 技术选型、架构设计、代码审查 |
| **AI工程师** | 2 | AI Agent开发、Self-Healing、模型优化 |
| **后端工程师** | 2 | Django API、Celery任务、数据库 |
| **前端工程师** | 1 | Vue 3 Dashboard、数据可视化 |
| **测试工程师** | 1 | 平台测试、CLI测试、性能测试 |
| **DevOps工程师** | 1 | CI/CD、Docker/K8s、监控 |

**总计**：9人核心团队

### 14.2 资源配置

| 资源类型 | 配置 | 成本（月） |
|---------|------|-----------|
| **云服务器** | AWS/GCP 3台（8C16G） | $1,500 |
| **数据库** | PostgreSQL（托管） | $200 |
| **缓存** | Redis（托管） | $100 |
| **向量数据库** | Qdrant（自建） | $0 |
| **LLM API** | GPT-4/Claude（测试生成+Self-Healing+智能问答） | $5,000-8,000 |
| **CI/CD** | GitLab CI | $100 |
| **监控** | Prometheus + Grafana | $0 |
| **总计** | | **$6,900-9,900/月** |

### 14.3 开发工具

| 工具 | 用途 | 成本 |
|------|------|------|
| **IDE** | VS Code / Cursor | 免费 |
| **版本控制** | Git + GitHub/GitLab | 免费 |
| **项目管理** | Linear / Jira | $200/月 |
| **文档** | Notion / Confluence | $100/月 |
| **沟通** | Slack / 企微 | 免费 |

---

## 15. 附录

### 15.1 术语表

> 业务术语（AI Native、工程中心化、Self-Healing、Locator Fallback、Intent-Based、Qoder、QualityAI、RAG、A11y、LLM）详见 [BRD第11章](../BRD.md#11-术语表)。

**技术术语**：

| 术语 | 定义 |
|------|------|
| **Page Object** | 页面对象模式（UI测试设计模式） |
| **RBAC** | Role-Based Access Control（基于角色的访问控制） |
| **LangChain** | AI应用开发框架，提供LLM抽象层和工具链 |
| **LangGraph** | 基于LangGraph的Agent工作流编排库 |

### 15.2 相关文档

| 文档 | 链接 | 说明 |
|------|------|------|
| **BRD** | [BRD.md](../BRD.md) | 业务需求文档 |
| **L1规范** | [L1目录](../L1/) | 详细设计文档 |
| **CLI Test Agent** | [L1-01](../L1/L1-01_CLI_Test_Agent.md) | CLI设计规范 |
| **测试用例管理** | [L1-02](../L1/L1-02_Test_Case_Management.md) | 用例管理规范 |
| **UI自动化** | [L1-03](../L1/L1-03_UI_Automation.md) | UI自动化规范 |
| **API自动化** | [L1-04](../L1/L1-04_API_Automation.md) | API自动化规范 |
| **执行引擎** | [L1-05](../L1/L1-05_Execution_Engine.md) | 执行引擎规范 |
| **Bug管理** | [L1-06](../L1/L1-06_Bug_Management.md) | Bug管理规范 |
| **知识库** | [L1-07](../L1/L1-07_Knowledge_Base.md) | 知识库规范 |
| **平台Portal** | [L1-08](../L1/L1-08_Platform_Portal.md) | 平台设计规范 |

### 15.3 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|---------|--------|
| V1.0 | 2026-04-19 | 初始版本，融合BRD、AI-Quality-Platform-PRD、L0_PRD | QualityAI产品团队 |
| V1.1 | 2026-04-19 | 评审修订版：①修正Self-Healing成功率矛盾 ②拆分US-TC-003和US-UI-002 ③调整V1.0范围（Intent-Based推迟到V1.5） ④补充LLM依赖、误修复等5个重大风险 ⑤修正并发能力矛盾 ⑥统一术语 ⑦补充验收标准定义 ⑧调整LLM API成本 | QualityAI产品团队 |
| V1.2 | 2026-04-19 | 职责分离重构版：①删除重复内容~250行（产品愿景、痛点分析、能力矩阵、Self-Healing架构、定价表、路线图、业务KPI、业务风险、术语） ②添加10处BRD交叉引用 ③PRD从1882行精简到~1632行（精简13%） ④明确PRD聚焦技术实现（User Stories、验收标准、技术规格） | QualityAI产品团队 |

---

**文档结束**

*本文档是AI Native质量管理平台的核心产品需求文档，融合了业务需求（BRD）、详细功能规格（AI-Quality-Platform-PRD）和工程技术架构（L0_PRD），作为后续产品设计、技术开发和商业化推进的基准文档。*
