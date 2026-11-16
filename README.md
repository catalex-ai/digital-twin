# Digital Twin

A personal brain that answers as you. It runs on your computer: no server, no
account, no cloud copy of your data.

You get two agents that share one folder, the brain:

- **Twin Manager.** You talk to it. Give it a CV, notes, a profile export, a
  chat or a link. It breaks them into small facts, files each one under a type,
  asks you a few questions, and takes corrections.
- **Twin.** Other people talk to it. It answers as you, in the first person,
  from the facts you have allowed for that audience. It can only read.

```
 you ──> Twin Manager ──> brain folder ──> Twin ──> other people
         (reads, splits,   raw facts       (reads only the
          asks, corrects)  + personas      active persona)
```

## Install

Pick one. All three end with the same two agents and the same brain at
`~/.twin/brain`.

### 1. CatalEx Marketplace

In CatalEx, open **Marketplace**, find **Digital Twin** (or choose **Add a
repo** and paste `https://github.com/catalex-ai/digital-twin`), and press
**Import**. CatalEx sets up both agents from [`catalex.yaml`](catalex.yaml):
Claude Haiku, each agent limited to its own folder and its own tools. Then
open the **Twin Manager** and say "Create a persona called Professional for
people I work with". See [docs/catalex.md](docs/catalex.md) for every setting
and how updates work.

### 2. Ask your coding assistant

Give Claude Code (or another coding assistant) this prompt:

> Read https://raw.githubusercontent.com/catalex-ai/digital-twin/main/SKILL.md
> and set up the Digital Twin here.

### 3. By hand

You need Python 3.11+, Git and [Claude Code](https://claude.com/claude-code).

```bash
git clone https://github.com/catalex-ai/digital-twin.git
cd digital-twin
./setup.sh                       # brain in ~/.twin/brain
TWIN_HOME=~/my-brain ./setup.sh  # or somewhere else
```

Then start each agent in its own folder:

```bash
cd manager-agent && claude   # you: the Twin Manager
cd twin-agent && claude      # other people: the Twin
```

Claude Code asks once to trust each folder; say yes. If you set `TWIN_HOME`,
use the same value when you start Claude.

`setup.sh` is optional: the agents set themselves up on their first start.
Either way, the one-time install makes a Python environment in `~/.twin/venv`,
installs three pinned packages (`mcp`, `model2vec`, `PyYAML`) and fetches a
small search model (about 30 MB). It is safe to run again.

## How it works

1. You add material. The manager splits it into facts, one sentence each.
2. Each fact gets a **type** (work history, education, family...).
3. You decide, once per type, which audience may know it. "May Professional
   know about family?" You are never asked about a single fact.
4. A **persona** is one audience (professional, personal). Each persona's folder
   holds only the facts allowed for it.
5. You tell the manager which persona the twin uses.

Questions never block. Material is always kept, and what is waiting on an answer
simply waits.

**Profiles.** One brain can hold several identities, each fully separate and
each with a tone preset (natural, light, humorous, serious, leader, parody).
See [docs/profiles.md](docs/profiles.md).

## Things to say to the manager

- "Create a persona called Professional for people I work with."
- "Here's a chat with my sister." (paste or attach a WhatsApp export: one chat
  per kind of person, a normal recent one is best; this is what makes the twin
  sound like you)
- "Ask me how I'd reply to a few messages."
- "Add my CV." (attach a file or paste a link)
- "The twin should use Professional."
- "You said I live in Pune. It should be Leeds."
- "Make the twin sound more casual."
- "Never keep my phone number." / "Allow my email in Personal."
- "Tidy up." / "Show me what the twin knows."
- "Set up a parody of <name>." / "Switch to <profile>." / "Make it funnier."

After new chats or replies, the manager runs `make_foils`: for each real
message it writes the polished version a bot would have sent, and the twin is
shown both, so it learns what not to sound like. It needs the `claude` command
line.

"Show me what the twin knows" writes `audit.html` in the brain folder. Open it
in a browser. It lists each persona, its facts by topic, open questions and
conflicts. It never shows held values.

## Privacy settings

Names are information. People, companies and places are stored. Contact details
and secrets follow a setting you can change at any time.

| mode | what is stored | the persona sees |
|---|---|---|
| `allow` | the value as written | the value |
| `hold` | a token such as `⟦email:3fa9c1⟧`, the value kept in the manager zone only | nothing |
| `drop` | a token such as `⟦password⟧`, the value kept nowhere | nothing |

Defaults: email, phone and address are `hold`. Password, bank account, card and
government ID are `drop`. Everything else is `allow`. `drop` cannot be undone.
See [PRIVACY.md](PRIVACY.md).

## Agents and tools

| Agent | Folder | MCP server | Tools |
|---|---|---|---|
| Twin Manager | `manager-agent/` | `twin-manage` | read and write the brain: add material, personas, rules, privacy, questions, corrections, tidy, audit |
| Twin | `twin-agent/` | `twin-read` | read only the active persona: `brief`, `search`, `examples`, `check_reply`, `ask_owner` |

Each folder has its own instructions (`CLAUDE.md`, plus `AGENTS.md` for the
Twin), its own skill in `.claude/skills/`, its own `.mcp.json`, and
`.claude/settings.json`, which pre-approves only that folder's tools. Both
servers start through [`bin/twin-mcp`](bin/twin-mcp). The package adds no other
restrictions: whatever hosts the agents (Claude Code, CatalEx) decides which
tools each one may use.

## Repo layout

```text
catalex.yaml          CatalEx Marketplace setup (both agents, Haiku)
SKILL.md              setup steps for a coding assistant
setup.sh              optional one-time setup
bin/                  twin-mcp (starts a server) and env.sh (finds Python)
manager-agent/        the Twin Manager: instructions, skill, tools config
twin-agent/           the Twin: instructions, skill, tools config
brainkit/             the code behind both MCP servers
templates/            starting soul, voice, rules, contract, privacy, schema
tests/, evals/        unit tests and the eval harness
docs/catalex.md       how the twin is configured on CatalEx
```

## More

- [docs/catalex.md](docs/catalex.md): CatalEx setup, settings and updates
- [PRIVACY.md](PRIVACY.md): what is stored where
- [TESTING.md](TESTING.md): tests and evals
- [evals/REPORT.md](evals/REPORT.md): eval results by round
- [PERSONA-FEATURES.md](PERSONA-FEATURES.md): what makes the twin sound like you
- [DEV-CONTRACT.md](DEV-CONTRACT.md): module interfaces, for contributors

It is a hobby project for one person, not a product. [MIT License](LICENSE).
