# Contributing

1. Set up a dev environment and run the tests (see [TESTING.md](TESTING.md)).
2. Read [DEV-CONTRACT.md](DEV-CONTRACT.md) before changing a module: it fixes
   the interfaces between them.
3. Never put a real person's name, job or data in code, prompts, templates,
   tests or fixtures. Use placeholders ("Asha", "Northwind Ltd").
4. Keep the Twin read-only, and keep held values out of persona folders.
5. If you add or rename an agent, an agent folder or an MCP server, update
   `catalex.yaml` and [docs/catalex.md](docs/catalex.md) in the same pull request.
