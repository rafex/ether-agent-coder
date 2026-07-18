#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
Xolotl_SMOKE=1 uv run --no-project python helpers/scripts/python/check_runtime.py
uv run --project xolotl/agent/python python xolotl/agent/python/src/main.py --info
uv run --project xolotl/agent/python python smoke-test/check_agent.py
./helpers/scripts/shell/secrets-check.sh
printf 'Xolotl smoke test passed.\n'
