import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from pymongo import MongoClient

app = FastAPI(title="Product Catalog Service", version="1.0.0")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "blinkit")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
products_collection = db["products"]


def seed_products():
    if products_collection.count_documents({}) > 0:
        return
    sample_products = [
        {
            "product_id": "p1",
            "name": "Fresh Milk 1L",
            "description": "Full cream milk",
            "price": 65.0,
            "category": "Dairy",
            "image_url": "https://via.placeholder.com/150",
            "availability": True,
        },
        {
            "product_id": "p2",
            "name": "Brown Bread",
            "description": "Whole wheat bread",
            "price": 40.0,
            "category": "Bakery",
            "image_url": "https://via.placeholder.com/150",
            "availability": True,
        },
        {
            "product_id": "p3",
            "name": "Banana (6 pcs)",
            "description": "Fresh bananas",
            "price": 55.0,
            "category": "Fruits",
            "image_url": "https://via.placeholder.com/150",
            "availability": True,
        },
    ]
    products_collection.insert_many(sample_products)


@app.on_event("startup")
def startup_event():
    seed_products()


@app.get("/health")
def health():
    return {"status": "ok", "service": "product-service"}


@app.get("/products")
def get_products(category: Optional[str] = None):
    query = {"category": category} if category else {}
    products = list(products_collection.find(query, {"_id": 0}))
    return {"products": products}


@app.get("/products/{product_id}")
def get_product(product_id: str):
    product = products_collection.find_one({"product_id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/categories")
def get_categories():
    categories = products_collection.distinct("category")
    return {"categories": categories}
