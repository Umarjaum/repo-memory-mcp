# repo-memory-mcp for VS Code

A small, privacy-safe companion extension for the local [repo-memory-mcp](https://github.com/Umarjaum/repo-memory-mcp) server.

## Commands

- **Repo Memory: Copy MCP Configuration** — copies the `uvx` stdio server configuration.
- **Repo Memory: Copy Startup Instruction** — copies a recommended agent instruction.
- **Repo Memory: Open Documentation** — opens the public setup guide.

The extension does not access repositories, make network requests, collect telemetry, or invoke the MCP server directly. It only writes user-selected text to the VS Code clipboard or opens the documentation URL.

## Package locally

```bash
cd extensions/vscode
npx @vscode/vsce package
code --install-extension repo-memory-*.vsix
```

## Contribute

The extension is MIT licensed and maintained in the main repository. Add tests or commands only when they preserve the local-first, explicit-consent design.
