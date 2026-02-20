# Blink - B2C Quick Commerce Application (Blinkit-like)

A minimal but functional internship evaluation project implementing a **microservice-based quick commerce app** with FastAPI + MongoDB backend and Flutter frontend.

## 1) Architecture Overview

```text
+------------------------+
|     Flutter App        |
| (Login, Catalog, Cart, |
|  Order, Tracking)      |
+-----------+------------+
            |
            | REST/JSON
            v
+-----------+------------+     +------------------------+
|      User Service      |     |  Product Service       |
|  register/login/profile|     | products/categories    |
+-----------+------------+     +-----------+------------+
            |                              |
            | JWT token                    |
            v                              v
+-----------+------------+     +-----------+------------+
|   Cart & Order Service |---->| Product Service (price)|
| cart + order creation  |     +------------------------+
+-----------+------------+
            |
            | order_id
            v
+-----------+------------+
| Delivery Status Service|
| status lifecycle       |
+------------------------+

All services persist in MongoDB (separate collections).
```

## 2) Backend Microservices (Exactly 4)

### A) User Service (`user-service/`)
Responsibilities:
- Register user
- Login user
- Return profile for authenticated user

APIs:
- `POST /register`
- `POST /login`
- `GET /profile` (JWT protected)
- `GET /health`

Data model (`users` collection):
- `user_id`
- `name`
- `email`
- `password` (bcrypt hash)
- `created_at`

---

### B) Product Catalog Service (`product-service/`)
Responsibilities:
- Provide product list
- Product detail
- Category list

APIs:
- `GET /products`
- `GET /products/{product_id}`
- `GET /categories`
- `GET /health`

Data model (`products` collection):
- `product_id`
- `name`
- `description`
- `price`
- `category`
- `image_url`
- `availability`

---

### C) Cart & Order Service (`cart-order-service/`)
Responsibilities:
- Add/remove/list cart
- Create orders
- List order history

APIs:
- `POST /cart/add` (JWT protected)
- `POST /cart/remove` (JWT protected)
- `GET /cart` (JWT protected)
- `POST /order/create` (JWT protected)
- `GET /orders` (JWT protected)
- `GET /health`

Data models:
- `cart` collection:
  - `user_id`, `product_id`, `quantity`
- `orders` collection:
  - `order_id`, `user_id`, `items`, `total_amount`, `timestamp`, `order_reference_id` (UUID)

---

### D) Delivery & Order Status Service (`delivery-service/`)
Responsibilities:
- Track status by order id
- Update status manually

APIs:
- `GET /order/{order_id}/status`
- `POST /order/{order_id}/update-status`
- `GET /health`

Status flow:
`PLACED -> PACKED -> OUT_FOR_DELIVERY -> DELIVERED`

Data model (`delivery_status` collection):
- `order_id`
- `current_status`
- `last_updated`

## 3) Frontend (Flutter)

Folder: `flutter-app/`

Implemented screens:
- Login
- Signup
- Home (categories + products)
- Product details
- Cart
- Order confirmation
- Order tracking

Features:
- Calls all backend REST APIs
- JWT token used on frontend-facing protected APIs
- Simple error handling + navigation

## 4) Project Structure

```text
root/
├── user-service/
├── product-service/
├── cart-order-service/
├── delivery-service/
├── flutter-app/
├── docker-compose.yml
├── k8s/
│   ├── mongodb.yaml
│   ├── user-service.yaml
│   ├── product-service.yaml
│   ├── cart-order-service.yaml
│   └── delivery-service.yaml
└── README.md
```

## 5) Run with Docker Compose

```bash
docker compose up --build
```

Services:
- User service: `http://localhost:8001`
- Product service: `http://localhost:8002`
- Cart & order service: `http://localhost:8003`
- Delivery service: `http://localhost:8004`
- MongoDB: `mongodb://localhost:27017`

## 6) Kubernetes (Minikube/kind)

Build images in local docker daemon used by cluster, then apply:

```bash
kubectl apply -f k8s/mongodb.yaml
kubectl apply -f k8s/user-service.yaml
kubectl apply -f k8s/product-service.yaml
kubectl apply -f k8s/cart-order-service.yaml
kubectl apply -f k8s/delivery-service.yaml
```

Use `kubectl port-forward` for local access.

## 7) Assumptions

- Payment flow is out of scope (orders considered prepaid).
- Internal service calls are trusted.
- Hardcoded JWT secret is used for demo simplicity.
- Products are auto-seeded on startup.

## 8) Known Limitations

- No API gateway.
- No central logging/monitoring.
- Flutter app uses localhost URLs (adjust for emulator/device networking).
- No production-grade secrets/config management.

## 9) AI-assisted Disclosure

- Architecture scaffolding, service boilerplate, Docker/K8s manifests, and README drafting were AI-assisted.
- Final integration and structure were manually reviewed.

## 10) Demo Video & Drive Upload

- Demo video (2–5 min): _To be recorded and attached by project submitter._
- Google Drive upload link: _To be added by project submitter._
