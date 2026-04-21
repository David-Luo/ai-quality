# src/qoder/parsers/markdown_parser.py

import re
import frontmatter
from qoder.models.case_models import ParsedCase, TestStep

REQUIRED_FIELDS = {"id", "title", "type"}


def parse_case_file(file_path: str) -> ParsedCase:
    """解析单个测试用例 Markdown 文件"""
    post = frontmatter.load(file_path)
    
    # 验证必填字段
    metadata = post.metadata
    for field in REQUIRED_FIELDS:
        if field not in metadata:
            raise ValueError(f"Missing required field: {field}")
    
    # 解析步骤表
    steps = _parse_steps_table(post.content)
    if not steps:
        raise ValueError("No test steps found")
    
    # 解析输入数据表
    test_data = _parse_test_data_table(post.content)
    
    # 解析前提条件
    preconditions = _parse_preconditions(post.content)
    
    # 解析备注
    notes = _parse_notes(post.content)
    
    return ParsedCase(
        id=metadata["id"],
        title=metadata["title"],
        module=metadata.get("module", ""),
        priority=metadata.get("priority", "P3"),
        type=metadata["type"],
        tags=metadata.get("tags", []),
        status=metadata.get("status", "draft"),
        preconditions=preconditions,
        steps=steps,
        test_data=test_data,
        notes=notes,
        source_path=file_path,
        frontmatter=metadata,
    )


def _parse_steps_table(content: str) -> list[TestStep]:
    """解析测试步骤 Markdown 表格"""
    steps = []
    # 查找 ## 测试步骤 section
    section_match = re.search(r'## 测试步骤\s*\n(.*?)(?=##|\Z)', content, re.DOTALL)
    if not section_match:
        return steps
    
    section_content = section_match.group(1)
    
    # 解析 Markdown 表格
    lines = section_content.strip().split('\n')
    table_lines = [l.strip() for l in lines if l.strip().startswith('|')]
    
    if len(table_lines) < 3:  # 至少需要表头+分隔线+1行数据
        return steps
    
    # 跳过表头和分隔线
    for line in table_lines[2:]:
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if len(cells) >= 3:
            step_num = int(cells[0]) if cells[0].isdigit() else len(steps) + 1
            action = cells[1]
            expected = cells[2]
            request = cells[3] if len(cells) > 3 else None
            steps.append(TestStep(step_num, action, expected, request))
    
    return steps


def _parse_test_data_table(content: str) -> dict[str, str]:
    """解析输入数据表"""
    test_data = {}
    section_match = re.search(r'## 输入数据\s*\n(.*?)(?=##|\Z)', content, re.DOTALL)
    if not section_match:
        return test_data
    
    lines = section_match.group(1).strip().split('\n')
    table_lines = [l.strip() for l in lines if l.strip().startswith('|')]
    
    for line in table_lines[2:]:
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if len(cells) >= 2:
            key = cells[0].strip('`')
            value = cells[1].strip('`')
            test_data[key] = value
    
    return test_data


def _parse_preconditions(content: str) -> list[str]:
    """解析前提条件"""
    preconditions = []
    section_match = re.search(r'## 前提条件\s*\n(.*?)(?=##|\Z)', content, re.DOTALL)
    if not section_match:
        return preconditions
    
    for line in section_match.group(1).strip().split('\n'):
        line = line.strip()
        if line.startswith('- '):
            preconditions.append(line[2:].strip())
    
    return preconditions


def _parse_notes(content: str) -> str:
    """解析备注"""
    section_match = re.search(r'## 备注\s*\n(.*?)(?=##|\Z)', content, re.DOTALL)
    return section_match.group(1).strip() if section_match else ""
