from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import bcrypt

from deps import db, User, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/register", response_model=LoginResponse)
async def register(data: RegisterRequest):
    existing = await db.users.find_one({"username": data.username}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
    user = User(username=data.username, email=f"{data.username}@fleet.local")
    user_dict = user.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    user_dict['password_hash'] = hashed
    await db.users.insert_one(user_dict)

    access_token = create_access_token(data={"sub": user.id})
    return LoginResponse(
        access_token=access_token,
        user={"id": user.id, "username": user.username}
    )


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    existing_user = await db.users.find_one({"username": login_data.username}, {"_id": 0})

    if existing_user:
        stored_hash = existing_user.get('password_hash', '')
        if stored_hash and bcrypt.checkpw(login_data.password.encode(), stored_hash.encode()):
            if isinstance(existing_user['created_at'], str):
                existing_user['created_at'] = datetime.fromisoformat(existing_user['created_at'])
            user = User(**existing_user)
        else:
            raise HTTPException(status_code=401, detail="Invalid password")
    else:
        hashed = bcrypt.hashpw(login_data.password.encode(), bcrypt.gensalt()).decode()
        user = User(username=login_data.username, email=f"{login_data.username}@fleet.local")
        user_dict = user.model_dump()
        user_dict['created_at'] = user_dict['created_at'].isoformat()
        user_dict['password_hash'] = hashed
        await db.users.insert_one(user_dict)

    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    return LoginResponse(
        access_token=access_token,
        user={"id": user.id, "username": user.username, "email": user.email}
    )
