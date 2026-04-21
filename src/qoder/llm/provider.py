# src/qoder/llm/provider.py

from typing import Any


def get_llm(config: dict) -> Any:
    """根据配置创建 LLM 实例"""
    provider = config.get("provider", "openai")
    
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.get("model", "gpt-4"),
            temperature=config.get("temperature", 0.2),
            max_tokens=config.get("max_tokens", 4096),
        )
    elif provider == "ollama":
        from langchain_community.llms import Ollama
        return Ollama(
            model=config.get("model", "llama3"),
            base_url=config.get("base_url", "http://localhost:11434"),
        )
    elif provider == "qwen":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.get("model", "qwen-max"),
            api_key=config.get("api_key"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=config.get("temperature", 0.2),
        )
    elif provider == "azure":
        from langchain_openai import AzureChatOpenAI
        return AzureChatOpenAI(
            azure_deployment=config.get("model"),
            temperature=config.get("temperature", 0.2),
        )
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
