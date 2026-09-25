const MENU_ID = 'repo-memory-copy-selection';

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: MENU_ID,
    title: 'Copy as repo-memory prompt',
    contexts: ['selection'],
    documentUrlPatterns: ['https://www.bing.com/*']
  });
});

chrome.contextMenus.onClicked.addListener((info) => {
  if (info.menuItemId !== MENU_ID || !info.selectionText) return;
  const prompt = `Review this research note and decide whether it is durable repository guidance. If it is, store it with an appropriate repo-memory tool. Do not store secrets.\n\nSelected text:\n${info.selectionText}`;
  chrome.storage.local.set({ lastPrompt: prompt });
  chrome.tabs.create({ url: `data:text/plain;charset=utf-8,${encodeURIComponent(prompt)}` });
});
