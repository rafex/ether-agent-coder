"""The first usable Xolotl programming assistant runtime."""
from __future__ import annotations

import os
import platform
import shlex
import shutil
import subprocess
from pathlib import Path

from smolagents import LiteLLMModel, ToolCallingAgent, tool


REPO_ROOT = Path(os.environ.get("Xolotl_REPO_ROOT", Path.cwd())).resolve()
BLOCKED_PARTS = {".git", ".secrets", ".venv", "__pycache__", ".pytest_cache", "node_modules", "target"}
BLOCKED_NAMES = {".env", ".env.local", ".llm-provider.yml"}
POSIX_COMMANDS = {
    "bash", "cargo", "find", "git", "gradle", "java", "just", "make", "mvn",
    "node", "npm", "python", "pytest", "rg", "rustc", "sed", "uv",
}
WINDOWS_COMMANDS = {
    "cargo", "git", "gradle", "java", "just", "mvn", "node", "npm", "python",
    "pytest", "pwsh", "powershell", "rg", "rustc", "uv",
}
FORBIDDEN_COMMAND_TEXT = ("git push", "git reset", "git clean", "rm -rf", "sudo ")
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


def _safe_path(relative_path: str) -> Path:
    path = (REPO_ROOT / relative_path).resolve()
    if path != REPO_ROOT and REPO_ROOT not in path.parents:
        raise ValueError("path must remain inside the repository")
    if any(part in BLOCKED_PARTS for part in path.relative_to(REPO_ROOT).parts):
        raise ValueError("access to Git metadata and secrets is disabled")
    if path.name in BLOCKED_NAMES or path.name.startswith(".env."):
        raise ValueError("access to secret files is disabled")
    return path


def _allowed_commands() -> set[str]:
    commands = WINDOWS_COMMANDS if platform.system() == "Windows" else POSIX_COMMANDS
    return {command for command in commands if shutil.which(command)}


@tool
def environment_info() -> str:
    """Describe the host environment and available development commands.

    Returns:
        Operating system, architecture, Python runtime, shell and available
        allowlisted executables. Use this before choosing platform-specific commands.
    """
    shell_name = "ComSpec" if platform.system() == "Windows" else "SHELL"
    shell = os.environ.get(shell_name, "unknown")
    available = ", ".join(sorted(_allowed_commands())) or "none"
    return (
        f"os={platform.system()}\n"
        f"release={platform.release()}\n"
        f"architecture={platform.machine()}\n"
        f"python={platform.python_version()}\n"
        f"shell={shell}\n"
        f"repo_root={REPO_ROOT}\n"
        f"available_commands={available}"
    )


@tool
def list_files(path: str = ".") -> str:
    """List source files in a repository directory.

    Args:
        path: Repository-relative directory to inspect.

    Returns:
        A newline-separated list of up to 200 repository-relative file paths.
    """
    directory = _safe_path(path)
    if not directory.is_dir():
        raise ValueError(f"not a directory: {path}")
    files: list[str] = []
    for item in sorted(directory.rglob("*")):
        if not item.is_file():
            continue
        try:
            relative = item.relative_to(REPO_ROOT)
            if any(part in BLOCKED_PARTS for part in relative.parts):
                continue
            files.append(relative.as_posix())
        except ValueError:
            continue
        if len(files) >= 200:
            break
    return "\n".join(files) or "(no files found)"


@tool
def read_file(path: str, start_line: int = 1, end_line: int = 240) -> str:
    """Read a bounded range of a repository text file.

    Args:
        path: Repository-relative file path.
        start_line: First 1-based line to return.
        end_line: Last line to return, capped at 240 lines.

    Returns:
        The requested source lines with line numbers.
    """
    file_path = _safe_path(path)
    if not file_path.is_file():
        raise ValueError(f"not a file: {path}")
    if start_line < 1 or end_line < start_line:
        raise ValueError("invalid line range")
    end_line = min(end_line, start_line + 239)
    lines = file_path.read_text(encoding="utf-8").splitlines()
    return "\n".join(f"{number}: {lines[number - 1]}" for number in range(start_line, min(end_line, len(lines)) + 1))


@tool
def search_code(pattern: str, path: str = ".") -> str:
    """Search repository source text with ripgrep.

    Args:
        pattern: Literal or regular-expression pattern to search for.
        path: Repository-relative directory to search.

    Returns:
        Matching file paths and line snippets.
    """
    directory = _safe_path(path)
    result = subprocess.run(
        [
            "rg", "--line-number", "--hidden", "--glob", "!.git", "--glob", "!.secrets",
            "--glob", "!.venv", "--glob", "!__pycache__", "--glob", "!node_modules", "--glob", "!target",
            pattern, str(directory),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip() or "search failed")
    return result.stdout[-12000:] or "(no matches)"


@tool
def write_file(path: str, content: str) -> str:
    """Create or replace a repository source file.

    Args:
        path: Repository-relative destination path.
        content: Complete UTF-8 file content.

    Returns:
        Confirmation with the written path and byte count.
    """
    file_path = _safe_path(path)
    if len(content.encode("utf-8")) > 200_000:
        raise ValueError("refusing files larger than 200 KiB")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"wrote {file_path.relative_to(REPO_ROOT)} ({len(content.encode('utf-8'))} bytes)"


@tool
def run_command(command: str, timeout_seconds: int = 60) -> str:
    """Run one safe, non-destructive development command in the repository.

    Args:
        command: One command without shell pipelines, redirects, or chained commands.
        timeout_seconds: Maximum runtime, capped at 120 seconds.

    Returns:
        Combined command output and exit status.
    """
    if any(token in command for token in (";", "|", ">", "<", "&&", "||", "`", "$(")):
        raise ValueError("shell chaining, redirects and substitutions are disabled")
    if any(fragment in command for fragment in FORBIDDEN_COMMAND_TEXT):
        raise ValueError("destructive or remote-write commands are disabled")
    argv = shlex.split(command)
    allowed_commands = _allowed_commands()
    if not argv or argv[0] not in allowed_commands:
        raise ValueError(f"command is not allowlisted: {argv[0] if argv else '(empty)'}")
    completed = subprocess.run(
        argv,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=min(max(timeout_seconds, 1), 120),
        check=False,
    )
    output = (completed.stdout + completed.stderr).strip()
    return f"exit={completed.returncode}\n{output[-12000:]}"


SYSTEM_INSTRUCTIONS = """You are Xolotl, a programming-support agent working inside a repository.
Help the user understand, plan, implement, debug, test, review, and document software changes.
Call environment_info before choosing commands so you respect the host OS, shell, architecture,
and installed executables. Use repository tools before making assumptions. Read relevant files
first, make focused changes, then run proportional checks. Never access secrets, .git, or
environment files. Never push, reset, clean, or perform destructive operations. Explain what
changed and what was verified."""


def build_agent() -> ToolCallingAgent:
    config = provider_config()
    if not config["api_key"]:
        raise RuntimeError("llm_provider_openai_apikey is missing")
    if not config["model"]:
        raise RuntimeError("llm_provider_openai_model is missing")
    # LiteLLM consumes the first `openai/` segment as its transport provider.
    # Prefixing once unconditionally preserves provider model IDs such as
    # Groq's `openai/gpt-oss-120b` in the outgoing OpenAI-compatible request.
    model_id = _litellm_model_id(config["model"])
    model_kwargs = {}
    # Groq rejects `required` when the model can answer without a tool call.
    # `auto` still enables tool use when the task needs repository inspection.
    model_kwargs["tool_choice"] = "auto"
    if config["reasoner_level"]:
        model_kwargs["reasoning_effort"] = config["reasoner_level"]
    model = LiteLLMModel(
        model_id=model_id,
        api_base=config["base_url"],
        api_key=config["api_key"],
        flatten_messages_as_text=True,
        **model_kwargs,
    )
    return ToolCallingAgent(
        tools=[environment_info, list_files, read_file, search_code, write_file, run_command],
        model=model,
        instructions=SYSTEM_INSTRUCTIONS,
        max_tool_threads=1,
    )


def provider_config() -> dict[str, str]:
    return {
        "api_key": os.environ.get("llm_provider_openai_apikey", ""),
        "base_url": os.environ.get("llm_provider_openai_url", "https://api.openai.com/v1"),
        "model": os.environ.get("llm_provider_openai_model", ""),
        "reasoner_level": os.environ.get("llm_provider_openai_model_level_razoner", ""),
    }


def _litellm_model_id(model_name: str) -> str:
    """Map the configured model name to LiteLLM's OpenAI transport form."""
    return f"openai/{model_name}"
