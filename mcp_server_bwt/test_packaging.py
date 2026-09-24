import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_console_scripts_cover_both_names() -> None:
    """Regression for #24: uvx accepts both the dashed and the underscore executable."""
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["scripts"] == {
        "mcp-server-bwt": "mcp_server_bwt.main:app",
        "mcp_server_bwt": "mcp_server_bwt.main:app",
    }


def test_readme_json_snippets_parse_and_uvx_snippets_pass_the_key() -> None:
    """Regression for #24: README client configs are valid JSON and start the server."""
    readme = (ROOT / "README.md").read_text()
    snippets = re.findall(r"```json\n(.*?)```", readme, re.DOTALL)

    configs = [json.loads("{" + snippet + "}") for snippet in snippets]

    uvx_servers = [
        server
        for config in configs
        for servers in config.values()
        for server in servers.values()
        if server["command"] == "uvx"
    ]
    assert len(uvx_servers) == 2
    for server in uvx_servers:
        assert server["args"][-1] == "mcp-server-bwt"
        assert "BING_WEBMASTER_API_KEY" in server["env"]
