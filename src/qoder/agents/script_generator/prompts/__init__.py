"""Prompt templates"""

from pathlib import Path

# 加载 Prompt 模板
_prompts_dir = Path(__file__).parent

def _load_prompt(filename: str) -> str:
    """加载 Prompt 模板文件"""
    filepath = _prompts_dir / filename
    return filepath.read_text(encoding='utf-8')

# 导出 Prompt 常量
UI_SCRIPT_SYSTEM = _load_prompt("ui_script_system.txt")
API_SCRIPT_SYSTEM = _load_prompt("api_script_system.txt")
SYNTAX_FIX = _load_prompt("syntax_fix.txt")
