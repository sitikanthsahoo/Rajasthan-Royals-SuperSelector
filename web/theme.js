/* Run before CSS to avoid flashing the wrong theme. No application state is remounted. */
(() => {
  'use strict';
  const key = 'superr-appearance';
  const media = window.matchMedia('(prefers-color-scheme: dark)');
  let choice = null;
  try { choice = localStorage.getItem(key); } catch (_) { /* Works without storage too. */ }
  const valid = value => value === 'light' || value === 'dark';
  if (!valid(choice)) choice = null;
  function apply(theme) {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
      toggle.setAttribute('aria-checked', String(theme === 'dark'));
      toggle.title = `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`;
    }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = theme === 'dark' ? '#101126' : '#151542';
  }
  apply(choice || (media.matches ? 'dark' : 'light'));
  document.addEventListener('DOMContentLoaded', () => {
    apply(document.documentElement.dataset.theme);
    document.getElementById('theme-toggle')?.addEventListener('click', () => {
      choice = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      apply(choice);
      try { localStorage.setItem(key, choice); } catch (_) { /* Persistence is optional. */ }
    });
  });
  media.addEventListener('change', event => { if (!choice) apply(event.matches ? 'dark' : 'light'); });
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) {
      choice = valid(event.newValue) ? event.newValue : null;
      apply(choice || (media.matches ? 'dark' : 'light'));
    }
  });
})();
