const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, { method = "GET", body, token } = {}) {
  const headers = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

export const api = {
  register: (payload) => request("/api/auth/register", { method: "POST", body: payload }),
  login: (payload) => request("/api/auth/login", { method: "POST", body: payload }),
  logout: (token) => request("/api/auth/logout", { method: "POST", token }),
  getProfile: (token) => request("/api/auth/profile", { token }),
  updateProfile: (token, payload) => request("/api/auth/profile", { method: "PUT", token, body: payload }),
  searchProducts: (params) => {
    const filteredParams = Object.fromEntries(
      Object.entries(params).filter(([, value]) => value !== "" && value !== null && value !== undefined)
    );
    const query = new URLSearchParams(filteredParams).toString();
    return request(`/api/products/search?${query}`);
  },
  getProduct: (id) => request(`/api/products/${id}`),
};
