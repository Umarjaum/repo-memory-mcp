document.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-copy]');
  if (!button) return;
  const text = button.getAttribute('data-copy') || '';
  try {
    await navigator.clipboard.writeText(text);
    const original = button.textContent;
    button.textContent = 'Copied';
    setTimeout(() => { button.textContent = original; }, 1400);
  } catch {
    button.textContent = 'Select and copy';
    setTimeout(() => { button.textContent = 'Copy'; }, 1600);
  }
});
