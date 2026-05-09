#!/usr/bin/env bash
# Wrapper minimal cho bash-guard.py.
# Toàn bộ logic pattern matching nằm trong file .py (Python regex flexible hơn
# bash glob/grep ERE, dễ test, không cần jq).
exec python "$HOME/.claude/hooks/bash-guard.py"
