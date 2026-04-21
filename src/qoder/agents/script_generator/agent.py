# src/qoder/agents/script_generator/agent.py

from pathlib import Path
from typing import Any, Dict, List

from qoder.agents.base import BaseAgent
from qoder.agents.script_generator.workflow import build_workflow
from qoder.llm.provider import get_llm
from qoder.kb.retriever import KnowledgeRetriever


class ScriptGeneratorAgent(BaseAgent):
    """测试脚本生成 Agent"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.llm = get_llm(config.get("llm", {}))
        self.kb_client = KnowledgeRetriever(config.get("knowledge", {}))
        self.workflow = build_workflow(self.llm, self.kb_client)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行脚本生成工作流"""
        if not self.validate_input(context):
            return {
                "scripts": [],
                "summary": {"total": 0, "generated": 0, "skipped": 0,
                           "ui_count": 0, "api_count": 0, "errors": ["Invalid input"]},
                "status": "failed",
            }
        
        # 注入 Prompt 模板到 state
        context["_prompts"] = self.get_prompts()
        
        # LangGraph 同步调用(V1.0)
        result = self.workflow.invoke(context)
        
        return {
            "scripts": result.get("generated_scripts", []),
            "summary": result.get("summary", {}),
            "status": "partial" if result.get("errors") else "success",
        }
    
    def validate_input(self, context: Dict[str, Any]) -> bool:
        cases_path = Path(context.get("cases", ""))
        return cases_path.exists()
    
    def get_tools(self) -> List[Any]:
        from qoder.parsers.markdown_parser import MarkdownParser
        from qoder.validators.syntax_validator import SyntaxValidator
        return [MarkdownParser, SyntaxValidator]
    
    def get_prompts(self) -> Dict[str, str]:
        from qoder.agents.script_generator.prompts import (
            UI_SCRIPT_SYSTEM, API_SCRIPT_SYSTEM, SYNTAX_FIX,
        )
        return {
            "ui_script_system": UI_SCRIPT_SYSTEM,
            "api_script_system": API_SCRIPT_SYSTEM,
            "syntax_fix": SYNTAX_FIX,
        }
