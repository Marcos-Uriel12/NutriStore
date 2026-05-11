/**
 * NutriStore — Cart API Client
 */

const cart = {
  async get() {
    const res = await apiFetch("/carrito", {
      headers: { "X-Session-ID": getSessionId() },
    });
    return res.json();
  },

  async add(productoId, cantidad, unidadMedida = "KG") {
    const res = await apiFetch("/carrito", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Session-ID": getSessionId() },
      body: JSON.stringify({ producto_id: productoId, cantidad, unidad_medida: unidadMedida }),
    });
    return res.json();
  },

  async update(productoId, cantidad, unidadMedida = "KG") {
    const res = await apiFetch(`/carrito/${productoId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", "X-Session-ID": getSessionId() },
      body: JSON.stringify({ producto_id: productoId, cantidad, unidad_medida: unidadMedida }),
    });
    return res.json();
  },

  async remove(productoId) {
    const res = await apiFetch(`/carrito/${productoId}`, {
      method: "DELETE",
      headers: { "X-Session-ID": getSessionId() },
    });
    return res.json();
  },

  async clear() {
    await apiFetch("/carrito", {
      method: "DELETE",
      headers: { "X-Session-ID": getSessionId() },
    });
  },
};
