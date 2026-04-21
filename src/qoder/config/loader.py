# src/qoder/config/loader.py

import os
import sys
from pathlib import Path

# Python 3.11+ 使用 tomllib, 3.10 使用 tomli
if sys.version_info >= (3, 11):
    import tomllib as tomli
else:
    import tomli

from qoder.config.defaults import DEFAULT_CONFIG


def load_config(project_dir: str = ".") -> dict:
    """加载项目配置"""
    config_path = Path(project_dir) / "tests" / ".qoder" / "config.toml"
    
    config = DEFAULT_CONFIG.copy()
    
    if config_path.exists():
        with open(config_path, "rb") as f:
            file_config = tomli.load(f)
        _deep_merge(config, file_config)
    
    # 注入环境变量覆盖
    if os.environ.get("QODER_LLM_MODEL"):
        config.setdefault("llm", {})["model"] = os.environ["QODER_LLM_MODEL"]
    if os.environ.get("QODER_LLM_PROVIDER"):
        config.setdefault("llm", {})["provider"] = os.environ["QODER_LLM_PROVIDER"]
    
    return config


def _deep_merge(base: dict, override: dict) -> dict:
    """深度合并字典"""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base
