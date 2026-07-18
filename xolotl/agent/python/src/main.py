"""OpenAI-compatible entry point for Xolotl's programming assistant."""
from __future__ import annotations

import os


AGENT_ROLE = "programming-support"
PROGRAMMING_CAPABILITIES = (
    "understand repository",
    "plan implementation",
    "write and refactor code",
    "debug failures",
    "run tests",
    "review changes",
    "document decisions",
)


def provider_config() -> dict[str, str]:
    return {
        "api_key": os.environ.get("llm_provider_openai_apikey", ""),
        "base_url": os.environ.get("llm_provider_openai_url", "https://api.openai.com/v1"),
        "model": os.environ.get("llm_provider_openai_model", ""),
        "reasoner_level": os.environ.get("llm_provider_openai_model_level_razoner", ""),
    }


def main() -> None:
    config = {k: ("***" if k == "api_key" and v else v) for k, v in provider_config().items()}
    print({"role": AGENT_ROLE, "capabilities": PROGRAMMING_CAPABILITIES, "provider": config})


if __name__ == "__main__":
    main()
