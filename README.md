# Ecommerce

FastAPI + React ecommerce starter built from the CTT SRS document with a microservice architecture.

## Project Structure

- `Backend/`: FastAPI microservices (`auth_service`, `catalog_service`, `gateway`).
- `Frontend/`: React (Vite) client application.

## Implemented Functionality

- Login, logout, registration, and profile update.
- Product search page with filters and validation.
- Product details page showing stock and pricing information.

## Quick Start

Backend (terminal 1):

```bash
cd Backend
pip install -r requirements.txt
./run_services.sh
```

Frontend (terminal 2):

```bash
cd Frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

Gateway URL: `http://localhost:8000`