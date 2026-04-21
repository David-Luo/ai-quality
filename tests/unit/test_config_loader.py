# tests/unit/test_config_loader.py

import pytest
import os
from pathlib import Path
from qoder.config.loader import load_config, _deep_merge
from qoder.config.defaults import DEFAULT_CONFIG


def test_load_default_config():
    """测试加载默认配置"""
    config = load_config("/tmp/nonexistent_project")
    
    assert "llm" in config
    assert config["llm"]["provider"] == "openai"
    assert config["llm"]["model"] == "gpt-4"


def test_environment_variable_override(monkeypatch):
    """测试环境变量覆盖"""
    monkeypatch.setenv("QODER_LLM_MODEL", "gpt-3.5-turbo")
    monkeypatch.setenv("QODER_LLM_PROVIDER", "openai")
    
    config = load_config("/tmp/nonexistent_project")
    
    assert config["llm"]["model"] == "gpt-3.5-turbo"
    assert config["llm"]["provider"] == "openai"


def test_deep_merge():
    """测试深度合并"""
    base = {
        "llm": {
            "provider": "openai",
            "model": "gpt-4",
        },
        "test": {
            "case_dir": "tests/cases",
        }
    }
    
    override = {
        "llm": {
            "model": "gpt-3.5-turbo",
            "temperature": 0.5,
        }
    }
    
    result = _deep_merge(base, override)
    
    assert result["llm"]["provider"] == "openai"  # 保留
    assert result["llm"]["model"] == "gpt-3.5-turbo"  # 覆盖
    assert result["llm"]["temperature"] == 0.5  # 新增
    assert result["test"]["case_dir"] == "tests/cases"  # 未变
