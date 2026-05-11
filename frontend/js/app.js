/**
 * NutriStore — Application Core
 *
 * Session ID management and shared helpers.
 */

/* ── Session ID ──────────────────────────────────────────────────── */

function getSessionId() {
  let sid = localStorage.getItem("nutristore_session_id");
  if (!sid) {
    sid = crypto.randomUUID();
    localStorage.setItem("nutristore_session_id", sid);
  }
  return sid;
}

/* ── Cart Badge ──────────────────────────────────────────────────── */

async function updateCartBadge() {
  try {
    const res = await apiFetch("/carrito", {
      headers: { "X-Session-ID": getSessionId() },
    });
    if (!res.ok) return;
    const items = await res.json();
    const badge = document.getElementById("cart-badge");
    if (!badge) return;
    const count = Array.isArray(items) ? items.length : 0;
    badge.textContent = count;
    badge.style.display = count > 0 ? "inline" : "none";
  } catch {
    // Cart endpoint unavailable — badge stays hidden
  }
}

document.addEventListener("DOMContentLoaded", updateCartBadge);
