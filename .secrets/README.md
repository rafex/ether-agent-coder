# Xolotl secrets

`.llm-provider.enc.yml` is the only provider configuration committed to Git.
The plaintext `.llm-provider.yml` is generated locally and is ignored.

Prerequisites: `age`, `sops`, and an age key at
`~/.age/ether-agent-coder-key.txt` (or `Xolotl_AGE_KEY_FILE`).

Use `just secrets-edit` to open the encrypted file in `vi`; SOPS writes the
result back encrypted when `vi` exits.

