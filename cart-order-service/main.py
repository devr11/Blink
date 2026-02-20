import os
import uuid
from datetime import datetime

import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI(title="Cart & Order Service", version="1.0.0")

CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in CORS_ALLOW_ORIGINS.split(",") if origin.strip()]
allow_credentials = "*" not in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "blinkit")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
cart_collection = db["cart"]
orders_collection = db["orders"]

security = HTTPBearer()


class CartItemRequest(BaseModel):
    product_id: str
    quantity: int = 1


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user_id
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


@app.get("/health")
def health():
    return {"status": "ok", "service": "cart-order-service"}


@app.post("/cart/add")
def add_to_cart(payload: CartItemRequest, user_id: str = Depends(get_current_user)):
    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    existing = cart_collection.find_one({"user_id": user_id, "product_id": payload.product_id})
    if existing:
        cart_collection.update_one(
            {"_id": existing["_id"]},
            {"$set": {"quantity": existing["quantity"] + payload.quantity}},
        )
    else:
        cart_collection.insert_one(
            {"user_id": user_id, "product_id": payload.product_id, "quantity": payload.quantity}
        )
    return {"message": "Item added to cart"}


@app.post("/cart/remove")
def remove_from_cart(payload: CartItemRequest, user_id: str = Depends(get_current_user)):
    existing = cart_collection.find_one({"user_id": user_id, "product_id": payload.product_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Item not in cart")

    if existing["quantity"] <= payload.quantity:
        cart_collection.delete_one({"_id": existing["_id"]})
    else:
        cart_collection.update_one(
            {"_id": existing["_id"]},
            {"$set": {"quantity": existing["quantity"] - payload.quantity}},
        )
    return {"message": "Item removed from cart"}


@app.get("/cart")
def get_cart(user_id: str = Depends(get_current_user)):
    items = list(cart_collection.find({"user_id": user_id}, {"_id": 0}))
    return {"user_id": user_id, "items": items}


@app.post("/order/create")
def create_order(user_id: str = Depends(get_current_user)):
    cart_items = list(cart_collection.find({"user_id": user_id}, {"_id": 0}))
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = 0.0
    enriched_items = []
    for item in cart_items:
        response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{item['product_id']}", timeout=5)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Product unavailable: {item['product_id']}")
        product = response.json()
        subtotal = float(product["price"]) * item["quantity"]
        total_amount += subtotal
        enriched_items.append({**item, "price": product["price"], "name": product["name"]})

    order_id = str(orders_collection.count_documents({}) + 1)
    order = {
        "order_id": order_id,
        "user_id": user_id,
        "items": enriched_items,
        "total_amount": round(total_amount, 2),
        "timestamp": datetime.utcnow().isoformat(),
        "order_reference_id": str(uuid.uuid4()),
    }
    orders_collection.insert_one(order)
    cart_collection.delete_many({"user_id": user_id})
    return {"message": "Order created", "order": order}


@app.get("/orders")
def get_orders(user_id: str = Depends(get_current_user)):
    orders = list(orders_collection.find({"user_id": user_id}, {"_id": 0}))
    return {"orders": orders}
