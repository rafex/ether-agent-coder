set shell := ["bash", "-euo", "pipefail", "-c"]

secrets-edit:
    ./helpers/scripts/shell/secrets-edit.sh

secrets-decrypt:
    ./helpers/scripts/shell/secrets-decrypt.sh

secrets-encrypt:
    ./helpers/scripts/shell/secrets-encrypt.sh

secrets-check:
    ./helpers/scripts/shell/secrets-check.sh

hooks-install:
    ./helpers/scripts/shell/install-hooks.sh

