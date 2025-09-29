#!/usr/bin/env bash
set -euo pipefail

# Paths (edit these)
VENV_PY="/Users/gary/Documents/Personal/flat-search/.venv/bin/python3"
SCRIPT="/Users/gary/Documents/Personal/flat-search/src/main.py"
LOGDIR="/Users/gary/Documents/Personal/flat-search/logs"

mkdir -p "$LOGDIR"

TIMESTAMP=$(date +%Y-%m-%d_%H-%M)
LOGFILE="$LOGDIR/log_${TIMESTAMP}.log"

echo "---- $(date '+%Y-%m-%d %H:%M:%S') ----" >> "$LOGFILE"
"$VENV_PY" "$SCRIPT" >> "$LOGFILE" 2>&1