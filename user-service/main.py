import os
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient

app = FastAPI(title="User Service", version="1.0.0")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "blinkit")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload.update({"exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)})
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate token") from exc

    user = users_collection.find_one({"user_id": user_id}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.get("/health")
def health():
    return {"status": "ok", "service": "user-service"}


@app.post("/register")
def register(payload: RegisterRequest):
    if users_collection.find_one({"email": payload.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(users_collection.count_documents({}) + 1)
    user = {
        "user_id": user_id,
        "name": payload.name,
        "email": payload.email,
        "password": hash_password(payload.password),
        "created_at": datetime.utcnow().isoformat(),
    }
    users_collection.insert_one(user)
    return {"message": "User registered successfully", "user_id": user_id}


@app.post("/login")
def login(payload: LoginRequest):
    user = users_collection.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": user["user_id"], "email": user["email"]})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/profile")
def profile(current_user: dict = Depends(get_current_user)):
    return current_user
