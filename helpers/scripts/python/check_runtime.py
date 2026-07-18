"""Minimal runtime checks used by the smoke test."""
from __future__ import annotations

import os
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    encrypted = root / ".secrets" / ".llm-provider.enc.yml"
    assert encrypted.exists(), encrypted
    assert not (root / ".secrets" / ".llm-provider.yml").exists()
    assert os.environ.get("Xolotl_SMOKE", "1") == "1"
    print("python runtime checks passed")


if __name__ == "__main__":
    main()

