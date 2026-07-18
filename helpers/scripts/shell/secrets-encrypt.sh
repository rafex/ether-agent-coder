#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
plain="$repo_root/.secrets/.llm-provider.yml"
encrypted="$repo_root/.secrets/.llm-provider.enc.yml"
[[ -f "$plain" ]] || { printf 'Missing plaintext file: %s\n' "$plain" >&2; exit 1; }
export SOPS_AGE_KEY_FILE="${Xolotl_AGE_KEY_FILE:-${HOME}/.age/ether-agent-coder-key.txt}"
recipient="$($repo_root/helpers/scripts/shell/age-recipient.sh)"
sops --age "$recipient" --encrypt --filename-override "$encrypted" --encrypted-regex '^(data|stringData|.*(apikey|key|token|secret|password).*)$' "$plain" > "$encrypted"
chmod 600 "$encrypted"
rm -f "$plain"
printf 'Encrypted provider configuration and removed plaintext.\n'
