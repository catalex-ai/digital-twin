# Shared by setup.sh and bin/twin-mcp. Sourced, not run.
#
# Finds or makes the Python environment the Digital Twin's tools run in.
#
#   1. $package/.venv, if it already works (an older setup, or a developer's).
#   2. Otherwise ${TWIN_VENV:-~/.twin/venv}, made on first use.
#
# The default lives outside the package on purpose: a host that installs the
# package as a fresh copy on every update (CatalEx does) reuses the same
# environment instead of reinstalling. It is rebuilt only when requirements.txt
# changes. Everything prints to stderr, because the MCP servers own stdout.

twin_log() { printf '%s\n' "$*" >&2; }

twin_find_python() {
  for c in python3.13 python3.12 python3.11 python3; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>/dev/null; then
      command -v "$c"; return 0
    fi
  done
  return 1
}

twin_venv_ok() {
  [ -x "$1/bin/python" ] && cmp -s "$package/requirements.txt" "$1/.twin-requirements.txt" \
    && "$1/bin/python" -c 'import mcp, model2vec, yaml' 2>/dev/null
}

# Sets $twin_python to a working interpreter, installing the pinned packages if
# needed. Returns non-zero with a one-line reason on stderr.
twin_ensure_env() {
  if [ -x "$package/.venv/bin/python" ] && "$package/.venv/bin/python" -c 'import mcp, model2vec, yaml' 2>/dev/null; then
    twin_python="$package/.venv/bin/python"; return 0
  fi
  venv="${TWIN_VENV:-$HOME/.twin/venv}"
  case "$venv" in "~"*) venv="$HOME${venv#\~}";; esac
  if twin_venv_ok "$venv"; then
    twin_python="$venv/bin/python"; return 0
  fi
  py=$(twin_find_python) || {
    twin_log "The Digital Twin needs Python 3.11 or newer. Install it from https://www.python.org/downloads/."
    return 1
  }
  twin_log "Installing the Digital Twin's tools (one time, about a minute)..."
  if [ ! -x "$venv/bin/python" ]; then
    mkdir -p "$(dirname "$venv")" && "$py" -m venv "$venv" >&2 || {
      twin_log "Couldn't make a Python environment in $venv."; return 1; }
  fi
  "$venv/bin/python" -m pip install -q --disable-pip-version-check -r "$package/requirements.txt" >&2 || {
    twin_log "Couldn't install the Python packages. Check the internet connection and try again."; return 1; }
  cp "$package/requirements.txt" "$venv/.twin-requirements.txt"
  twin_python="$venv/bin/python"
}
