#!/bin/bash
# AI-Quality Platform CLI wrapper
export PYTHONPATH="/home/wuying_heshan/codespace/ai-quality/src:$PYTHONPATH"
exec python3 -m qoder.cli.app "$@"
