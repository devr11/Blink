import os
from datetime import datetime

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI(title="Delivery Status Service", version="1.0.0")

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

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
delivery_collection = db["delivery_status"]

STATUS_FLOW = ["PLACED", "PACKED", "OUT_FOR_DELIVERY", "DELIVERED"]


class StatusUpdateRequest(BaseModel):
    current_status: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "delivery-service"}


@app.get("/order/{order_id}/status")
def get_order_status(order_id: str):
    status_data = delivery_collection.find_one({"order_id": order_id}, {"_id": 0})
    if not status_data:
        status_data = {
            "order_id": order_id,
            "current_status": "PLACED",
            "last_updated": datetime.utcnow().isoformat(),
        }
        delivery_collection.insert_one(status_data)
    return status_data


@app.post("/order/{order_id}/update-status")
def update_order_status(order_id: str, payload: StatusUpdateRequest):
    if payload.current_status not in STATUS_FLOW:
        raise HTTPException(status_code=400, detail=f"Status must be one of {STATUS_FLOW}")

    existing = delivery_collection.find_one({"order_id": order_id})
    if existing:
        current_idx = STATUS_FLOW.index(existing["current_status"])
        new_idx = STATUS_FLOW.index(payload.current_status)
        if new_idx < current_idx:
            raise HTTPException(status_code=400, detail="Cannot move status backward")

    updated = {
        "order_id": order_id,
        "current_status": payload.current_status,
        "last_updated": datetime.utcnow().isoformat(),
    }
    delivery_collection.update_one({"order_id": order_id}, {"$set": updated}, upsert=True)
    return {"message": "Status updated", "data": updated}
