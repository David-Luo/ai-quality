# src/qoder/cli/config_commands.py

import typer
from pathlib import Path

app = typer.Typer(help="Configuration management")

@app.command()
def show():
    """Show current configuration"""
    from qoder.config.loader import load_config
    
    config = load_config()
    print("Current Configuration:")
    for section, values in config.items():
        print(f"\n[{section}]")
        if isinstance(values, dict):
            for key, value in values.items():
                print(f"  {key} = {value}")
        else:
            print(f"  {values}")

@app.command()
def init(
    project_dir: Path = typer.Argument(".", help="Project directory")
):
    """Initialize default configuration file"""
    from qoder.config.defaults import DEFAULT_CONFIG
    import tomli_w
    
    config_path = project_dir / "tests" / ".qoder" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "wb") as f:
        tomli_w.dump(DEFAULT_CONFIG, f)
    
    print(f"Configuration file created: {config_path}")
