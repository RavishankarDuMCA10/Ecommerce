## CTT Ecommerce Backend (FastAPI Microservices)

This backend follows a microservice architecture with three independent FastAPI apps:

- `services/auth_service/main.py` (port `8001`): registration, login, logout, profile.
- `services/catalog_service/main.py` (port `8002`): search and product detail.
- `services/gateway/main.py` (port `8000`): single API entry point for the frontend.

### Implemented SRS Scope

- Login, logout, registration, and profile management.
- Search with validation and no-result message.
- Product details with stock and price visibility.

### Run Locally

From `Backend/`:

```bash
pip install -r requirements.txt
chmod +x run_services.sh
./run_services.sh
```

Or run services separately:

```bash
uvicorn services.auth_service.main:app --reload --port 8001
uvicorn services.catalog_service.main:app --reload --port 8002
uvicorn services.gateway.main:app --reload --port 8000
```

### API Routes Through Gateway

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/profile`
- `PUT /api/auth/profile`
- `GET /api/products/search`
- `GET /api/products/{product_id}`
