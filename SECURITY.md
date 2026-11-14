# Security

Please report security problems privately through GitHub's
[security advisories](https://github.com/catalex-ai/digital-twin/security/advisories/new),
not in a public issue.

- The brain lives on your computer, outside this repo (`~/.twin/brain` by
  default). Never commit a brain, a chat export or a corpus.
- The Twin is read-only. Its tools read only the active persona's folder,
  which holds only the facts you allowed for that audience. See
  [PRIVACY.md](PRIVACY.md).
- Treat imported documents, chats and links as untrusted input.
- Instructions are not a security boundary. Whatever hosts the agents
  (Claude Code, CatalEx) enforces which tools each one may use.
