/**
 * NutriStore — Cart API Client
 *
 * Relies on getSessionId() from js/app.js.
 * All cart endpoints use the X-Session-ID header.
 */

const cart = {
  /**
   * Fetch the current cart contents.
   * @returns {Promise<Array>} Array of CartItemResponse objects.
   */
  async get() {
    const res = await fetch("/carrito", {
      headers: { "X-Session-ID": getSessionId() },
    });
    if (!res.ok) {
      console.error("cart.get failed:", res.status, await res.text());
      return [];
    }
    return res.json();
  },

  /**
   * Add a product to the cart.
   * @param {number} productoId
   * @param {number} cantidad
   * @param {string} unidadMedida — "KG" | "UNIDAD" (default "KG")
   * @returns {Promise<Object>}
   */
  async add(productoId, cantidad, unidadMedida = "KG") {
    const res = await fetch("/carrito", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Session-ID": getSessionId(),
      },
      body: JSON.stringify({
        producto_id: productoId,
        cantidad,
        unidad_medida: unidadMedida,
      }),
    });
    if (!res.ok) {
      const detail = await res.text();
      throw new Error(`Error al agregar producto: ${detail}`);
    }
    return res.json();
  },

  /**
   * Update quantity of an item already in the cart.
   * @param {number} productoId
   * @param {number} cantidad
   * @param {string} unidadMedida — "KG" | "UNIDAD" (default "KG")
   * @returns {Promise<Object>}
   */
  async update(productoId, cantidad, unidadMedida = "KG") {
    const res = await fetch(`/carrito/${productoId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-Session-ID": getSessionId(),
      },
      body: JSON.stringify({
        producto_id: productoId,
        cantidad,
        unidad_medida: unidadMedida,
      }),
    });
    if (!res.ok) {
      const detail = await res.text();
      throw new Error(`Error al actualizar: ${detail}`);
    }
    return res.json();
  },

  /**
   * Remove a single item from the cart.
   * @param {number} productoId
   * @returns {Promise<Object>}
   */
  async remove(productoId) {
    const res = await fetch(`/carrito/${productoId}`, {
      method: "DELETE",
      headers: { "X-Session-ID": getSessionId() },
    });
    if (!res.ok) {
      const detail = await res.text();
      throw new Error(`Error al eliminar: ${detail}`);
    }
    return res.json();
  },

  /**
   * Clear the entire cart.
   * @returns {Promise<void>}
   */
  async clear() {
    await fetch("/carrito", {
      method: "DELETE",
      headers: { "X-Session-ID": getSessionId() },
    });
  },
};
