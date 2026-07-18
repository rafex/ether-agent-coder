#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
Xolotl_SMOKE=1 uv run --no-project python helpers/scripts/python/check_runtime.py
./helpers/scripts/shell/secrets-check.sh
printf 'Xolotl smoke test passed.\n'

