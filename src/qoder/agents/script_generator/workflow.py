# src/qoder/agents/script_generator/workflow.py

from typing import TypedDict, List, Optional, Any
from langgraph.graph import StateGraph, END

from qoder.agents.script_generator.nodes import (
    case_reader_node,
    framework_selector_node,
    script_generator_node,
    validator_node,
    case_updater_node,
)


class ScriptGenerationState(TypedDict):
    case_files: List[str]
    current_index: int
    parsed_cases: List[Any]  # List[ParsedCase]
    framework: str
    kb_context: str
    openapi_context: Optional[str]
    generated_scripts: List[Any]  # List[GeneratedScript]
    validation_results: List[dict]
    retry_count: int
    config: dict
    errors: List[str]
    summary: dict
    _prompts: dict  # 内部使用:Prompt 模板
    dry_run: bool


def route_after_validation(state: ScriptGenerationState) -> str:
    """条件路由:根据验证结果决定下一步"""
    if not state["validation_results"]:
        return "pass"
    
    latest = state["validation_results"][-1]
    if latest.get("status") == "passed":
        return "pass"
    elif state.get("retry_count", 0) < 3:
        return "retry"
    else:
        return "give_up"


def build_workflow(llm, kb_client):
    """构建并编译 LangGraph 工作流"""
    workflow = StateGraph(ScriptGenerationState)
    
    # 注册节点(注入 llm 和 kb_client)
    workflow.add_node("case_reader", case_reader_node)
    workflow.add_node("framework_selector", framework_selector_node)
    workflow.add_node("script_generator", lambda s: script_generator_node(s, llm))
    workflow.add_node("validator", validator_node)
    workflow.add_node("case_updater", case_updater_node)
    
    # 连接边
    workflow.set_entry_point("case_reader")
    workflow.add_edge("case_reader", "framework_selector")
    workflow.add_edge("framework_selector", "script_generator")
    workflow.add_edge("script_generator", "validator")
    
    workflow.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "pass": "case_updater",
            "retry": "script_generator",
            "give_up": "case_updater",
        }
    )
    workflow.add_edge("case_updater", END)
    
    return workflow.compile()
