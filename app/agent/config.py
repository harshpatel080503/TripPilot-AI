"""Runtime constants and MCP Server Configuration."""
import logging
import os
import pathlib
import platform
import shutil
from mcp import StdioServerParameters

_REPO_ROOT = pathlib.Path(__file__).parent.parent.parent

logger = logging.getLogger(__name__)

def _playwright_browsers_path() -> str:
    """Return the platform-correct Playwright browsers cache directory."""
    override = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if override:
        return override
    if platform.system() == "Darwin":
        return os.path.expanduser("~/Library/Caches/ms-playwright")
    return os.path.expanduser("~/.cache/ms-playwright")

MODEL: dict[str, str] = {
    "planner":    "gpt-oss:120b-cloud",
    "pricer":     "gpt-oss:120b-cloud",
    "budget":     "gpt-oss:120b-cloud",
    "aggregator": "gpt-oss:120b-cloud",
}

MAX_TOKENS: dict[str, int] = {
    "planner": 2048,
    "pricer": 3000,
    "budget": 2048,
    "aggregator": 3072,
}

MAX_TURNS: dict[str, int] = {
    "planner": 10,
    "pricer": 60,
    "budget": 60,
    "aggregator": 10,
}

ROLE_TOOL_SERVERS: dict[str, list[str]] = {
    "planner": [],
    "pricer": ["browser"],
    "budget": ["financial_quant"],
    "aggregator": [],
}

def _browser_mcp_params(playwright_config: str, base_env: dict) -> StdioServerParameters:
    args = ["--browser", "chromium", "--config", playwright_config, "--isolated"]
    if shutil.which("playwright-mcp"):
        logger.info("browser MCP: using global playwright-mcp binary")
        return StdioServerParameters(command="playwright-mcp", args=args, env=base_env)
    # npx fallback for local dev — pinned version avoids re-download on each run
    logger.info("browser MCP: playwright-mcp not found globally, falling back to npx")
    return StdioServerParameters(
        command="npx",
        args=["-y", "@playwright/mcp@0.0.83", *args],
        env=base_env,
    )


def build_mcp_server_configs() -> dict[str, StdioServerParameters]:
    playwright_config = str(_REPO_ROOT / "playwright-mcp.config.json")
    base_env = {
        **os.environ,
    }
    return {
        "financial_quant": StdioServerParameters(
            command="uvx",
            args=["calculator-mcp-server"],
            env=base_env,
        ),
        "browser": _browser_mcp_params(playwright_config, base_env),
    }