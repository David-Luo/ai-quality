# src/qoder/agents/script_generator/nodes/case_reader.py

from pathlib import Path
from qoder.parsers.markdown_parser import parse_case_file


def case_reader_node(state: dict) -> dict:
    """解析所有输入的用例 Markdown 文件"""
    cases_path = Path(state["case_files"])
    
    if cases_path.is_file():
        md_files = [cases_path]
    else:
        md_files = list(cases_path.rglob("*.md"))
    
    parsed_cases = []
    errors = []
    
    for md_file in md_files:
        try:
            case = parse_case_file(str(md_file))
            parsed_cases.append(case)
        except Exception as e:
            errors.append(f"Skipped {md_file}: {e}")
    
    return {
        "case_files": [str(f) for f in md_files],
        "parsed_cases": parsed_cases,
        "errors": errors,
        "summary": {
            "total": len(md_files),
            "skipped": len(errors),
            "errors": errors,
        },
    }
