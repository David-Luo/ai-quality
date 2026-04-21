# tests/unit/test_markdown_parser.py

import pytest
from qoder.parsers.markdown_parser import parse_case_file


def test_parse_valid_ui_case(tmp_path):
    """测试解析有效的 UI 测试用例"""
    case_content = """---
id: TC_001
title: 有效登录
module: auth
type: functional
priority: P0
---

## 前提条件

- 用户已注册

## 测试步骤

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 打开登录页 | 页面正常显示 |
| 2 | 输入用户名 | 输入框显示内容 |
| 3 | 点击登录按钮 | 跳转到 Dashboard |

## 输入数据

| 字段 | 值 |
|------|-----|
| 用户名 | test@example.com |
"""
    case_file = tmp_path / "TC_001.md"
    case_file.write_text(case_content)
    
    case = parse_case_file(str(case_file))
    
    assert case.id == "TC_001"
    assert case.title == "有效登录"
    assert len(case.steps) == 3
    assert case.steps[0].action == "打开登录页"
    assert case.test_data["用户名"] == "test@example.com"


def test_parse_missing_required_field(tmp_path):
    """测试缺少必填字段时抛出异常"""
    case_content = """---
id: TC_001
title: 缺少 type 字段
---

## 测试步骤

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 操作 | 结果 |
"""
    case_file = tmp_path / "TC_001.md"
    case_file.write_text(case_content)
    
    with pytest.raises(ValueError, match="Missing required field: type"):
        parse_case_file(str(case_file))


def test_parse_no_steps(tmp_path):
    """测试没有步骤时抛出异常"""
    case_content = """---
id: TC_001
title: 没有步骤
type: functional
---

只有备注,没有步骤表。
"""
    case_file = tmp_path / "TC_001.md"
    case_file.write_text(case_content)
    
    with pytest.raises(ValueError, match="No test steps found"):
        parse_case_file(str(case_file))
