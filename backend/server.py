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
                return {"success": True, "data": get_comprehensive_ship_list()}
    except Exception as e:
        logging.error(f"Error fetching ships: {str(e)}")
        return {"success": True, "data": get_comprehensive_ship_list()}

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