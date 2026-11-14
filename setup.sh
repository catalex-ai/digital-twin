#!/bin/sh
# Set up the Digital Twin on this computer. Safe to run again.
#
#   ./setup.sh                      # brain in ~/.twin/brain
#   TWIN_HOME=~/my-brain ./setup.sh # brain somewhere else
#
# Optional: the agents also set themselves up on their first start (see
# bin/twin-mcp). Running this first just does the one-time install up front
# and checks that everything works.
#
# It adds no restrictions: run `claude` inside manager-agent/ or twin-agent/
# and each loads its own MCP server, with that server's tools pre-approved.
# Whatever runs the agents (for example CatalEx) decides which tools they may
# use.
#
# Everything stays local: a Python environment in ~/.twin/venv (or TWIN_VENV),
# and the brain folder. The only download is the pinned Python packages and a
# small search model (about 30 MB), once.
set -eu

package=$(cd -P "$(dirname "$0")" && pwd)
. "$package/bin/env.sh"
brain="${TWIN_HOME:-$HOME/.twin/brain}"
cd "$package"

say() { printf '%s\n' "$*"; }
fail() { printf '%s\n' "$*" >&2; exit 1; }

# 1. Python 3.11+ and the pinned packages.
twin_ensure_env || fail "Then run ./setup.sh again."

# 2. Search model, fetched once and cached.
"$twin_python" -c '
import os
from model2vec import StaticModel
StaticModel.from_pretrained(os.environ.get("TWIN_EMBED_MODEL", "minishlab/potion-base-8M"))
' >/dev/null 2>&1 || say "Note: the search model didn't download. Search still works by keywords, and the model is fetched the next time it is needed."

# 3. The brain. Never inside this folder.
case "$brain" in "$package"*) fail "Keep the brain outside the package folder. Set TWIN_HOME to another folder.";; esac
TWIN_HOME="$brain" PYTHONPATH="$package" "$twin_python" -m brainkit.cli init >/dev/null
TWIN_HOME="$brain" PYTHONPATH="$package" "$twin_python" -m brainkit.cli status >/dev/null \
  || fail "The brain didn't start. Run ./setup.sh again; if it keeps failing, open an issue."

# 4. Claude Code.
if ! command -v claude >/dev/null 2>&1; then
  say "Ready, except Claude Code isn't installed. Install it from https://claude.com/claude-code."
  exit 0
fi

say "Digital Twin is ready. Your brain is in $brain."
say "  cd $package/manager-agent && claude   the Twin Manager (you): add your CV, answer questions, fix mistakes"
say "  cd $package/twin-agent && claude      the Twin (other people): answers as you from what you allowed"
say "Each folder loads its own tools. Use the same TWIN_HOME if you changed it."
