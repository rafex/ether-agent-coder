"""CLI entry point for Xolotl's programming assistant."""
from __future__ import annotations

import sys

from agent import AGENT_ROLE, PROGRAMMING_CAPABILITIES, build_agent, provider_config

def main() -> None:
    if "--info" in sys.argv:
        config = {k: ("***" if k == "api_key" and v else v) for k, v in provider_config().items()}
        print({"role": AGENT_ROLE, "capabilities": PROGRAMMING_CAPABILITIES, "provider": config})
        return
    task = " ".join(argument for argument in sys.argv[1:] if argument != "--info").strip()
    if not task:
        task = input("xolotl> ").strip()
    if not task:
        raise SystemExit("provide a programming task")
    result = build_agent().run(task)
    print(result)


if __name__ == "__main__":
    main()
