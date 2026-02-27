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
from ship_data_enhancer import enhance_ship_data, get_vehicle_image

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
                ships = enhance_ship_data(data.get("data", []))
                return {"success": True, "data": ships}
            else:
                ships = enhance_ship_data(get_comprehensive_ship_list())
                return {"success": True, "data": ships}
    except Exception as e:
        logging.error(f"Error fetching ships: {str(e)}")
        ships = enhance_ship_data(get_comprehensive_ship_list())
        return {"success": True, "data": ships}

def get_comprehensive_ship_list():
    """Comprehensive list of Star Citizen ships"""
    return [
        # Origin Jumpworks
        {"id": "85x", "name": "85X", "manufacturer": "Origin Jumpworks", "size": "Snub", "crew": "1", "cargo": 0, "length": 12.5},
        {"id": "100i", "name": "100i", "manufacturer": "Origin Jumpworks", "size": "Small", "crew": "1", "cargo": 2, "length": 20},
        {"id": "125a", "name": "125a", "manufacturer": "Origin Jumpworks", "size": "Small", "crew": "1", "cargo": 2, "length": 20},
        {"id": "135c", "name": "135c", "manufacturer": "Origin Jumpworks", "size": "Small", "crew": "1", "cargo": 6, "length": 20},
        {"id": "300i", "name": "300i", "manufacturer": "Origin Jumpworks", "size": "Small", "crew": "1", "cargo": 8, "length": 27},
        {"id": "315p", "name": "315p", "manufacturer": "Origin Jumpworks", "size": "Small", "crew": "1", "cargo": 12, "length": 27},
        {"id": "325a", "name": "325a", "manufacturer": "Origin Jumpworks", "size": "Small", "crew": "1", "cargo": 4, "length": 27},
        {"id": "350r", "name": "350r", "manufacturer": "Origin Jumpworks", "size": "Small", "crew": "1", "cargo": 0, "length": 27},
        {"id": "400i", "name": "400i", "manufacturer": "Origin Jumpworks", "size": "Medium", "crew": "3", "cargo": 42, "length": 60},
        {"id": "600i", "name": "600i Explorer", "manufacturer": "Origin Jumpworks", "size": "Large", "crew": "5", "cargo": 40, "length": 91.5},
        {"id": "600i-touring", "name": "600i Touring", "manufacturer": "Origin Jumpworks", "size": "Large", "crew": "5", "cargo": 16, "length": 91.5},
        {"id": "890jump", "name": "890 Jump", "manufacturer": "Origin Jumpworks", "size": "Capital", "crew": "8", "cargo": 0, "length": 210},
        
        # Anvil Aerospace
        {"id": "arrow", "name": "Arrow", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "1", "cargo": 0, "length": 16},
        {"id": "hawk", "name": "Hawk", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "1", "cargo": 0, "length": 16},
        {"id": "hornet-f7c", "name": "F7C Hornet", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "1", "cargo": 0, "length": 22.5},
        {"id": "hornet-f7cm", "name": "F7C-M Super Hornet", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "2", "cargo": 0, "length": 22.5},
        {"id": "hornet-f7cs", "name": "F7C-S Hornet Ghost", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "1", "cargo": 0, "length": 22.5},
        {"id": "hornet-f7a", "name": "F7A Hornet (Military)", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "1", "cargo": 0, "length": 22.5},
        {"id": "gladiator", "name": "Gladiator", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "2", "cargo": 0, "length": 24},
        {"id": "hurricane", "name": "Hurricane", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "2", "cargo": 0, "length": 22},
        {"id": "terrapin", "name": "Terrapin", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "1", "cargo": 0, "length": 20},
        {"id": "valkyrie", "name": "Valkyrie", "manufacturer": "Anvil Aerospace", "size": "Large", "crew": "5", "cargo": 30, "length": 46.5},
        {"id": "carrack", "name": "Carrack", "manufacturer": "Anvil Aerospace", "size": "Large", "crew": "6", "cargo": 456, "length": 126.5},
        {"id": "liberator", "name": "Liberator", "manufacturer": "Anvil Aerospace", "size": "Large", "crew": "6", "cargo": 400, "length": 163},
        {"id": "crucible", "name": "Crucible", "manufacturer": "Anvil Aerospace", "size": "Large", "crew": "6", "cargo": 230, "length": 95},
        
        # Roberts Space Industries (RSI)
        {"id": "aurora-ln", "name": "Aurora LN", "manufacturer": "Roberts Space Industries", "size": "Small", "crew": "1", "cargo": 3, "length": 18.5},
        {"id": "aurora-mr", "name": "Aurora MR", "manufacturer": "Roberts Space Industries", "size": "Small", "crew": "1", "cargo": 3, "length": 18.5},
        {"id": "aurora-cl", "name": "Aurora CL", "manufacturer": "Roberts Space Industries", "size": "Small", "crew": "1", "cargo": 6, "length": 18.5},
        {"id": "aurora-lx", "name": "Aurora LX", "manufacturer": "Roberts Space Industries", "size": "Small", "crew": "1", "cargo": 3, "length": 18.5},
        {"id": "aurora-es", "name": "Aurora ES", "manufacturer": "Roberts Space Industries", "size": "Small", "crew": "1", "cargo": 3, "length": 18.5},
        {"id": "mantis", "name": "Mantis", "manufacturer": "Roberts Space Industries", "size": "Small", "crew": "1", "cargo": 0, "length": 28},
        {"id": "scorpius", "name": "Scorpius", "manufacturer": "Roberts Space Industries", "size": "Medium", "crew": "2", "cargo": 0, "length": 27},
        {"id": "constellation-andromeda", "name": "Constellation Andromeda", "manufacturer": "Roberts Space Industries", "size": "Large", "crew": "5", "cargo": 96, "length": 61},
        {"id": "constellation-aquila", "name": "Constellation Aquila", "manufacturer": "Roberts Space Industries", "size": "Large", "crew": "5", "cargo": 96, "length": 61},
        {"id": "constellation-taurus", "name": "Constellation Taurus", "manufacturer": "Roberts Space Industries", "size": "Large", "crew": "5", "cargo": 174, "length": 61},
        {"id": "constellation-phoenix", "name": "Constellation Phoenix", "manufacturer": "Roberts Space Industries", "size": "Large", "crew": "5", "cargo": 96, "length": 61},
        {"id": "perseus", "name": "Perseus", "manufacturer": "Roberts Space Industries", "size": "Large", "crew": "6", "cargo": 500, "length": 100},
        {"id": "polaris", "name": "Polaris", "manufacturer": "Roberts Space Industries", "size": "Capital", "crew": "14", "cargo": 216, "length": 155},
        {"id": "galaxy", "name": "Galaxy", "manufacturer": "Roberts Space Industries", "size": "Capital", "crew": "12", "cargo": 1088, "length": 115},
        
        # Aegis Dynamics
        {"id": "avenger-titan", "name": "Avenger Titan", "manufacturer": "Aegis Dynamics", "size": "Small", "crew": "1", "cargo": 8, "length": 22.5},
        {"id": "avenger-stalker", "name": "Avenger Stalker", "manufacturer": "Aegis Dynamics", "size": "Small", "crew": "1", "cargo": 0, "length": 22.5},
        {"id": "avenger-warlock", "name": "Avenger Warlock", "manufacturer": "Aegis Dynamics", "size": "Small", "crew": "1", "cargo": 0, "length": 22.5},
        {"id": "sabre", "name": "Sabre", "manufacturer": "Aegis Dynamics", "size": "Small", "crew": "1", "cargo": 0, "length": 24},
        {"id": "sabre-comet", "name": "Sabre Comet", "manufacturer": "Aegis Dynamics", "size": "Small", "crew": "1", "cargo": 0, "length": 24},
        {"id": "gladius", "name": "Gladius", "manufacturer": "Aegis Dynamics", "size": "Small", "crew": "1", "cargo": 0, "length": 20},
        {"id": "vanguard-warden", "name": "Vanguard Warden", "manufacturer": "Aegis Dynamics", "size": "Medium", "crew": "2", "cargo": 0, "length": 38},
        {"id": "vanguard-sentinel", "name": "Vanguard Sentinel", "manufacturer": "Aegis Dynamics", "size": "Medium", "crew": "2", "cargo": 0, "length": 38},
        {"id": "vanguard-harbinger", "name": "Vanguard Harbinger", "manufacturer": "Aegis Dynamics", "size": "Medium", "crew": "2", "cargo": 0, "length": 38},
        {"id": "vanguard-hoplite", "name": "Vanguard Hoplite", "manufacturer": "Aegis Dynamics", "size": "Medium", "crew": "2", "cargo": 0, "length": 38},
        {"id": "eclipse", "name": "Eclipse", "manufacturer": "Aegis Dynamics", "size": "Small", "crew": "1", "cargo": 0, "length": 30},
        {"id": "retaliator", "name": "Retaliator Bomber", "manufacturer": "Aegis Dynamics", "size": "Large", "crew": "7", "cargo": 0, "length": 70.5},
        {"id": "redeemer", "name": "Redeemer", "manufacturer": "Aegis Dynamics", "size": "Medium", "crew": "5", "cargo": 0, "length": 46},
        {"id": "hammerhead", "name": "Hammerhead", "manufacturer": "Aegis Dynamics", "size": "Large", "crew": "11", "cargo": 40, "length": 102},
        {"id": "reclaimer", "name": "Reclaimer", "manufacturer": "Aegis Dynamics", "size": "Large", "crew": "7", "cargo": 180, "length": 158},
        {"id": "nautilus", "name": "Nautilus", "manufacturer": "Aegis Dynamics", "size": "Large", "crew": "6", "cargo": 0, "length": 95},
        {"id": "idris-p", "name": "Idris-P", "manufacturer": "Aegis Dynamics", "size": "Capital", "crew": "28", "cargo": 995, "length": 242},
        {"id": "idris-m", "name": "Idris-M", "manufacturer": "Aegis Dynamics", "size": "Capital", "crew": "28", "cargo": 819, "length": 242},
        {"id": "javelin", "name": "Javelin", "manufacturer": "Aegis Dynamics", "size": "Capital", "crew": "80", "cargo": 5400, "length": 480},
        
        # Drake Interplanetary
        {"id": "dragonfly-black", "name": "Dragonfly Black", "manufacturer": "Drake Interplanetary", "size": "Snub", "crew": "1", "cargo": 0, "length": 6.3},
        {"id": "dragonfly-yellow", "name": "Dragonfly Yellowjacket", "manufacturer": "Drake Interplanetary", "size": "Snub", "crew": "1", "cargo": 0, "length": 6.3},
        {"id": "buccaneer", "name": "Buccaneer", "manufacturer": "Drake Interplanetary", "size": "Small", "crew": "1", "cargo": 0, "length": 24},
        {"id": "herald", "name": "Herald", "manufacturer": "Drake Interplanetary", "size": "Small", "crew": "1", "cargo": 0, "length": 24},
        {"id": "cutlass-black", "name": "Cutlass Black", "manufacturer": "Drake Interplanetary", "size": "Medium", "crew": "3", "cargo": 46, "length": 38.5},
        {"id": "cutlass-red", "name": "Cutlass Red", "manufacturer": "Drake Interplanetary", "size": "Medium", "crew": "3", "cargo": 10, "length": 38.5},
        {"id": "cutlass-blue", "name": "Cutlass Blue", "manufacturer": "Drake Interplanetary", "size": "Medium", "crew": "3", "cargo": 10, "length": 38.5},
        {"id": "corsair", "name": "Corsair", "manufacturer": "Drake Interplanetary", "size": "Large", "crew": "4", "cargo": 72, "length": 52},
        {"id": "caterpillar", "name": "Caterpillar", "manufacturer": "Drake Interplanetary", "size": "Large", "crew": "5", "cargo": 576, "length": 111},
        {"id": "vulture", "name": "Vulture", "manufacturer": "Drake Interplanetary", "size": "Medium", "crew": "1", "cargo": 12, "length": 32},
        {"id": "kraken", "name": "Kraken", "manufacturer": "Drake Interplanetary", "size": "Capital", "crew": "10", "cargo": 3792, "length": 270},
        
        # Crusader Industries
        {"id": "ares-ion", "name": "Ares Ion", "manufacturer": "Crusader Industries", "size": "Medium", "crew": "1", "cargo": 0, "length": 30},
        {"id": "ares-inferno", "name": "Ares Inferno", "manufacturer": "Crusader Industries", "size": "Medium", "crew": "1", "cargo": 0, "length": 30},
        {"id": "spirit-a1", "name": "Spirit A1", "manufacturer": "Crusader Industries", "size": "Medium", "crew": "2", "cargo": 48, "length": 42},
        {"id": "spirit-c1", "name": "Spirit C1", "manufacturer": "Crusader Industries", "size": "Medium", "crew": "2", "cargo": 96, "length": 42},
        {"id": "mercury", "name": "Mercury Star Runner", "manufacturer": "Crusader Industries", "size": "Large", "crew": "3", "cargo": 114, "length": 66},
        {"id": "starlifter-m2", "name": "M2 Hercules", "manufacturer": "Crusader Industries", "size": "Large", "crew": "4", "cargo": 468, "length": 94},
        {"id": "starlifter-c2", "name": "C2 Hercules", "manufacturer": "Crusader Industries", "size": "Large", "crew": "4", "cargo": 696, "length": 94},
        {"id": "starlifter-a2", "name": "A2 Hercules", "manufacturer": "Crusader Industries", "size": "Large", "crew": "4", "cargo": 234, "length": 94},
        {"id": "genesis", "name": "Genesis Starliner", "manufacturer": "Crusader Industries", "size": "Large", "crew": "5", "cargo": 0, "length": 85},
        {"id": "odyssey", "name": "Odyssey", "manufacturer": "Crusader Industries", "size": "Large", "crew": "6", "cargo": 252, "length": 140},
        
        # Misc
        {"id": "prospector", "name": "Prospector", "manufacturer": "MISC", "size": "Small", "crew": "1", "cargo": 32, "length": 31},
        {"id": "razor", "name": "Razor", "manufacturer": "MISC", "size": "Small", "crew": "1", "cargo": 0, "length": 13},
        {"id": "reliant-kore", "name": "Reliant Kore", "manufacturer": "MISC", "size": "Small", "crew": "2", "cargo": 6, "length": 28.5},
        {"id": "reliant-tana", "name": "Reliant Tana", "manufacturer": "MISC", "size": "Small", "crew": "2", "cargo": 0, "length": 28.5},
        {"id": "reliant-sen", "name": "Reliant Sen", "manufacturer": "MISC", "size": "Small", "crew": "2", "cargo": 2, "length": 28.5},
        {"id": "reliant-mako", "name": "Reliant Mako", "manufacturer": "MISC", "size": "Small", "crew": "2", "cargo": 0, "length": 28.5},
        {"id": "freelancer", "name": "Freelancer", "manufacturer": "MISC", "size": "Medium", "crew": "4", "cargo": 66, "length": 38},
        {"id": "freelancer-dur", "name": "Freelancer DUR", "manufacturer": "MISC", "size": "Medium", "crew": "4", "cargo": 36, "length": 38},
        {"id": "freelancer-max", "name": "Freelancer MAX", "manufacturer": "MISC", "size": "Medium", "crew": "4", "cargo": 120, "length": 38},
        {"id": "freelancer-mis", "name": "Freelancer MIS", "manufacturer": "MISC", "size": "Medium", "crew": "4", "cargo": 36, "length": 38},
        {"id": "hull-a", "name": "Hull A", "manufacturer": "MISC", "size": "Small", "crew": "1", "cargo": 48, "length": 22},
        {"id": "hull-b", "name": "Hull B", "manufacturer": "MISC", "size": "Medium", "crew": "2", "cargo": 384, "length": 49.5},
        {"id": "hull-c", "name": "Hull C", "manufacturer": "MISC", "size": "Large", "crew": "3", "cargo": 4608, "length": 132},
        {"id": "starfarer", "name": "Starfarer", "manufacturer": "MISC", "size": "Large", "crew": "6", "cargo": 291, "length": 101},
        {"id": "starfarer-gemini", "name": "Starfarer Gemini", "manufacturer": "MISC", "size": "Large", "crew": "6", "cargo": 291, "length": 101},
        {"id": "endeavor", "name": "Endeavor", "manufacturer": "MISC", "size": "Capital", "crew": "16", "cargo": 500, "length": 200},
        
        # Aopoa
        {"id": "nox", "name": "Nox", "manufacturer": "Aopoa", "size": "Snub", "crew": "1", "cargo": 0, "length": 7.25},
        {"id": "nox-kue", "name": "Nox Kue", "manufacturer": "Aopoa", "size": "Snub", "crew": "1", "cargo": 0, "length": 7.25},
        {"id": "khartu-al", "name": "Khartu-Al", "manufacturer": "Aopoa", "size": "Small", "crew": "1", "cargo": 0, "length": 16},
        {"id": "san-tok-yai", "name": "San'tok.yāi", "manufacturer": "Aopoa", "size": "Medium", "crew": "1", "cargo": 0, "length": 35},
        
        # Banu
        {"id": "defender", "name": "Defender", "manufacturer": "Banu", "size": "Small", "crew": "2", "cargo": 0, "length": 26},
        {"id": "merchantman", "name": "Merchantman", "manufacturer": "Banu", "size": "Large", "crew": "8", "cargo": 3584, "length": 160},
        
        # Esperia (Alien reproductions)
        {"id": "blade", "name": "Blade", "manufacturer": "Esperia", "size": "Small", "crew": "1", "cargo": 0, "length": 26},
        {"id": "glaive", "name": "Glaive", "manufacturer": "Esperia", "size": "Small", "crew": "1", "cargo": 0, "length": 32},
        {"id": "prowler", "name": "Prowler", "manufacturer": "Esperia", "size": "Medium", "crew": "5", "cargo": 0, "length": 34},
        {"id": "talon", "name": "Talon", "manufacturer": "Esperia", "size": "Small", "crew": "1", "cargo": 0, "length": 22},
        {"id": "talon-shrike", "name": "Talon Shrike", "manufacturer": "Esperia", "size": "Small", "crew": "1", "cargo": 0, "length": 22},
        
        # Argo Astronautics
        {"id": "mpuv-cargo", "name": "MPUV Cargo", "manufacturer": "Argo Astronautics", "size": "Snub", "crew": "1", "cargo": 2, "length": 9.5},
        {"id": "mpuv-personnel", "name": "MPUV Personnel", "manufacturer": "Argo Astronautics", "size": "Snub", "crew": "1", "cargo": 0, "length": 9.5},
        {"id": "mole", "name": "MOLE", "manufacturer": "Argo Astronautics", "size": "Large", "crew": "4", "cargo": 96, "length": 55},
        {"id": "raft", "name": "RAFT", "manufacturer": "Argo Astronautics", "size": "Medium", "crew": "2", "cargo": 96, "length": 38},
        
        # CNOU (Consolidated Outland)
        {"id": "mustang-alpha", "name": "Mustang Alpha", "manufacturer": "Consolidated Outland", "size": "Small", "crew": "1", "cargo": 6, "length": 19},
        {"id": "mustang-beta", "name": "Mustang Beta", "manufacturer": "Consolidated Outland", "size": "Small", "crew": "1", "cargo": 0, "length": 19},
        {"id": "mustang-gamma", "name": "Mustang Gamma", "manufacturer": "Consolidated Outland", "size": "Small", "crew": "1", "cargo": 0, "length": 19},
        {"id": "mustang-delta", "name": "Mustang Delta", "manufacturer": "Consolidated Outland", "size": "Small", "crew": "1", "cargo": 0, "length": 19},
        {"id": "mustang-omega", "name": "Mustang Omega", "manufacturer": "Consolidated Outland", "size": "Small", "crew": "1", "cargo": 0, "length": 19},
        {"id": "nomad", "name": "Nomad", "manufacturer": "Consolidated Outland", "size": "Small", "crew": "1", "cargo": 24, "length": 26},
        {"id": "pioneer", "name": "Pioneer", "manufacturer": "Consolidated Outland", "size": "Capital", "crew": "6", "cargo": 500, "length": 140},
    ]

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
    return {"success": True, "data": get_comprehensive_components_list()}

def get_comprehensive_components_list():
    """Comprehensive list of Star Citizen ship components"""
    return [
        # Shields - Size 1
        {"id": "shield_allstop", "name": "AllStop", "type": "Shield", "manufacturer": "Mirage", "size": "1", "grade": "A", "power": 0.5},
        {"id": "shield_shimmer", "name": "Shimmer", "type": "Shield", "manufacturer": "Mirage", "size": "1", "grade": "B", "power": 0.45},
        {"id": "shield_bulwark", "name": "Bulwark", "type": "Shield", "manufacturer": "A&R", "size": "1", "grade": "A", "power": 0.52},
        {"id": "shield_vanguard", "name": "Vanguard", "type": "Shield", "manufacturer": "Gorgon Defender", "size": "1", "grade": "C", "power": 0.48},
        
        # Shields - Size 2
        {"id": "shield_fr76", "name": "FR-76 Shield Generator", "type": "Shield", "manufacturer": "Gorgon Defender", "size": "2", "grade": "A", "power": 0.8},
        {"id": "shield_fr86", "name": "FR-86 Shield Generator", "type": "Shield", "manufacturer": "Gorgon Defender", "size": "2", "grade": "B", "power": 0.75},
        {"id": "shield_rampart", "name": "Rampart", "type": "Shield", "manufacturer": "Mirage", "size": "2", "grade": "A", "power": 0.85},
        {"id": "shield_palisade", "name": "Palisade", "type": "Shield", "manufacturer": "A&R", "size": "2", "grade": "B", "power": 0.78},
        {"id": "shield_stronghold", "name": "Stronghold", "type": "Shield", "manufacturer": "A&R", "size": "2", "grade": "C", "power": 0.72},
        
        # Shields - Size 3
        {"id": "shield_sukoran", "name": "Sukoran Shield", "type": "Shield", "manufacturer": "A&R", "size": "3", "grade": "A", "power": 1.2},
        {"id": "shield_guardian", "name": "Guardian", "type": "Shield", "manufacturer": "Gorgon Defender", "size": "3", "grade": "B", "power": 1.15},
        {"id": "shield_citadel", "name": "Citadel", "type": "Shield", "manufacturer": "Mirage", "size": "3", "grade": "A", "power": 1.25},
        {"id": "shield_fortress", "name": "Fortress", "type": "Shield", "manufacturer": "A&R", "size": "3", "grade": "C", "power": 1.1},
        
        # Power Plants - Size 1
        {"id": "power_breton", "name": "Breton", "type": "Power", "manufacturer": "Sakura Sun", "size": "1", "grade": "A", "output": 3200},
        {"id": "power_juno", "name": "Juno Starworks", "type": "Power", "manufacturer": "Juno Starworks", "size": "1", "grade": "B", "output": 3000},
        {"id": "power_lightfire", "name": "Lightfire", "type": "Power", "manufacturer": "Aegis", "size": "1", "grade": "C", "output": 2800},
        
        # Power Plants - Size 2
        {"id": "power_genoa", "name": "Genoa", "type": "Power", "manufacturer": "Sakura Sun", "size": "2", "grade": "A", "output": 4200},
        {"id": "power_beacon", "name": "Beacon", "type": "Power", "manufacturer": "Tyler Design", "size": "2", "grade": "B", "output": 4000},
        {"id": "power_slipstream", "name": "Slipstream", "type": "Power", "manufacturer": "Wen/Cassel", "size": "2", "grade": "C", "output": 3800},
        
        # Power Plants - Size 3
        {"id": "power_regulus", "name": "Regulus", "type": "Power", "manufacturer": "Aegis", "size": "3", "grade": "A", "output": 5600},
        {"id": "power_maelstrom", "name": "Maelstrom", "type": "Power", "manufacturer": "Lightning Power", "size": "3", "grade": "B", "output": 5400},
        {"id": "power_quadracell", "name": "Quadracell", "type": "Power", "manufacturer": "Tyler Design", "size": "3", "grade": "C", "output": 5200},
        
        # Coolers - Size 1
        {"id": "cooler_frost", "name": "Frost-Star", "type": "Cooler", "manufacturer": "J-Span", "size": "1", "grade": "A", "rate": 4200},
        {"id": "cooler_polar", "name": "Polar", "type": "Cooler", "manufacturer": "Seal Corp", "size": "1", "grade": "B", "rate": 4000},
        {"id": "cooler_thermal", "name": "ThermalCore", "type": "Cooler", "manufacturer": "ACOM", "size": "1", "grade": "C", "rate": 3800},
        
        # Coolers - Size 2
        {"id": "cooler_avalanche", "name": "Avalanche", "type": "Cooler", "manufacturer": "J-Span", "size": "2", "grade": "A", "rate": 6800},
        {"id": "cooler_zero", "name": "Zero-Rush", "type": "Cooler", "manufacturer": "Seal Corp", "size": "2", "grade": "B", "rate": 6500},
        {"id": "cooler_arctic", "name": "ArcticStorm", "type": "Cooler", "manufacturer": "ACOM", "size": "2", "grade": "C", "rate": 6200},
        
        # Coolers - Size 3
        {"id": "cooler_blizzard", "name": "Blizzard", "type": "Cooler", "manufacturer": "J-Span", "size": "3", "grade": "A", "rate": 8800},
        {"id": "cooler_icecream", "name": "Ice-Scream", "type": "Cooler", "manufacturer": "Seal Corp", "size": "3", "grade": "B", "rate": 8500},
        {"id": "cooler_cryo", "name": "CryoStar", "type": "Cooler", "manufacturer": "ACOM", "size": "3", "grade": "C", "rate": 8200},
        
        # Quantum Drives - Size 1
        {"id": "quantum_rush", "name": "Rush", "type": "Quantum", "manufacturer": "Aspro Hangar", "size": "1", "grade": "A", "speed": 121000},
        {"id": "quantum_yeager", "name": "Yeager", "type": "Quantum", "manufacturer": "Wei-Tek", "size": "1", "grade": "B", "speed": 115000},
        {"id": "quantum_voyage", "name": "Voyage", "type": "Quantum", "manufacturer": "Eos", "size": "1", "grade": "C", "speed": 110000},
        
        # Quantum Drives - Size 2
        {"id": "quantum_atlas", "name": "Atlas", "type": "Quantum", "manufacturer": "RSI", "size": "2", "grade": "A", "speed": 141000},
        {"id": "quantum_bolon", "name": "Bolon", "type": "Quantum", "manufacturer": "Borea", "size": "2", "grade": "B", "speed": 135000},
        {"id": "quantum_pontes", "name": "Pontes", "type": "Quantum", "manufacturer": "Agni", "size": "2", "grade": "C", "speed": 130000},
        
        # Quantum Drives - Size 3
        {"id": "quantum_vk00", "name": "VK-00", "type": "Quantum", "manufacturer": "Agni", "size": "3", "grade": "A", "speed": 161000},
        {"id": "quantum_crossfield", "name": "Crossfield", "type": "Quantum", "manufacturer": "Eos", "size": "3", "grade": "B", "speed": 155000},
        {"id": "quantum_beacon", "name": "Beacon", "type": "Quantum", "manufacturer": "Wei-Tek", "size": "3", "grade": "C", "speed": 150000},
        
        # Radars - Size 1
        {"id": "radar_hawk", "name": "Hawk-3", "type": "Radar", "manufacturer": "Talon Navigation", "size": "1", "grade": "A", "range": 8000},
        {"id": "radar_scout", "name": "Scout", "type": "Radar", "manufacturer": "Chimera Communications", "size": "1", "grade": "B", "range": 7500},
        
        # Radars - Size 2
        {"id": "radar_eagle", "name": "Eagle-Eye", "type": "Radar", "manufacturer": "Talon Navigation", "size": "2", "grade": "A", "range": 12000},
        {"id": "radar_optics", "name": "WideView Optics", "type": "Radar", "manufacturer": "Chimera Communications", "size": "2", "grade": "B", "range": 11000},
        
        # Radars - Size 3
        {"id": "radar_nightjar", "name": "Nightjar", "type": "Radar", "manufacturer": "Talon Navigation", "size": "3", "grade": "A", "range": 16000},
        {"id": "radar_sentinel", "name": "Sentinel", "type": "Radar", "manufacturer": "Chimera Communications", "size": "3", "grade": "B", "range": 15000},
    ]

@api_router.get("/weapons")
async def get_weapons(user_id: str = Depends(get_current_user)):
    """Fetch all weapons"""
    return {"success": True, "data": get_comprehensive_weapons_list()}

def get_comprehensive_weapons_list():
    """Comprehensive list of Star Citizen weapons"""
    return [
        # Energy Weapons - Size 1
        {"id": "weapon_badger", "name": "CF-117 Badger Repeater", "type": "Energy", "manufacturer": "Klaus & Werner", "size": "1", "damage": 38, "rate": 600},
        {"id": "weapon_attrition1", "name": "Attrition-1", "type": "Energy", "manufacturer": "Hurston Dynamics", "size": "1", "damage": 42, "rate": 550},
        {"id": "weapon_scorpion", "name": "Scorpion GT-215", "type": "Energy", "manufacturer": "Banu", "size": "1", "damage": 40, "rate": 580},
        {"id": "weapon_suckerpunch", "name": "Suckerpunch Distortion", "type": "Energy", "manufacturer": "Kastak Arms", "size": "1", "damage": 35, "rate": 620},
        
        # Energy Weapons - Size 2
        {"id": "weapon_panther", "name": "CF-227 Panther Repeater", "type": "Energy", "manufacturer": "Klaus & Werner", "size": "2", "damage": 62, "rate": 550},
        {"id": "weapon_attrition2", "name": "Attrition-2", "type": "Energy", "manufacturer": "Hurston Dynamics", "size": "2", "damage": 68, "rate": 500},
        {"id": "weapon_omnisky6", "name": "Omnisky VI", "type": "Energy", "manufacturer": "Klaus & Werner", "size": "2", "damage": 185, "rate": 180},
        {"id": "weapon_nn14", "name": "NN-14 Neutron Repeater", "type": "Energy", "manufacturer": "Neutron", "size": "2", "damage": 70, "rate": 350},
        
        # Energy Weapons - Size 3
        {"id": "weapon_m6a", "name": "M6A Laser Cannon", "type": "Energy", "manufacturer": "Klaus & Werner", "size": "3", "damage": 210, "rate": 300},
        {"id": "weapon_attrition3", "name": "Attrition-3", "type": "Energy", "manufacturer": "Hurston Dynamics", "size": "3", "damage": 225, "rate": 280},
        {"id": "weapon_omnisky9", "name": "Omnisky IX", "type": "Energy", "manufacturer": "Klaus & Werner", "size": "3", "damage": 305, "rate": 150},
        {"id": "weapon_nn13", "name": "NN-13 Neutron Cannon", "type": "Energy", "manufacturer": "Neutron", "size": "3", "damage": 240, "rate": 260},
        
        # Energy Weapons - Size 4
        {"id": "weapon_m7a", "name": "M7A Laser Cannon", "type": "Energy", "manufacturer": "Klaus & Werner", "size": "4", "damage": 350, "rate": 280},
        {"id": "weapon_attrition4", "name": "Attrition-4", "type": "Energy", "manufacturer": "Hurston Dynamics", "size": "4", "damage": 375, "rate": 260},
        {"id": "weapon_c788", "name": "C-788 Ballistic Cannon", "type": "Energy", "manufacturer": "Behring", "size": "4", "damage": 420, "rate": 200},
        
        # Ballistic Weapons - Size 1
        {"id": "weapon_s38", "name": "S-38 Pistol", "type": "Ballistic", "manufacturer": "Gemini", "size": "1", "damage": 50, "rate": 400, "ammo_per_mag": 60},
        {"id": "weapon_longsword", "name": "Longsword-1", "type": "Ballistic", "manufacturer": "Behring", "size": "1", "damage": 52, "rate": 380, "ammo_per_mag": 55},
        {"id": "weapon_sawbuck", "name": "Sawbuck Repeater", "type": "Ballistic", "manufacturer": "Gallenson Tactical", "size": "1", "damage": 48, "rate": 420, "ammo_per_mag": 65},
        
        # Ballistic Weapons - Size 2
        {"id": "weapon_panther_ballistic", "name": "CF-337 Panther", "type": "Ballistic", "manufacturer": "Behring", "size": "2", "damage": 85, "rate": 700, "ammo_per_mag": 300},
        {"id": "weapon_mantis", "name": "Mantis GT-220", "type": "Ballistic", "manufacturer": "Behring", "size": "2", "damage": 90, "rate": 650, "ammo_per_mag": 280},
        {"id": "weapon_revenant", "name": "Revenant Gatling", "type": "Ballistic", "manufacturer": "Apocalypse Arms", "size": "2", "damage": 45, "rate": 1200, "ammo_per_mag": 1500},
        {"id": "weapon_deadbolt2", "name": "Deadbolt II", "type": "Ballistic", "manufacturer": "Klaus & Werner", "size": "2", "damage": 220, "rate": 100, "ammo_per_mag": 40},
        
        # Ballistic Weapons - Size 3
        {"id": "weapon_longsword3", "name": "Longsword-3", "type": "Ballistic", "manufacturer": "Behring", "size": "3", "damage": 180, "rate": 400, "ammo_per_mag": 200},
        {"id": "weapon_sledge2", "name": "Sledge II Mass Driver", "type": "Ballistic", "manufacturer": "Klaus & Werner", "size": "3", "damage": 450, "rate": 75, "ammo_per_mag": 30},
        {"id": "weapon_sawbuck3", "name": "Sawbuck Repeater III", "type": "Ballistic", "manufacturer": "Gallenson Tactical", "size": "3", "damage": 95, "rate": 650, "ammo_per_mag": 350},
        
        # Ballistic Weapons - Size 4
        {"id": "weapon_combine", "name": "C-788 Combine Ballistic Cannon", "type": "Ballistic", "manufacturer": "Apocalypse Arms", "size": "4", "damage": 740, "rate": 120, "ammo_per_mag": 80},
        {"id": "weapon_m6a_ballistic", "name": "M6A Autocannon", "type": "Ballistic", "manufacturer": "Behring", "size": "4", "damage": 380, "rate": 350, "ammo_per_mag": 400},
        
        # Ballistic Weapons - Size 5
        {"id": "weapon_ad5b", "name": "AD5B Ballistic Cannon", "type": "Ballistic", "manufacturer": "Apocalypse Arms", "size": "5", "damage": 1200, "rate": 80, "ammo_per_mag": 60},
        {"id": "weapon_m8a", "name": "M8A Autocannon", "type": "Ballistic", "manufacturer": "Behring", "size": "5", "damage": 550, "rate": 280, "ammo_per_mag": 500},
        
        # Missiles - Size 1
        {"id": "missile_spark1", "name": "Spark I", "type": "Missile", "manufacturer": "A&R", "size": "1", "damage": 1200, "rate": 1},
        {"id": "missile_ignite1", "name": "Ignite I", "type": "Missile", "manufacturer": "A&R", "size": "1", "damage": 1350, "rate": 1},
        {"id": "missile_rattler1", "name": "Rattler I", "type": "Missile", "manufacturer": "Behring", "size": "1", "damage": 1180, "rate": 1},
        
        # Missiles - Size 2
        {"id": "missile_spark2", "name": "Spark II", "type": "Missile", "manufacturer": "A&R", "size": "2", "damage": 2400, "rate": 1},
        {"id": "missile_ignite2", "name": "Ignite II", "type": "Missile", "manufacturer": "A&R", "size": "2", "damage": 2700, "rate": 1},
        {"id": "missile_marksman", "name": "Marksman I", "type": "Missile", "manufacturer": "Behring", "size": "2", "damage": 2500, "rate": 1},
        
        # Missiles - Size 3
        {"id": "missile_talon", "name": "Talon IR Missile", "type": "Missile", "manufacturer": "Behring", "size": "3", "damage": 4500, "rate": 1},
        {"id": "missile_tempest", "name": "Tempest II", "type": "Missile", "manufacturer": "Behring", "size": "3", "damage": 4800, "rate": 1},
        {"id": "missile_arrow3", "name": "Arrow III", "type": "Missile", "manufacturer": "A&R", "size": "3", "damage": 4200, "rate": 1},
        
        # Missiles - Size 4
        {"id": "missile_pioneer", "name": "Pioneer", "type": "Missile", "manufacturer": "Behring", "size": "4", "damage": 8500, "rate": 1},
        {"id": "missile_raptor", "name": "Raptor", "type": "Missile", "manufacturer": "A&R", "size": "4", "damage": 9000, "rate": 1},
        
        # Torpedoes - Size 5
        {"id": "torpedo_argos5", "name": "Argos V", "type": "Missile", "manufacturer": "Behring", "size": "5", "damage": 28000, "rate": 1},
        {"id": "torpedo_seeker5", "name": "Seeker V", "type": "Missile", "manufacturer": "A&R", "size": "5", "damage": 30000, "rate": 1},
        
        # Torpedoes - Size 9
        {"id": "torpedo_argos9", "name": "Argos IX Torpedo", "type": "Missile", "manufacturer": "Behring", "size": "9", "damage": 125000, "rate": 1},
        {"id": "torpedo_seeker9", "name": "Seeker IX Torpedo", "type": "Missile", "manufacturer": "A&R", "size": "9", "damage": 135000, "rate": 1},
        
        # Special Weapons
        {"id": "weapon_mass_driver", "name": "Sledge Mass Driver", "type": "Ballistic", "manufacturer": "Klaus & Werner", "size": "4", "damage": 850, "rate": 60, "ammo_per_mag": 25},
        {"id": "weapon_plasma", "name": "Plasma Projector", "type": "Energy", "manufacturer": "Sakura Sun", "size": "4", "damage": 680, "rate": 90},
        {"id": "weapon_emp", "name": "Suckerpunch EMP", "type": "Energy", "manufacturer": "Kastak Arms", "size": "3", "damage": 0, "rate": 30},
        {"id": "weapon_mining_laser", "name": "Hofstede-S1 Mining Laser", "type": "Energy", "manufacturer": "Greycat Industrial", "size": "2", "damage": 0, "rate": 1},
        {"id": "weapon_tractor", "name": "MaxLift Tractor Beam", "type": "Energy", "manufacturer": "Greycat Industrial", "size": "1", "damage": 0, "rate": 1},
    ]

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