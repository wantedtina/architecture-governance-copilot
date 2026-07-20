#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
PWCLI="$CODEX_HOME/skills/playwright/scripts/playwright_cli.sh"
SESSION="agc-video-draft"
RECORDING="$ROOT/video/recordings/architecture_governance_copilot_demo_source.webm"

"$PWCLI" -s="$SESSION" close >/dev/null 2>&1 || true
"$PWCLI" -s="$SESSION" open http://localhost:8501/
"$PWCLI" -s="$SESSION" resize 1920 1080
"$PWCLI" -s="$SESSION" video-start "$RECORDING" --size "1920x1080"
"$PWCLI" -s="$SESSION" run-code --filename "$ROOT/video/tools/record_demo.js"
"$PWCLI" -s="$SESSION" video-stop
"$PWCLI" -s="$SESSION" close

printf '%s\n' "$RECORDING"
