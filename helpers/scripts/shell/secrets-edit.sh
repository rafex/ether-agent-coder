#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
encrypted="$repo_root/.secrets/.llm-provider.enc.yml"
mkdir -p "$(dirname "$encrypted")"
export SOPS_AGE_KEY_FILE="${Xolotl_AGE_KEY_FILE:-${HOME}/.age/ether-agent-coder-key.txt}"
recipient="$($repo_root/helpers/scripts/shell/age-recipient.sh)"

if [[ ! -s "$encrypted" ]] || ! sops --age "$recipient" --decrypt "$encrypted" >/dev/null 2>&1; then
  tmp="$(mktemp)"
  trap 'rm -f "$tmp"' EXIT
  cat > "$tmp" <<'EOF'
llm_provider_openai_apikey: ""
llm_provider_openai_url: "https://api.openai.com/v1"
llm_provider_openai_model: ""
llm_provider_openai_model_level_razoner: ""
EOF
  sops --age "$recipient" --encrypt --filename-override "$encrypted" --encrypted-regex '^(data|stringData|.*(apikey|key|token|secret|password).*)$' "$tmp" > "$encrypted"
fi

set +e
SOPS_EDITOR="${SOPS_EDITOR:-vi}" sops --age "$recipient" edit "$encrypted"
edit_status=$?
set -e
[[ "$edit_status" -eq 0 || "$edit_status" -eq 200 ]] || exit "$edit_status"
chmod 600 "$encrypted"
