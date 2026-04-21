# src/qoder/agents/script_generator/nodes/case_updater.py

import os
from pathlib import Path
from datetime import datetime, timezone

import frontmatter
from jinja2 import Environment, FileSystemLoader


def case_updater_node(state: dict) -> dict:
    """写入脚本文件 + 回写用例 Frontmatter + 生成 conftest.py"""
    
    for script in state.get("generated_scripts", []):
        if script.get("validation_status") in ("passed", "needs_review"):
            # 写入脚本文件
            output_path = Path(script["output_path"])
            if not state.get("dry_run"):
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(script["code"], encoding="utf-8")
            
            # 生成 conftest.py(若不存在)
            _ensure_conftest(output_path.parent, script["framework"], state.get("dry_run", False))
            
            # 回写用例 Frontmatter
            _update_case_frontmatter(script, state.get("dry_run", False))
    
    # 构建 summary
    summary = state.get("summary", {})
    summary["generated"] = len([s for s in state["generated_scripts"] 
                                if s.get("validation_status") in ("passed", "needs_review")])
    summary["ui_count"] = len([s for s in state["generated_scripts"] 
                               if s.get("framework") == "playwright" and s.get("validation_status") == "passed"])
    summary["api_count"] = len([s for s in state["generated_scripts"] 
                                if s.get("framework") == "pytest" and s.get("validation_status") == "passed"])
    
    return {"generated_scripts": state["generated_scripts"], "summary": summary}


def _ensure_conftest(script_dir: Path, framework: str, dry_run: bool):
    """在脚本输出目录生成 conftest.py(若不存在)"""
    conftest_path = script_dir / "conftest.py"
    if conftest_path.exists():
        return
    
    if dry_run:
        return
    
    # 从 Jinja2 模板生成
    from qoder.config.defaults import get_conftest_template
    template_content = get_conftest_template(framework)
    conftest_path.write_text(template_content, encoding="utf-8")


def _update_case_frontmatter(script: dict, dry_run: bool):
    """回写用例 Markdown 的 Frontmatter"""
    # 需要从 state 中找到对应的用例文件
    # 这里简化处理,实际实现中需要在 state 中维护 case -> script 的映射
    pass  # V1.0 MVP: 简化为注释,完整实现需在 State 中维护映射关系
