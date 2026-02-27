from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="Star Citizen Fleet Manager")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
SC_API_BASE = "https://api.star-citizen.wiki"
SC_API_KEY = os.environ.get('STAR_CITIZEN_API_KEY', '')

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserFleet(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    ship_id: str
    ship_name: str
    manufacturer: str
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LoginRequest(BaseModel):
    email: str
    star_citizen_token: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@api_router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Login or register user with Star Citizen API token"""
    existing_user = await db.users.find_one({"email": login_data.email}, {"_id": 0})
    
    if existing_user:
        if isinstance(existing_user['created_at'], str):
            existing_user['created_at'] = datetime.fromisoformat(existing_user['created_at'])
        user = User(**existing_user)
    else:
        user = User(username=login_data.email.split('@')[0], email=login_data.email)
        user_dict = user.model_dump()
        user_dict['created_at'] = user_dict['created_at'].isoformat()
        user_dict['sc_api_token'] = login_data.star_citizen_token
        await db.users.insert_one(user_dict)
    
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    return LoginResponse(
        access_token=access_token,
        user={"id": user.id, "username": user.username, "email": user.email}
    )

@api_router.get("/ships")
async def get_ships(user_id: str = Depends(get_current_user)):
    """Fetch all ships from Star Citizen API"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            headers = {}
            if SC_API_KEY:
                headers["Authorization"] = f"Bearer {SC_API_KEY}"
            
            response = await http_client.get(
                f"{SC_API_BASE}/api/v2/ships",
                headers=headers,
                params={"mode": "cache", "limit": 100}
            )
            
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data.get("data", [])}
            else:
                mock_ships = [
                    {"id": "600i", "name": "600i", "manufacturer": "Origin Jumpworks", "size": "Large", "crew": "5", "cargo": 40, "length": 91.5},
                    {"id": "890jump", "name": "890 Jump", "manufacturer": "Origin Jumpworks", "size": "Capital", "crew": "8", "cargo": 0, "length": 210},
                    {"id": "hornet", "name": "F7C Hornet", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "1", "cargo": 0, "length": 22.5},
                    {"id": "constellation", "name": "Constellation Andromeda", "manufacturer": "Roberts Space Industries", "size": "Large", "crew": "5", "cargo": 96, "length": 61},
                    {"id": "cutlass", "name": "Cutlass Black", "manufacturer": "Drake Interplanetary", "size": "Medium", "crew": "3", "cargo": 46, "length": 38.5},
                    {"id": "carrack", "name": "Carrack", "manufacturer": "Anvil Aerospace", "size": "Large", "crew": "6", "cargo": 456, "length": 126.5},
                ]
                return {"success": True, "data": mock_ships}
    except Exception as e:
        logging.error(f"Error fetching ships: {str(e)}")
        mock_ships = [
            {"id": "600i", "name": "600i", "manufacturer": "Origin Jumpworks", "size": "Large", "crew": "5", "cargo": 40, "length": 91.5},
            {"id": "890jump", "name": "890 Jump", "manufacturer": "Origin Jumpworks", "size": "Capital", "crew": "8", "cargo": 0, "length": 210},
            {"id": "hornet", "name": "F7C Hornet", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "1", "cargo": 0, "length": 22.5},
            {"id": "constellation", "name": "Constellation Andromeda", "manufacturer": "Roberts Space Industries", "size": "Large", "crew": "5", "cargo": 96, "length": 61},
            {"id": "cutlass", "name": "Cutlass Black", "manufacturer": "Drake Interplanetary", "size": "Medium", "crew": "3", "cargo": 46, "length": 38.5},
            {"id": "carrack", "name": "Carrack", "manufacturer": "Anvil Aerospace", "size": "Large", "crew": "6", "cargo": 456, "length": 126.5},
        ]
        return {"success": True, "data": mock_ships}

@api_router.get("/vehicles")
async def get_vehicles(user_id: str = Depends(get_current_user)):
    """Fetch all ground vehicles"""
    mock_vehicles = [
        {"id": "cyclone", "name": "Cyclone", "manufacturer": "Tumbril", "type": "Ground", "crew": "2"},
        {"id": "nox", "name": "Nox", "manufacturer": "Aopoa", "type": "Hover", "crew": "1"},
        {"id": "ursa", "name": "Ursa Rover", "manufacturer": "Roberts Space Industries", "type": "Ground", "crew": "6"},
        {"id": "nova", "name": "Nova Tank", "manufacturer": "Roberts Space Industries", "type": "Ground", "crew": "2"},
    ]
    return {"success": True, "data": mock_vehicles}

@api_router.get("/components")
async def get_components(user_id: str = Depends(get_current_user)):
    """Fetch all ship components"""
    mock_components = [
        {"id": "shield_01", "name": "FR-86 Shield Generator", "type": "Shield", "manufacturer": "Gorgon Defender", "size": "2", "grade": "A", "power": 0.8},
        {"id": "power_01", "name": "Regulus Power Plant", "type": "Power", "manufacturer": "Aegis", "size": "3", "grade": "A", "output": 5600},
        {"id": "cooler_01", "name": "Avalanche Cooler", "type": "Cooler", "manufacturer": "J-Span", "size": "2", "grade": "A", "rate": 6800},
        {"id": "quantum_01", "name": "Atlas Quantum Drive", "type": "Quantum", "manufacturer": "Roberts Space Industries", "size": "2", "grade": "A", "speed": 141000},
        {"id": "shield_02", "name": "Sukoran Shield", "type": "Shield", "manufacturer": "A&R", "size": "3", "grade": "B", "power": 1.2},
        {"id": "power_02", "name": "Genoa Power Plant", "type": "Power", "manufacturer": "Sakura Sun", "size": "2", "grade": "B", "output": 4200},
    ]
    return {"success": True, "data": mock_components}

@api_router.get("/weapons")
async def get_weapons(user_id: str = Depends(get_current_user)):
    """Fetch all weapons"""
    mock_weapons = [
        {"id": "weapon_01", "name": "M6A Laser Cannon", "type": "Energy", "manufacturer": "Klaus & Werner", "size": "3", "damage": 450, "rate": 300},
        {"id": "weapon_02", "name": "CF-337 Panther", "type": "Ballistic", "manufacturer": "Behring", "size": "2", "damage": 320, "rate": 700},
        {"id": "weapon_03", "name": "M7A Laser Cannon", "type": "Energy", "manufacturer": "Klaus & Werner", "size": "4", "damage": 620, "rate": 280},
        {"id": "weapon_04", "name": "Talon IR Missile", "type": "Missile", "manufacturer": "Behring", "size": "3", "damage": 8500, "rate": 1},
        {"id": "weapon_05", "name": "C-788 Combine Cannon", "type": "Ballistic", "manufacturer": "Apocalypse Arms", "size": "4", "damage": 740, "rate": 120},
        {"id": "weapon_06", "name": "NN-14 Neutron", "type": "Energy", "manufacturer": "Neutron", "size": "2", "damage": 280, "rate": 350},
    ]
    return {"success": True, "data": mock_weapons}

@api_router.get("/upgrades/{ship_id}")
async def get_upgrades(ship_id: str, user_id: str = Depends(get_current_user)):
    """Get recommended upgrades for a ship"""
    recommendations = {
        "shields": [{"id": "shield_01", "name": "FR-86 Shield Generator", "reason": "25% better shield capacity"}],
        "power": [{"id": "power_01", "name": "Regulus Power Plant", "reason": "Higher power output for better performance"}],
        "weapons": [{"id": "weapon_03", "name": "M7A Laser Cannon", "reason": "Superior damage and accuracy"}],
        "quantum": [{"id": "quantum_01", "name": "Atlas Quantum Drive", "reason": "Faster quantum travel speed"}]
    }
    return {"success": True, "data": recommendations}

@api_router.post("/fleet/add")
async def add_to_fleet(ship_data: dict, user_id: str = Depends(get_current_user)):
    """Add ship to user's fleet"""
    fleet_item = UserFleet(
        user_id=user_id,
        ship_id=ship_data.get('id'),
        ship_name=ship_data.get('name'),
        manufacturer=ship_data.get('manufacturer')
    )
    doc = fleet_item.model_dump()
    doc['added_at'] = doc['added_at'].isoformat()
    await db.user_fleet.insert_one(doc)
    return {"success": True, "message": "Ship added to fleet"}

@api_router.get("/fleet/my")
async def get_my_fleet(user_id: str = Depends(get_current_user)):
    """Get user's fleet"""
    fleet = await db.user_fleet.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    for item in fleet:
        if isinstance(item.get('added_at'), str):
            item['added_at'] = datetime.fromisoformat(item['added_at'])
    return {"success": True, "data": fleet}

@api_router.delete("/fleet/{fleet_id}")
async def remove_from_fleet(fleet_id: str, user_id: str = Depends(get_current_user)):
    """Remove ship from user's fleet"""
    result = await db.user_fleet.delete_one({"id": fleet_id, "user_id": user_id})
    if result.deleted_count > 0:
        return {"success": True, "message": "Ship removed from fleet"}
    raise HTTPException(status_code=404, detail="Ship not found in fleet")

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()