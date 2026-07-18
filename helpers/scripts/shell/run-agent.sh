#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
encrypted="$repo_root/.secrets/.llm-provider.enc.yml"
key_file="${Xolotl_AGE_KEY_FILE:-${HOME}/.age/ether-agent-coder-key.txt}"
[[ -f "$key_file" ]] || { printf 'Age key not found: %s\n' "$key_file" >&2; exit 1; }
[[ -f "$encrypted" ]] || { printf 'Encrypted provider config not found: %s\n' "$encrypted" >&2; exit 1; }

command=(uv run --project "$repo_root/xolotl/agent/python" python "$repo_root/xolotl/agent/python/src/main.py")
command+=("$@")
printf -v command_string '%q ' "${command[@]}"
SOPS_AGE_KEY_FILE="$key_file" sops exec-env "$encrypted" "$command_string"

