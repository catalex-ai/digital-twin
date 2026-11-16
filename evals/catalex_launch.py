"""Launch an agent folder the way CatalEx does with folder isolation (RFC018 S8 in catalex-relay).

CatalEx starts Claude Code with no settings source, only the folder's .mcp.json, the folder's settings
merged into one --settings document, and the folder's CLAUDE.md (one level of @file imports inlined)
appended to the system prompt under its identity header. Skills in .claude/skills are NOT loaded that
way, so an agent must @import its skill. The agent's tools are its MCP servers plus ToolSearch (MCP
tools may be deferred). Relay's own tools and guidance are left out: no relay server runs here.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HEADER = ("# Your instructions\n\n"
          "The instructions below are your own, from your agent folder. They define who "
          "you are, your role, your tone and your limits, and they take precedence over "
          "any generic description of you as an AI or coding assistant. When someone "
          "asks who you are or what you can do, answer as the role they describe and "
          "name only what they allow. People reach you through CatalEx chats.\n\n")


def instructions(folder: Path) -> str:
    out = []
    for line in (folder / "CLAUDE.md").read_text(encoding="utf-8").splitlines():
        m = re.fullmatch(r"\s*@(\S+)\s*", line)
        p = folder / m.group(1) if m else None
        if p and p.is_file() and folder in p.resolve().parents:
            out.append(p.read_text(encoding="utf-8").rstrip("\n"))
        else:
            out.append(line)
    return HEADER + "\n".join(out).strip() + "\n"


def argv(folder: Path, model: str, effort: str = "", approval: str = "deny") -> list[str]:
    folder = Path(folder)
    servers = list(json.loads((folder / ".mcp.json").read_text())["mcpServers"])
    settings = folder / ".claude" / "settings.json"
    cmd = ["claude", "-p", "--model", model, "--setting-sources", "", "--strict-mcp-config",
           "--mcp-config", str(folder / ".mcp.json"), "--tools", "",
           "--append-system-prompt", instructions(folder),
           "--permission-mode", "dontAsk" if approval == "deny" else "bypassPermissions",
           "--allowedTools", "ToolSearch", "--allowedTools", ",".join(f"mcp__{s}__*" for s in servers)]
    if settings.exists():
        cmd += ["--settings", settings.read_text()]
    if effort:
        cmd += ["--effort", effort]
    return cmd
