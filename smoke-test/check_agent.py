"""Offline checks for the programming-agent tool boundary."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "xolotl/agent/python/src"))

from agent import list_files, read_file, run_command  # noqa: E402


def main() -> None:
    assert "xolotl/agent/python/src/agent.py" in list_files.forward("xolotl/agent/python/src")
    assert "ether-agent-coder" in read_file.forward("README.md", 1, 1)
    assert run_command.forward("python --version").startswith("exit=0")
    try:
        read_file.forward(".secrets/.llm-provider.enc.yml")
    except ValueError:
        pass
    else:
        raise AssertionError("secret access must be rejected")
    print("agent tool boundary checks passed")


if __name__ == "__main__":
    main()

