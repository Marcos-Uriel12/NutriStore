/**
 * NutriStore — Admin Auth & API Client
 *
 * JWT stored in localStorage as "nutristore_token".
 * All admin API calls auto-attach the Bearer token.
 * 401 responses trigger automatic logout + redirect.
 */

const admin = {
  TOKEN_KEY: "nutristore_token",

  /* ── Token Management ─────────────────────────────────────────── */

  getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  },

  setToken(token) {
    localStorage.setItem(this.TOKEN_KEY, token);
  },

  clearToken() {
    localStorage.removeItem(this.TOKEN_KEY);
  },

  isAuthenticated() {
    return !!this.getToken();
  },

  /* ── Auth ──────────────────────────────────────────────────────── */

  async login(email, password) {
    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const detail = await res.text();
      throw new Error(detail || "Credenciales inválidas");
    }
    const data = await res.json();
    this.setToken(data.access_token);
    return data;
  },

  logout() {
    this.clearToken();
    window.location.href = "/admin/login.html";
  },

  /* ── Auth-aware Fetch ──────────────────────────────────────────── */

  async fetch(url, options = {}) {
    const headers = { ...(options.headers || {}) };
    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(url, { ...options, headers });

    if (res.status === 401) {
      this.clearToken();
      window.location.href = "/admin/login.html";
      throw new Error("Sesión expirada");
    }

    return res;
  },

  /* ── Categorías API ────────────────────────────────────────────── */

  async getCategorias() {
    const res = await this.fetch("/categorias");
    return res.json();
  },

  async createCategoria(data) {
    const res = await this.fetch("/categorias", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const detail = await res.text();
      throw new Error(detail || "Error al crear categoría");
    }
    return res.json();
  },

  /* ── Productos API ─────────────────────────────────────────────── */

  async getProductos() {
    const res = await this.fetch("/productos");
    return res.json();
  },

  async createProducto(data) {
    const res = await this.fetch("/productos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const detail = await res.text();
      throw new Error(detail || "Error al crear producto");
    }
    return res.json();
  },

  async updateProducto(id, data) {
    const res = await this.fetch(`/productos/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const detail = await res.text();
      throw new Error(detail || "Error al actualizar producto");
    }
    return res.json();
  },

  async deleteProducto(id) {
    const res = await this.fetch(`/productos/${id}`, { method: "DELETE" });
    if (!res.ok && res.status !== 204) {
      const detail = await res.text();
      throw new Error(detail || "Error al eliminar producto");
    }
  },

  /* ── Pedidos API ───────────────────────────────────────────────── */

  async getPedidos() {
    const res = await this.fetch("/pedidos");
    return res.json();
  },

  async updatePedidoEstado(id, estado) {
    const res = await this.fetch(`/pedidos/${id}/estado`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ estado }),
    });
    if (!res.ok) {
      const detail = await res.text();
      throw new Error(detail || "Error al actualizar estado");
    }
    return res.json();
  },

  /* ── Envíos Config API ─────────────────────────────────────────── */

  async getEnvios() {
    const res = await this.fetch("/envios/config");
    return res.json();
  },

  async updateEnvios(data) {
    const res = await this.fetch("/envios/config", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const detail = await res.text();
      throw new Error(detail || "Error al actualizar configuración");
    }
    return res.json();
  },
};
