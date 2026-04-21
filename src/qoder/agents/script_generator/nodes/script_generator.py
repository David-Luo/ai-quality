# src/qoder/agents/script_generator/nodes/script_generator.py

import re
from datetime import datetime, timezone


def script_generator_node(state: dict, llm) -> dict:
    """使用 LLM 为每个用例生成 Python 脚本"""
    generated_scripts = state.get("generated_scripts", [])
    errors = state.get("errors", [])
    
    for case in state["parsed_cases"]:
        framework = getattr(case, "_framework", "playwright")
        
        # 构建 Prompt
        if framework == "playwright":
            system_prompt = state.get("_prompts", {}).get("ui_script_system", "")
        else:
            system_prompt = state.get("_prompts", {}).get("api_script_system", "")
        
        user_prompt = _build_user_prompt(case, state, framework)
        
        # 调用 LLM
        try:
            response = llm.invoke([
                ("system", system_prompt),
                ("human", user_prompt),
            ])
            code = _extract_python_code(response.content)
        except Exception as e:
            errors.append(f"LLM failed for {case.id}: {e}")
            continue
        
        # 构建输出路径
        output_path = _build_output_path(case, framework, state)
        
        generated_scripts.append({
            "case_id": case.id,
            "framework": framework,
            "code": code,
            "output_path": output_path,
            "validation_status": "pending",
            "validation_errors": [],
        })
    
    return {
        "generated_scripts": generated_scripts,
        "errors": errors,
    }


def _extract_python_code(text: str) -> str:
    """从 LLM 响应中提取 Python 代码"""
    # 去除 Markdown 代码围栏
    pattern = r'```python\s*\n(.*?)\n```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    # 如果没有代码围栏,尝试提取所有代码
    pattern = r'```\s*\n(.*?)\n```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    return text.strip()


def _build_user_prompt(case, state: dict, framework: str) -> str:
    """构建用户消息模板"""
    steps_text = "\n".join(
        f"  Step {s.step_number}: {s.action} → {s.expected_result}"
        for s in case.steps
    )
    test_data_text = "\n".join(f"  {k}: {v}" for k, v in case.test_data.items())
    
    return f"""
根据以下测试用例生成 {framework} Python 测试脚本。

测试用例:
- ID: {case.id}
- 标题: {case.title}
- 模块: {case.module}
- 前提条件: {', '.join(case.preconditions) if case.preconditions else '无'}
- 测试步骤:
{steps_text}
- 输入数据:
{test_data_text}

只输出 Python 代码,不添加任何解释。
"""


def _build_output_path(case, framework: str, state: dict) -> str:
    """构建脚本输出路径"""
    if framework == "playwright":
        base = "tests/scripts/ui"
        return f"{base}/test_{case.module.lower().replace('/', '_')}_{case.id.lower()}.py"
    else:
        base = "tests/scripts/api"
        return f"{base}/test_{case.module.lower().replace('/', '_')}_{case.id.lower()}.py"
