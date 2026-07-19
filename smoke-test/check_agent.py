"""Offline checks for the programming-agent tool boundary."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "xolotl/agent/python/src"))

import fastapi  # noqa: E402,F401
import litellm  # noqa: E402,F401
import orjson  # noqa: E402,F401

from agent import _litellm_model_id, environment_info, list_files, read_file, run_command, write_report  # noqa: E402


def main() -> None:
    assert "xolotl/agent/python/src/agent.py" in list_files.forward("xolotl/agent/python/src")
    assert "os=" in environment_info.forward()
    assert "ether-agent-coder" in read_file.forward("README.md", 1, 1)
    assert run_command.forward("python --version").startswith("exit=0")
    assert _litellm_model_id("openai/gpt-oss-120b") == "openai/openai/gpt-oss-120b"
    report = Path(tempfile.gettempdir()) / "xolotl-smoke-report.md"
    try:
        assert "wrote report" in write_report.forward(str(report), "# smoke\n")
        assert report.read_text(encoding="utf-8") == "# smoke\n"
    finally:
        report.unlink(missing_ok=True)
    try:
        read_file.forward(".secrets/.llm-provider.enc.yml")
    except ValueError:
        pass
    else:
        raise AssertionError("secret access must be rejected")
    print("agent tool boundary checks passed")


if __name__ == "__main__":
    main()
