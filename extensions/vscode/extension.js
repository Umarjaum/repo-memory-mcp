const vscode = require('vscode');

const MCP_CONFIG = JSON.stringify({
  mcpServers: {
    'repo-memory': {
      command: 'uvx',
      args: ['--from', 'repo-memory-mcp-ai', 'repo-memory-mcp']
    }
  }
}, null, 2);

const STARTUP_INSTRUCTION = 'At the start of this coding session, call get_startup_context. Store durable corrections and repository rules with repo-memory tools. Never store secrets.';

async function copy(text, message) {
  await vscode.env.clipboard.writeText(text);
  vscode.window.showInformationMessage(message);
}

function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand('repoMemory.copyMcpConfig', () => copy(MCP_CONFIG, 'Repo Memory MCP configuration copied.')),
    vscode.commands.registerCommand('repoMemory.copyStartupInstruction', () => copy(STARTUP_INSTRUCTION, 'Repo Memory startup instruction copied.')),
    vscode.commands.registerCommand('repoMemory.openDocs', () => vscode.env.openExternal(vscode.Uri.parse('https://repo-memory-mcp.pages.dev/docs.html')))
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
