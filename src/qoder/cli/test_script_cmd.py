# src/qoder/cli/test_script_cmd.py

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from qoder.agents.script_generator import ScriptGeneratorAgent

console = Console()

app = typer.Typer(help="Generate test scripts from Markdown test cases")

@app.callback()
def callback():
    """测试脚本生成命令组"""
    pass

@app.command()
def generate(
    cases: Path = typer.Argument(
        ...,
        help="Input: test case directory or single .md file",
        exists=True,
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        help="Script output directory (default: tests/scripts/<module>/)",
    ),
    framework: Optional[str] = typer.Option(
        None,
        "--framework",
        help="Framework override: playwright | pytest",
    ),
    env: Optional[str] = typer.Option(
        None,
        "--env",
        help="Target environment name",
    ),
    spec: Optional[Path] = typer.Option(
        None,
        "--spec",
        help="OpenAPI spec file (optional, for API tests)",
    ),
    no_interactive: bool = typer.Option(
        False,
        "--no-interactive",
        help="Non-interactive mode (for CI/CD)",
    ),
    with_kb: bool = typer.Option(
        True,
        "--with-kb/--no-kb",
        help="Enable knowledge base context",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview only, do not write files",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Show detailed LLM and KB logs",
    ),
):
    """Generate test scripts from Markdown test cases."""
    
    # 1. 构建 Agent 上下文
    context = {
        "cases": str(cases),
        "output_dir": str(output_dir) if output_dir else None,
        "framework": framework,
        "env": env,
        "spec": str(spec) if spec else None,
        "interactive": not no_interactive,
        "with_kb": with_kb,
        "dry_run": dry_run,
        "verbose": verbose,
    }
    
    # 2. 加载配置
    from qoder.config import load_config
    config = load_config()
    context["config"] = config
    
    # 如果 CLI 指定了 framework,传递到 config
    if framework:
        context["config"]["_cli_framework"] = framework
    
    # 3. 创建并执行 Agent
    agent = ScriptGeneratorAgent(config["script_generator"])
    result = agent.execute(context)  # 同步调用(V1.0)
    
    # 4. 输出结果
    _display_result(result, dry_run)
    
    # 5. 设置退出码
    if result.status == "failed":
        raise typer.Exit(2)
    elif result.status == "partial":
        raise typer.Exit(1)


def _display_result(result, dry_run: bool):
    """格式化输出生成结果"""
    console.print()
    console.print(f"{'─' * 50}")
    console.print(f"总计: {result.summary.total} │ 生成: {result.summary.generated} │ 跳过: {result.summary.skipped}")
    console.print(f"UI 脚本: {result.summary.ui_count} │ API 脚本: {result.summary.api_count}")
    
    if dry_run:
        console.print("[yellow]Dry run - 文件未写入[/yellow]")
    else:
        console.print(f"输出目录: tests/scripts/")
    
    if result.summary.errors:
        console.print()
        console.print("[red]错误:[/red]")
        for err in result.summary.errors:
            console.print(f"  - {err}")
    
    console.print()
    console.print("提示: 运行 'qoder test run --suite tests/scripts/' 执行生成的脚本。")
