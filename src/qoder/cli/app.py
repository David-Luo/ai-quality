# src/qoder/cli/app.py

import typer
from qoder.cli import test_commands, config_commands

app = typer.Typer(
    name="aq",
    help="AI-Quality Test Platform CLI",
    add_completion=False,
)

app.add_typer(test_commands.app, name="test")
app.add_typer(config_commands.app, name="config")
# app.add_typer(bug_commands.app, name="bug")        # V1.0 后续实现
# app.add_typer(kb_commands.app, name="kb")          # V1.0 后续实现
# app.add_typer(sync_commands.app, name="sync")      # V1.0 后续实现

def main():
    app()
