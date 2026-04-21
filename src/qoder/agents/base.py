# src/qoder/agents/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseAgent(ABC):
    """Qoder Agent 基类(与 Agent扩展机制设计 §2.2 一致)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", self.__class__.__name__)
        self.version = config.get("version", "1.0.0")
        self.description = config.get("description", "")
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行 Agent
        
        Args:
            context: 执行上下文
            
        Returns:
            执行结果
        """
        pass
    
    @abstractmethod
    def validate_input(self, context: Dict[str, Any]) -> bool:
        """验证输入数据"""
        pass
    
    def get_tools(self) -> List[Any]:
        """获取 Agent 可用的工具列表"""
        return []
    
    def get_prompts(self) -> Dict[str, str]:
        """获取 Prompt 模板"""
        return {}
