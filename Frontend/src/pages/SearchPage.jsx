import { useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/client";

const initialFilters = {
  q: "",
  category: "",
  color: "",
  brand: "",
  sort: "default",
};

export default function SearchPage() {
  const [filters, setFilters] = useState(initialFilters);
  const [result, setResult] = useState({ products: [], message: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSearch(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const payload = {
        ...filters,
      };
      const data = await api.searchProducts(payload);
      setResult({ products: data.products || [], message: data.message || "" });
    } catch (err) {
      setResult({ products: [], message: "" });
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="search-layout">
      <article className="card">
        <h2>Search Products</h2>
        <form className="form" onSubmit={onSearch}>
          <label>
            Search string
            <input
              value={filters.q}
              onChange={(e) => setFilters((prev) => ({ ...prev, q: e.target.value }))}
              placeholder="Try shirt, saree, watch"
              required
            />
          </label>

          <div className="grid-2">
            <label>
              Category
              <select value={filters.category} onChange={(e) => setFilters((prev) => ({ ...prev, category: e.target.value }))}>
                <option value="">Any</option>
                <option value="Men">Men</option>
                <option value="Women">Women</option>
              </select>
            </label>
            <label>
              Sort
              <select value={filters.sort} onChange={(e) => setFilters((prev) => ({ ...prev, sort: e.target.value }))}>
                <option value="default">Default</option>
                <option value="price_asc">Price low to high</option>
                <option value="price_desc">Price high to low</option>
                <option value="rating_desc">Top rated</option>
                <option value="popularity">Popularity</option>
              </select>
            </label>
            <label>
              Brand
              <input value={filters.brand} onChange={(e) => setFilters((prev) => ({ ...prev, brand: e.target.value }))} />
            </label>
            <label>
              Color
              <input value={filters.color} onChange={(e) => setFilters((prev) => ({ ...prev, color: e.target.value }))} />
            </label>
          </div>

          <button disabled={loading} type="submit">
            {loading ? "Searching..." : "Search"}
          </button>
        </form>

        {error ? <p className="notice error">{error}</p> : null}
        {result.message ? <p className="notice">{result.message}</p> : null}
      </article>

      <article className="card">
        <h2>Results</h2>
        <ul className="results">
          {result.products.map((product) => (
            <li key={product.id}>
              <h3>{product.name}</h3>
              <p>{product.description}</p>
              <p>
                ${product.price.toFixed(2)} · {product.brand} · {product.in_stock ? "In Stock" : "Out of Stock"}
              </p>
              <Link to={`/products/${product.id}`}>View product details</Link>
            </li>
          ))}
        </ul>
      </article>
    </section>
  );
}
