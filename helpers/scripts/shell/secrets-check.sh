#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"
[[ -f .secrets/.llm-provider.enc.yml ]] || { printf 'Missing encrypted provider configuration.\n' >&2; exit 1; }
[[ ! -e .secrets/.llm-provider.yml ]] || { printf 'Plaintext secret exists: .secrets/.llm-provider.yml\n' >&2; exit 1; }

staged="$(git diff --cached --name-only --diff-filter=ACMR || true)"
while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  case "$file" in
    .secrets/.llm-provider.enc.yml|.secrets/README.md|.secrets/.gitignore) continue ;;
    .secrets/*|.env|.env.*|*.pem|*.key|*id_rsa*)
      printf 'Refusing sensitive staged file: %s\n' "$file" >&2; exit 1 ;;
  esac
  # This checker necessarily contains the key-name pattern it is looking for.
  [[ "$file" == "helpers/scripts/shell/secrets-check.sh" ]] && continue
  if git show ":$file" 2>/dev/null | grep -Eq 'BEGIN (RSA|OPENSSH|EC|PRIVATE) KEY|sk-[A-Za-z0-9]{20,}'; then
    printf 'Refusing plaintext credential material in: %s\n' "$file" >&2
    exit 1
  fi
  if git show ":$file" 2>/dev/null | awk '/llm_provider_openai_apikey:/ && $0 !~ /ENC\[/ && $0 !~ /:[[:space:]]*""[[:space:]]*$/ { found=1 } END { exit found ? 0 : 1 }'; then
    printf 'Refusing unencrypted OpenAI provider key in: %s\n' "$file" >&2
    exit 1
  fi
done <<< "$staged"

printf 'Secret checks passed.\n'
