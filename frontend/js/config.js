// NutriStore API Configuration
// =============================
// For local dev, leave empty (same-origin).
// For production, set to your Render backend URL.
// Netlify: set API_BASE env var in build settings.

// If you deploy the frontend separately, change this:
const API_BASE = window.API_BASE || '';

// HTMX: prepend API_BASE to all hx-get/hx-post/etc URLs
document.addEventListener('htmx:configRequest', (e) => {
  if (API_BASE && e.detail.path?.startsWith?.('/')) {
    e.detail.path = API_BASE + e.detail.path;
  }
  // Add session ID header
  e.detail.headers['X-Session-ID'] = getSessionId();
  const token = localStorage.getItem('nutristore_token');
  if (token) {
    e.detail.headers['Authorization'] = `Bearer ${token}`;
  }
});

// Fetch wrapper that prepends API_BASE
async function apiFetch(path, options = {}) {
  const url = API_BASE + path;
  const headers = { ...options.headers };

  const token = localStorage.getItem('nutristore_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(url, { ...options, headers });
  if (res.status === 401 && !path.startsWith('/auth/login')) {
    localStorage.removeItem('nutristore_token');
    if (window.location.pathname.startsWith('/admin')) {
      window.location.href = '/admin/login.html';
    }
  }
  return res;
}
