import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { api } from "../api/client";

export default function ProductDetailPage() {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadProduct() {
      setLoading(true);
      setError("");
      try {
        const data = await api.getProduct(productId);
        setProduct(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadProduct();
  }, [productId]);

  if (loading) {
    return <section className="card"><p>Loading product details...</p></section>;
  }

  if (error) {
    return (
      <section className="card">
        <p className="notice error">{error}</p>
        <Link to="/search">Back to search</Link>
      </section>
    );
  }

  if (!product) {
    return (
      <section className="card">
        <p className="notice">Product not found</p>
        <Link to="/search">Back to search</Link>
      </section>
    );
  }

  return (
    <section className="card">
      <h2>{product.name}</h2>
      <p className="muted">
        {product.category} / {product.subcategory}
      </p>
      <p>{product.description}</p>
      <div className="detail-grid">
        <div>
          <strong>Price</strong>
          <p>${product.price.toFixed(2)} {product.currency}</p>
        </div>
        <div>
          <strong>Availability</strong>
          <p>{product.availability_label}</p>
        </div>
        <div>
          <strong>Brand</strong>
          <p>{product.brand}</p>
        </div>
        <div>
          <strong>Color</strong>
          <p>{product.color}</p>
        </div>
        <div>
          <strong>Rating</strong>
          <p>{product.rating}</p>
        </div>
        <div>
          <strong>Stock Quantity</strong>
          <p>{product.stock_qty}</p>
        </div>
      </div>
      <Link to="/search">Back in Catalog</Link>
    </section>
  );
}
