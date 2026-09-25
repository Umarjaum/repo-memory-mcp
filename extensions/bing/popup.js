chrome.storage.local.get(['lastPrompt'], ({lastPrompt}) => {
  document.getElementById('prompt').textContent = lastPrompt || 'No prompt copied yet.';
});
