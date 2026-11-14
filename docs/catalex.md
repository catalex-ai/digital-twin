# The Digital Twin on CatalEx

This repo is ready for the CatalEx Marketplace. [`catalex.yaml`](../catalex.yaml)
at the root declares both agents, so one Import sets up the Twin Manager and
the Twin with working settings. Nothing else is needed: no setup step, no
credentials.

## What Import sets up

CatalEx clones the repo at one exact commit into `~/catalex/digital-twin` and
registers two ordinary agents. It never runs anything from the repo during the
import.

| | Twin Manager | Twin |
|---|---|---|
| Who talks to it | you, the owner | other people, in your channels |
| Folder | `manager-agent` | `twin-agent` |
| Provider and model | Claude, `haiku` | Claude, `haiku` |
| Effort | `medium` | `low` (quick replies) |
| Isolation | `folder` | `folder` |
| Terminal access | off | off |
| Sandbox commands | on | on |
| Internet for commands | off | off |
| Approvals | `manual` (it can ask you) | `deny` (never asks; refuses anything not already allowed) |
| MCP servers | `twin-manage` | `twin-read` |
| Tone | `friendly` | `default` (your voice comes from the brain) |
| Engagement | `medium` | `low` (its text is the message itself) |

Why these defaults:

- **Haiku for both.** The twin is tuned and evaluated on Haiku
  ([evals/REPORT.md](../evals/REPORT.md)): it is fast enough for chat and
  cheap enough to leave running. If a computer's provider does not offer
  `haiku`, CatalEx uses the provider's default model.
- **Folder isolation.** Each agent starts with only its folder's settings and
  its own MCP server, never your personal plugins or servers. Each folder's
  `.claude/settings.json` pre-approves only its own tools.
- **No terminal.** Everything the agents do goes through their tools. The Twin
  can only read the active persona; it cannot change what it knows.
- **The Twin never asks for approvals.** It talks to other people, who must
  never be shown an approval prompt. `deny` refuses anything outside its
  read-only tools instead.

Every value is a starting value. Change any of them in the agent's settings
after the import; an update never resets your changes.

## First start

The first time either agent starts, `bin/twin-mcp` installs the tools once
(a Python environment in `~/.twin/venv` with three pinned packages, about a
minute) and creates the brain at `~/.twin/brain`. This runs in the MCP server
process, outside the agent's command sandbox. It needs Python 3.11 or newer
and an internet connection that one time.

If the first chat says the tools are missing, the install took longer than the
tool start-up allows: start a new chat. If it still fails, run `./setup.sh`
once in `~/catalex/digital-twin`; it prints what is wrong (usually a missing
Python).

Then, in the Twin Manager:

1. "Create a persona called Professional for people I work with."
2. "Add my CV." (attach a file or paste a link)
3. "Here's a chat with a colleague." (a WhatsApp export makes the twin sound
   like you)
4. "The twin should use Professional."

Connect the Twin to the channels people reach you on. It answers from the
active persona only.

## Updates

CatalEx checks this repo daily. When a new commit is offered, the agents show
an update icon. Update is a fresh install into a new folder: the same agents,
chats and your own settings move to it, and nothing is copied from the old
folder.

That is why nothing you own lives in the repo folder:

- the brain is in `~/.twin/brain` (or `TWIN_HOME`)
- the Python environment is in `~/.twin/venv` (or `TWIN_VENV`), reused across
  updates and rebuilt only when `requirements.txt` changes

## Settings reference

`catalex.yaml` is version 1 of the CatalEx repo setup file. The settings this
repo uses:

| Setting | Values |
|---|---|
| `version` | `1` (required) |
| `agents[].name` | 1 to 60 characters (required) |
| `agents[].description` | up to 200 characters |
| `agents[].folder` | the agent's folder inside the repo |
| `agents[].provider` | `claude` or `codex`; a preference |
| `agents[].model` | a model name, such as `haiku` |
| `agents[].effort` | `low`, `medium`, `high`, `xhigh` or `max` |
| `agents[].isolation` | `folder` or `none` (Claude only) |
| `tools.terminal_access` | `inherit`, `off` or `on` |
| `tools.sandbox` | `on` or `off` |
| `tools.command_internet` | `on` or `off` |
| `tools.approval_mode` | `inherit`, `manual` or `deny` |
| `tools.mcp_servers` | server names from the folder's `.mcp.json` |
| `tools.tools_off` | tools to turn off, as `server:tool` |
| `behavior.tone` | `default`, `professional` or `friendly` |
| `behavior.engagement_frequency` | `low`, `medium` or `high` |

An invalid setting never blocks the import: CatalEx uses its default instead
and tells the account that listed the repo. The file must never hold secrets,
extra folders, or `approval_mode: none`/`automatic`; only the person may grant
those.

## Notes for maintainers

- If you rename an agent folder or an MCP server, update `catalex.yaml` in the
  same change. A server name that is not in the folder's `.mcp.json` is
  reported to the listing account.
- Agent names are how updates match agents. Renaming `Twin Manager` or `Twin`
  makes CatalEx treat it as a new agent on the next update.
- The agents are built for Claude Code (`.mcp.json`, `.claude/`). On a
  computer with only Codex, CatalEx imports them on Codex, but their tools and
  skills are not loaded there yet.
- Before pushing a change to `catalex.yaml`, check it against the CatalEx
  `catalex.yaml` JSON Schema (version 1) in your editor.
