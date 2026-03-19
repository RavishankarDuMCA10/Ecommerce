from __future__ import annotations

import os
from typing import Any, Optional

import httpx
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8002")

app = FastAPI(title="CTT API Gateway", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def proxy(
    method: str,
    base_url: str,
    path: str,
    payload: Optional[dict[str, Any]] = None,
    query_params: Optional[dict[str, Any]] = None,
    bearer: Optional[str] = None,
) -> Any:
    headers: dict[str, str] = {}
    if bearer:
        headers["Authorization"] = bearer

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.request(
            method=method,
            url=f"{base_url}{path}",
            json=payload,
            params=query_params,
            headers=headers,
        )

    if response.status_code >= 400:
        detail = "Service request failed"
        try:
            data = response.json()
            detail = data.get("detail", detail)
        except Exception:
            pass
        raise HTTPException(status_code=response.status_code, detail=detail)

    if response.headers.get("content-type", "").startswith("application/json"):
        return response.json()
    return {"message": response.text}


@app.get("/health")
async def health() -> dict:
    return {"service": "gateway", "status": "ok"}


@app.post("/api/auth/register")
async def register(payload: dict[str, Any]) -> Any:
    return await proxy("POST", AUTH_SERVICE_URL, "/auth/register", payload=payload)


@app.post("/api/auth/login")
async def login(payload: dict[str, Any]) -> Any:
    return await proxy("POST", AUTH_SERVICE_URL, "/auth/login", payload=payload)


@app.post("/api/auth/logout")
async def logout(authorization: Optional[str] = Header(default=None)) -> Any:
    return await proxy("POST", AUTH_SERVICE_URL, "/auth/logout", bearer=authorization)


@app.get("/api/auth/profile")
async def get_profile(authorization: Optional[str] = Header(default=None)) -> Any:
    return await proxy("GET", AUTH_SERVICE_URL, "/auth/profile", bearer=authorization)


@app.put("/api/auth/profile")
async def update_profile(
    payload: dict[str, Any], authorization: Optional[str] = Header(default=None)
) -> Any:
    return await proxy(
        "PUT", AUTH_SERVICE_URL, "/auth/profile", payload=payload, bearer=authorization
    )


@app.get("/api/products/search")
async def search_products(
    q: str = Query(default=""),
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    color: Optional[str] = None,
    brand: Optional[str] = None,
    in_stock: Optional[bool] = None,
    sort: str = "default",
) -> Any:
    if not q.strip():
        raise HTTPException(status_code=400, detail="Please enter a search string")

    params = {
        "q": q,
        "category": category,
        "min_price": min_price,
        "max_price": max_price,
        "color": color,
        "brand": brand,
        "in_stock": in_stock,
        "sort": sort,
    }
    params = {
        k: v
        for k, v in params.items()
        if v is not None and (v != "" or k == "q")
    }
    return await proxy(
        "GET", CATALOG_SERVICE_URL, "/products/search", query_params=params
    )


@app.get("/api/products/{product_id}")
async def get_product(product_id: int) -> Any:
    return await proxy("GET", CATALOG_SERVICE_URL, f"/products/{product_id}")
