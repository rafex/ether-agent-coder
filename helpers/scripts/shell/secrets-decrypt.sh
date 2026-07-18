#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
encrypted="$repo_root/.secrets/.llm-provider.enc.yml"
plain="$repo_root/.secrets/.llm-provider.yml"
export SOPS_AGE_KEY_FILE="${Xolotl_AGE_KEY_FILE:-${HOME}/.age/ether-agent-coder-key.txt}"
recipient="$($repo_root/helpers/scripts/shell/age-recipient.sh)"
sops --age "$recipient" --decrypt "$encrypted" > "$plain"
chmod 600 "$plain"
printf 'Materialized %s (ignored by Git).\n' "$plain"
