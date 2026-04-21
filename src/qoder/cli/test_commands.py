# src/qoder/cli/test_commands.py

import typer
from qoder.cli import test_script_cmd

app = typer.Typer(help="Test management commands")

app.add_typer(test_script_cmd.app, name="script")
# app.add_typer(test_run_cmd.app, name="run")      # M5 执行引擎
# app.add_typer(test_plan_cmd.app, name="plan")    # M1 测试计划
# app.add_typer(test_generate_cmd.app, name="generate")  # M1 用例生成
