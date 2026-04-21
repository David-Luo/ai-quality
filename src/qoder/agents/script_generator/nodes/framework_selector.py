# src/qoder/agents/script_generator/nodes/framework_selector.py

import re


def _has_http_keywords(case) -> bool:
    """检查用例步骤是否包含 HTTP 关键词"""
    for step in case.steps:
        if re.search(r'\b(GET|POST|PUT|DELETE|PATCH)\b', step.action or "", re.I):
            return True
        if "/api/" in (step.action or ""):
            return True
    return False


def framework_selector_node(state: dict) -> dict:
    """为每个用例选择目标框架"""
    cli_framework = state.get("config", {}).get("_cli_framework")
    
    for case in state["parsed_cases"]:
        # 优先级判断
        if cli_framework:
            case._framework = cli_framework
        elif case.type == "api":
            case._framework = "pytest"
        elif _has_http_keywords(case):
            case._framework = "pytest"
        elif case.type in ("ui", "functional", "boundary", "exception", "security"):
            case._framework = "playwright"
        else:
            case._framework = "playwright"  # 兜底
    
    return {"parsed_cases": state["parsed_cases"]}
