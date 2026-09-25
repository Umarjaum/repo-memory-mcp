# Repo Memory Prompt Helper for Bing

A Manifest V3 browser companion for Bing research workflows.

## What it does

On `https://www.bing.com`, select text, right-click, and choose **Copy as repo-memory prompt**. The extension formats the selection into a prompt that an AI coding client can review and store with the appropriate repo-memory tool.

## Privacy boundary

- No page scraping or background browsing.
- No network requests to repo-memory or third parties.
- No API keys.
- Selected text is stored only in the browser’s local extension storage until replaced.
- A browser extension cannot directly invoke a local stdio MCP server without a native-messaging bridge. This companion intentionally copies a prompt instead.

## Install locally

1. Open the browser’s extensions page.
2. Enable Developer mode.
3. Choose **Load unpacked**.
4. Select this directory: `extensions/bing`.
5. Visit Bing, select research text, and use the context-menu action.

MIT licensed. Contributions are welcome.
