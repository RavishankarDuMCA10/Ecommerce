from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

APP_TITLE = "CTT Catalog Service"
DB_PATH = Path(__file__).resolve().parent / "catalog.db"

app = FastAPI(title=APP_TITLE, version="0.1.0")


class Product(BaseModel):
    id: int
    name: str
    category: str
    subcategory: str
    description: str
    brand: str
    color: str
    price: float
    currency: str
    rating: float
    in_stock: bool
    stock_qty: int


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                description TEXT NOT NULL,
                brand TEXT NOT NULL,
                color TEXT NOT NULL,
                price REAL NOT NULL,
                currency TEXT NOT NULL,
                rating REAL NOT NULL,
                in_stock INTEGER NOT NULL,
                stock_qty INTEGER NOT NULL
            )
            """
        )

        existing = conn.execute("SELECT COUNT(1) AS c FROM products").fetchone()["c"]
        if existing > 0:
            return

        seed = [
            (
                1,
                "Men Casual Shirt",
                "Men",
                "Casual Shirts",
                "Cotton casual shirt for daily wear.",
                "MCart",
                "Blue",
                39.99,
                "USD",
                4.2,
                1,
                15,
            ),
            (
                2,
                "Women Kurta Set",
                "Women",
                "Kurtas & Suits",
                "Three-piece festive kurta set.",
                "Aarika",
                "Maroon",
                59.99,
                "USD",
                4.5,
                1,
                9,
            ),
            (
                3,
                "Slim Fit Jeans",
                "Men",
                "Jeans",
                "Stretch denim for comfortable fit.",
                "DenimCo",
                "Black",
                49.0,
                "USD",
                4.1,
                1,
                20,
            ),
            (
                4,
                "Summer Floral Dress",
                "Women",
                "Dresses & Jumpsuits",
                "Lightweight floral midi dress.",
                "Luna",
                "Yellow",
                65.5,
                "USD",
                4.6,
                1,
                13,
            ),
            (
                5,
                "Classic Blazer",
                "Men",
                "Blazers & Coats",
                "Formal textured blazer.",
                "Regent",
                "Navy",
                119.0,
                "USD",
                4.4,
                1,
                4,
            ),
            (
                6,
                "Analog Watch",
                "Women",
                "Watches",
                "Stainless steel water-resistant watch.",
                "Timely",
                "Silver",
                89.99,
                "USD",
                4.0,
                1,
                25,
            ),
            (
                7,
                "Athletic Track Pants",
                "Men",
                "Track Pants",
                "Breathable track pants for workouts.",
                "Sprint",
                "Grey",
                34.99,
                "USD",
                3.9,
                1,
                18,
            ),
            (
                8,
                "Silk Saree",
                "Women",
                "Sarees & Blouses",
                "Handcrafted silk saree with border work.",
                "Vastra",
                "Red",
                149.99,
                "USD",
                4.8,
                0,
                0,
            ),
            (
                9,
                "Leather Wallet",
                "Men",
                "Wallets & Belts",
                "Premium fold wallet with RFID block.",
                "CraftHide",
                "Brown",
                29.5,
                "USD",
                4.3,
                1,
                40,
            ),
            (
                10,
                "Women Sunglasses",
                "Women",
                "Sunglasses",
                "UV-protected oversized sunglasses.",
                "Solaris",
                "Black",
                22.0,
                "USD",
                4.1,
                1,
                31,
            ),
        ]

        conn.executemany(
            """
            INSERT INTO products(id, name, category, subcategory, description, brand, color, price, currency, rating, in_stock, stock_qty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            seed,
        )


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "category": row["category"],
        "subcategory": row["subcategory"],
        "description": row["description"],
        "brand": row["brand"],
        "color": row["color"],
        "price": row["price"],
        "currency": row["currency"],
        "rating": row["rating"],
        "in_stock": bool(row["in_stock"]),
        "stock_qty": row["stock_qty"],
    }


@app.get("/health")
def health() -> dict:
    return {"service": "catalog", "status": "ok"}


@app.get("/products/search")
def search_products(
    q: str = Query(default="", description="Search query"),
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    color: Optional[str] = None,
    brand: Optional[str] = None,
    in_stock: Optional[bool] = None,
    sort: str = "default",
) -> dict:
    if not q.strip():
        raise HTTPException(status_code=400, detail="Please enter a search string")

    query = (
        "SELECT * FROM products WHERE (LOWER(name) LIKE ? OR LOWER(description) LIKE ?)"
    )
    params: list[object] = [f"%{q.lower().strip()}%", f"%{q.lower().strip()}%"]

    if category:
        query += " AND LOWER(category) = ?"
        params.append(category.lower().strip())
    if min_price is not None:
        query += " AND price >= ?"
        params.append(min_price)
    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)
    if color:
        query += " AND LOWER(color) = ?"
        params.append(color.lower().strip())
    if brand:
        query += " AND LOWER(brand) = ?"
        params.append(brand.lower().strip())
    if in_stock is not None:
        query += " AND in_stock = ?"
        params.append(1 if in_stock else 0)

    order_clause = {
        "price_asc": " ORDER BY price ASC",
        "price_desc": " ORDER BY price DESC",
        "rating_desc": " ORDER BY rating DESC",
        "popularity": " ORDER BY rating DESC, stock_qty DESC",
        "default": " ORDER BY id ASC",
    }.get(sort, " ORDER BY id ASC")

    query += order_clause

    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()

    products = [row_to_dict(row) for row in rows]
    if not products:
        return {
            "products": [],
            "message": "No products found for the provided search string",
        }

    return {
        "products": products,
        "count": len(products),
    }


@app.get("/products/{product_id}")
def get_product(product_id: int) -> dict:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    product = row_to_dict(row)
    product["availability_label"] = (
        "In Stock" if product["in_stock"] else "Out of Stock"
    )
    return product
