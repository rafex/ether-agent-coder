#!/usr/bin/env bash
set -euo pipefail

key_file="${Xolotl_AGE_KEY_FILE:-${HOME}/.age/ether-agent-coder-key.txt}"
if [[ ! -f "$key_file" ]]; then
  printf 'Age key not found: %s\n' "$key_file" >&2
  printf 'Set Xolotl_AGE_KEY_FILE or create the key at ~/.age/ether-agent-coder-key.txt.\n' >&2
  exit 1
fi

age-keygen -y "$key_file"

