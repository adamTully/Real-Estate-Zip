from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime, timedelta
import re
import asyncio
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from geopy.geocoders import Nominatim
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage
import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# JWT Configuration
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME_MINUTES = 60 * 24 * 7  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
users_collection = db.users

# App and router
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    owned_territories: List[str]
    created_at: datetime
    is_active: bool

class AdminUserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    owned_territories: List[str]
    created_at: datetime
    is_active: bool
    last_login: Optional[datetime] = None
    total_territories: int
    account_status: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Auth utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    payload = verify_token(credentials.credentials)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

async def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user

class ZipAnalysisRequest(BaseModel):
    zip_code: str
    
    @validator('zip_code')
    def validate_zip_code(cls, v):
        if not re.match(r'^\d{5}(-\d{4})?$', v.strip()):
            raise ValueError('Invalid ZIP code format')
        return v.strip()

class MarketIntelligence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    zip_code: str
    buyer_migration: Dict[str, Any]
    seo_social_trends: Dict[str, Any]
    content_strategy: Dict[str, Any]
    hidden_listings: Dict[str, Any]
    market_hooks: Dict[str, Any]
    content_assets: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Focus-mode task plan: add Content Assets
TASK_ORDER = ["location", "buyer_migration", "seo_social_trends", "content_strategy", "content_assets"]
TASK_PERCENT = {"location": 15, "buyer_migration": 40, "seo_social_trends": 70, "content_strategy": 90, "content_assets": 100}

# Service
class ZipIntelligenceService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="zip-intel-generator")
        self.llm = LlmChat(
            api_key=os.environ.get('OPENAI_API_KEY'),
            session_id=f"zipintel-{uuid.uuid4()}",
            system_message=(
                "You are an expert real estate market analyst. Provide comprehensive, data-driven "
                "insights based on the user's requests. Always be specific, actionable, and professional."
            ),
        ).with_model("openai", "gpt-5")

    async def _normalize_llm_response(self, resp: Any) -> str:
        try:
            if isinstance(resp, str):
                return resp
            text = getattr(resp, 'text', None)
            if isinstance(text, str):
                return text
            return json.dumps(resp, ensure_ascii=False)
        except Exception:
            return ""

    async def _safe_send(self, prompt: str, max_retries: int = 3) -> str:
        delay = 1.0
        last_err = None
        for _ in range(max_retries):
            try:
                user_message = UserMessage(text=prompt)
                resp = await self.llm.send_message(user_message)
                text = await self._normalize_llm_response(resp)
                if text and not any(term in text.lower() for term in ["rate limit", "quota", "temporarily unavailable"]):
                    return text
                raise RuntimeError("Upstream rate limit or temporary failure text")
            except Exception as e:
                last_err = e
                await asyncio.sleep(delay)
                delay = min(delay * 2, 8)
        logging.error(f"LLM send failed after retries: {str(last_err)}")
        return "Real-time analysis temporarily unavailable. Please try again."

    async def get_location_info(self, zip_code: str) -> Dict[str, Any]:
        try:
            base_zip = zip_code.split('-')[0]
            location = self.geolocator.geocode(f"{base_zip}, USA")
            if location:
                display = location.raw.get('display_name', '')
                city = display.split(',')[0]
                state = display.split(',')[-3].strip() if ',' in display else 'Unknown'
                return {
                    "city": city,
                    "state": state,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "full_address": location.address,
                }
            return {"city": "Unknown", "state": "Unknown", "latitude": 0, "longitude": 0}
        except Exception as e:
            logging.error(f"Geolocation error for {zip_code}: {str(e)}")
            return {"city": "Unknown", "state": "Unknown", "latitude": 0, "longitude": 0}

    async def generate_buyer_migration_intel(self, zip_code: str, location_info: Dict[str, Any]) -> Dict[str, Any]:
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        try:
            prompt = f"""
Act as a real estate market analyst. I'm a Realtor in {city_name}, {state_name} (ZIP {zip_code}).

Return your answer in clean, scannable Markdown with clear headings, subheadings, and lists. Use this exact structure:

# Buyer Migration Intelligence – {city_name}, {state_name}

## Market Overview
- 2-4 sentences summarizing notable migration dynamics and housing context.

## Where Buyers Are Coming From
- Bullet list of top feeder cities/metros/states with brief reasons (1 line each)
- If relevant, include a simple table:

| Origin | Share/Trend | Note |
| --- | --- | --- |
| City A | Rising | Lower cost, job inflows |
| City B | Stable | Lifestyle upgrade |

## Why They're Moving
- Bullet list of top motivations (cost of living, schools, taxes, commute, lifestyle, climate, etc.) with practical implications for messaging

## Content Strategy To Attract These Buyers
### Hooks (5-7)
- Short, thumb-stopping hooks tailored to {city_name}

### SEO Keywords (10-15)
- Comma-separated list or bullets of local, high-intent terms

### Video Title Ideas (5-10)
- YouTube-style titles optimized for search and CTR

## Quick Actions (3-5)
- Actionable next steps you recommend a local agent takes this week

Be specific, professional, and avoid fluff. Use lists where possible. Keep table simple and valid Markdown.
"""
            response_text = await self._safe_send(prompt)
            return {
                "summary": f"Migration analysis for {city_name}, {state_name} completed with real market data",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": response_text,
                "generated_with": "ChatGPT GPT-5",
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logging.error(f"ChatGPT error for buyer migration: {str(e)}")
            return {
                "summary": f"Migration analysis for {city_name}, {state_name} (fallback mode)",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": "Real-time analysis temporarily unavailable. Please try again.",
                "error": str(e),
            }

    async def generate_seo_social_trends(self, zip_code: str, location_info: Dict[str, Any]) -> Dict[str, Any]:
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        try:
            prompt = f"""
Act as an SEO expert and social media strategist. I'm a Realtor in {city_name}, {state_name} (ZIP {zip_code}).

Identify the top trending searches, keywords, and questions buyers are Googling and searching natively on Facebook, Instagram, X/Twitter, and TikTok about moving to or living in {city_name}, {state_name} in the past 90 days.

Return your answer in clean Markdown with clear sections and lists using this structure:

# SEO & Social Media Trends – {city_name}, {state_name}

## Market Search Insights
- 2-4 sentences summarizing how locals and relocators search across platforms for {city_name} topics

## High-Volume Local Keywords (10-15)
- Bullet list with user intent notes

| Keyword | Intent | Search Volume Indicator |
| --- | --- | --- |
| moving to {city_name} | informational | High relocation interest |
| best neighborhoods in {city_name} | research | School/lifestyle fit |
| {city_name} cost of living | comparison | Budget planning |

## Long-Tail Questions (8-12)
- "What neighborhoods in {city_name} have the best schools?"
- "How much does it cost to live in {city_name} compared to [other cities]?"
- "What's the job market like in {city_name}?"

## Video/Content Title Ideas (10)
- YouTube and social-ready titles optimized for search and engagement
- Include geo modifiers and trending angles

## Platform-Specific Breakouts

### Facebook
**Native Queries/Hashtags (5-10):**
- Bullet list of Facebook-specific searches and group discussions

**Hook Patterns (3):**
- Attention-grabbing opening lines that work on Facebook

**Content Angles (3):**
- Facebook-specific content approaches (community focus, local events, family-oriented)

**Sample Post Titles (3):**
- Ready-to-use Facebook post headlines

### Instagram  
**Native Queries/Hashtags (5-10):**
- Instagram-specific hashtags and search behaviors

**Hook Patterns (3):**
- Visual-first hooks for feed posts and reels

**Content Angles (3):**
- Instagram-specific approaches (lifestyle, behind-scenes, aesthetic)

**Sample Post Titles (3):**
- Caption-ready titles for Instagram posts

### X/Twitter
**Native Queries/Hashtags (5-10):**
- Twitter-specific hashtags and real-time search trends

**Hook Patterns (3):**
- Tweet-length hooks for engagement

**Content Angles (3):**
- Twitter-specific approaches (news, quick tips, conversations)

**Sample Post Titles (3):**
- Tweet-ready headlines

### TikTok
**Native Queries/Hashtags (5-10):**
- TikTok trending hashtags and search behaviors

**Hook Patterns (3):**
- 8-second rule hooks for TikTok videos

**Content Angles (3):**
- TikTok-specific approaches (trends, education, entertainment)

**Sample Post Titles (3):**
- TikTok video titles and concepts

## Implementation Tips
- Cross-platform keyword usage strategies
- Platform-specific optimization techniques
- Content repurposing recommendations

Use geo modifiers ({city_name}, nearby neighborhoods/landmarks). Keep Fair Housing compliant. Be specific and actionable.
"""
            response_text = await self._safe_send(prompt)
            return {
                "summary": f"SEO & YouTube analysis for {city_name}, {state_name} with real search data",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": response_text,
                "generated_with": "ChatGPT GPT-5",
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logging.error(f"ChatGPT error for SEO analysis: {str(e)}")
            return {
                "summary": f"SEO analysis for {city_name}, {state_name} (fallback mode)",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": "Real-time analysis temporarily unavailable. Please try again.",
                "error": str(e),
            }

    async def generate_content_strategy(self, zip_code: str, location_info: Dict[str, Any]) -> Dict[str, Any]:
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        try:
            prompt = f"""
Act as a real estate marketing strategist. I'm a Realtor in {city_name}, {state_name} (ZIP {zip_code}).

Return your answer in clean Markdown with this structure and clear typography-friendly sections:

# Content Marketing Strategy – {city_name}, {state_name}

## Strategy Goals
- 2-3 bullets on primary outcomes (awareness, leads, consultations)

## 8-Week Roadmap
### Week 1
- Short-form: …
- Long-form: …
- Lead Magnet: …
- Email/Retargeting: …

### Week 2
- Short-form: …
- Long-form: …
- Lead Magnet: …
- Email/Retargeting: …

### Week 3
- …

### Week 8
- …

## Implementation Best Practices
- Channel distribution, repurposing plan, CTAs, and measurement tips

## Quick Actions
- 3-5 next steps to execute this week
"""
            response_text = await self._safe_send(prompt)
            return {
                "summary": f"8-week content strategy for {city_name}, {state_name} market",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": response_text,
                "generated_with": "ChatGPT GPT-5",
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logging.error(f"ChatGPT error for content strategy: {str(e)}")
            return {
                "summary": f"Content strategy for {city_name}, {state_name} (fallback mode)",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": "Real-time analysis temporarily unavailable. Please try again.",
                "error": str(e),
            }

    async def generate_content_assets(self, zip_code: str, location_info: Dict[str, Any]) -> Dict[str, Any]:
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        try:
            prompt = f"""
Act as a content production system for a Realtor in {city_name}, {state_name} (ZIP {zip_code}).

Return ONLY valid JSON (no prose) with this schema:
{{
  "summary": "string",
  "blog_posts": [
    {{"name": "string", "title": "string", "content": "string"}}
  ],
  "email_campaigns": [
    {{"name": "string", "title": "string", "content": "string"}}
  ]
}}

Requirements:
- name must use kebab-case and end with .txt (e.g., moving-to-{city_name}-guide.txt)
- content must be plain text (no HTML/Markdown), ready to download as .txt
- 8 emails, 10 blogs; keep each ~300-700 words
- Titles should reflect local SEO terms and clear value
"""
            raw = await self._safe_send(prompt)
            data = None
            try:
                data = json.loads(raw)
            except Exception:
                start = raw.find('{')
                end = raw.rfind('}')
                if start != -1 and end != -1:
                    try:
                        data = json.loads(raw[start:end+1])
                    except Exception:
                        data = None
            if not data:
                raise RuntimeError("Failed to parse content assets JSON")

            def _slugify(text: str) -> str:
                try:
                    return (
                        (text or "")
                        .lower()
                        .strip()
                        .replace("&", " and ")
                        .replace("/", "-")
                    )
                except Exception:
                    return ""

            def enrich(items, kind: str):
                enriched = []
                for idx, it in enumerate(items):
                    title = it.get('title') or it.get('name') or f"{kind}-{idx+1}"
                    slug = "-".join([s for s in _slugify(title).split() if s])
                    if kind == 'emails':
                        import re as _re
                        m = _re.search(r"week\s*(\d{1,2})", title, _re.IGNORECASE)
                        week = m.group(1) if m else str(idx + 1)
                        base = f"week-{week}-email-{slug}" if slug else f"week-{week}-email"
                    else:
                        base = f"blog-{slug}" if slug else f"blog-{idx+1}"
                    name = it.get('name') or f"{base}.txt"
                    if not name.endswith('.txt'):
                        name = name + '.txt'
                    content = it.get('content', '')
                    size_kb = max(1, len(content.encode('utf-8')) // 1024)
                    enriched.append({
                        "name": name,
                        "title": title,
                        "content": content,
                        "size_kb": size_kb,
                    })
                return enriched

            blogs = enrich(data.get('blog_posts', []), 'blogs')
            emails = enrich(data.get('email_campaigns', []), 'emails')

            return {
                "summary": data.get('summary', f"Content assets for {city_name}, {state_name}"),
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "blog_posts": blogs,
                "email_campaigns": emails,
                "generated_with": "ChatGPT GPT-5",
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logging.error(f"ChatGPT error for content assets: {str(e)}")
            return {
                "summary": f"Content assets (fallback) for {city_name}, {state_name}",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "blog_posts": [],
                "email_campaigns": [],
                "error": str(e),
            }

# Status helpers
async def _init_status(zip_code: str) -> Dict[str, Any]:
    now = datetime.utcnow()
    job_id = str(uuid.uuid4())
    tasks = {tid: {"status": "pending", "percent": 0, "title": tid} for tid in TASK_ORDER}
    doc = {
        "zip_code": zip_code,
        "job_id": job_id,
        "state": "running",
        "overall_percent": 0,
        "tasks": tasks,
        "created_at": now,
        "updated_at": now,
    }
    await db.analysis_status.update_one({"zip_code": zip_code}, {"$set": doc}, upsert=True)
    return doc

async def _update_task(zip_code: str, task_id: str, status: str, percent: int):
    await db.analysis_status.update_one(
        {"zip_code": zip_code},
        {"$set": {f"tasks.{task_id}.status": status, f"tasks.{task_id}.percent": percent, "updated_at": datetime.utcnow()}},
    )

async def _update_overall(zip_code: str, percent: int):
    await db.analysis_status.update_one(
        {"zip_code": zip_code},
        {"$set": {"overall_percent": percent, "updated_at": datetime.utcnow()}},
    )

async def _complete_status(zip_code: str, state: str = "done"):
    await db.analysis_status.update_one(
        {"zip_code": zip_code},
        {"$set": {"state": state, "overall_percent": 100 if state == "done" else 0, "updated_at": datetime.utcnow()}},
    )

# Background job
async def _run_zip_job(zip_code: str):
    try:
        svc = ZipIntelligenceService()
        await _update_task(zip_code, "location", "running", 50)
        location_info = await svc.get_location_info(zip_code)
        await _update_task(zip_code, "location", "done", 100)
        await _update_overall(zip_code, TASK_PERCENT["location"])

        await _update_task(zip_code, "buyer_migration", "running", 10)
        buyer_migration = await svc.generate_buyer_migration_intel(zip_code, location_info)
        await _update_task(zip_code, "buyer_migration", "done", 100)
        await _update_overall(zip_code, TASK_PERCENT["buyer_migration"])
        await asyncio.sleep(0.5)

        await _update_task(zip_code, "seo_social_trends", "running", 10)
        seo = await svc.generate_seo_social_trends(zip_code, location_info)
        await _update_task(zip_code, "seo_social_trends", "done", 100)
        await _update_overall(zip_code, TASK_PERCENT["seo_social_trends"])
        await asyncio.sleep(0.5)

        await _update_task(zip_code, "content_strategy", "running", 10)
        strategy = await svc.generate_content_strategy(zip_code, location_info)
        await _update_task(zip_code, "content_strategy", "done", 100)
        await _update_overall(zip_code, TASK_PERCENT["content_strategy"])
        await asyncio.sleep(0.5)

        await _update_task(zip_code, "content_assets", "running", 10)
        assets = await svc.generate_content_assets(zip_code, location_info)
        await _update_task(zip_code, "content_assets", "done", 100)
        await _update_overall(zip_code, TASK_PERCENT["content_assets"])

        intelligence = MarketIntelligence(
            zip_code=zip_code,
            buyer_migration=buyer_migration,
            seo_social_trends=seo,
            content_strategy=strategy,
            hidden_listings={"summary": "Pending generation", "analysis_content": "Not generated yet."},
            market_hooks={"summary": "Pending generation", "detailed_analysis": "Not generated yet."},
            content_assets=assets,
        )
        await db.market_intelligence.insert_one(intelligence.dict())
        await _complete_status(zip_code, state="done")
    except Exception as e:
        logging.error(f"Job failed for {zip_code}: {str(e)}")
        await db.analysis_status.update_one(
            {"zip_code": zip_code},
            {"$set": {"state": "failed", "error": str(e), "updated_at": datetime.utcnow()}},
        )

# Authentication Endpoints
@api_router.post("/auth/register", response_model=TokenResponse)
async def register_user(user_data: UserCreate):
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    
    new_user = {
        "_id": user_id,
        "email": user_data.email,
        "password_hash": hashed_password,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "role": "agent",
        "owned_territories": [],
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    await users_collection.insert_one(new_user)
    
    # Create access token
    access_token = create_access_token({"user_id": user_id, "email": user_data.email})
    
    # Return user data and token
    user_response = UserResponse(
        id=user_id,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role="agent",
        owned_territories=[],
        created_at=new_user["created_at"],
        is_active=True
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)

@api_router.post("/auth/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    # Find user by email
    user = await users_collection.find_one({"email": login_data.email})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    if not user["is_active"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is deactivated")
    
    # Update last login time
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    access_token = create_access_token({"user_id": user["_id"], "email": user["email"]})
    
    # Return user data and token
    user_response = UserResponse(
        id=user["_id"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        role=user["role"],
        owned_territories=user["owned_territories"],
        created_at=user["created_at"],
        is_active=user["is_active"]
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["_id"],
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        role=current_user["role"],
        owned_territories=current_user["owned_territories"],
        created_at=current_user["created_at"],
        is_active=current_user["is_active"]
    )

# Admin Endpoints
@api_router.post("/users/assign-territory")
async def assign_territory_to_user(
    territory_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Assign a ZIP code territory to the current user"""
    zip_code = territory_data.get("zip_code")
    if not zip_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ZIP code is required")
    
    # **CRITICAL FIX**: Check if ZIP is already assigned to another user
    existing_owner = await users_collection.find_one({"owned_territories": zip_code})
    if existing_owner and existing_owner["_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"ZIP {zip_code} is already assigned to another user ({existing_owner['email']})"
        )
    
    # Check if current user already owns this territory
    if zip_code in current_user["owned_territories"]:
        return {"message": "Territory already assigned", "zip_code": zip_code}
    
    # Add territory to user's owned_territories
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$push": {"owned_territories": zip_code}}
    )
    
    return {"message": f"ZIP {zip_code} assigned successfully", "zip_code": zip_code}

@api_router.get("/admin/users", response_model=List[AdminUserResponse])
async def get_all_users(admin_user: dict = Depends(get_admin_user)):
    """Get all users for admin dashboard"""
    users_cursor = users_collection.find({})
    users = await users_cursor.to_list(length=None)
    
    admin_users = []
    for user in users:
        admin_users.append(AdminUserResponse(
            id=user["_id"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            role=user["role"],
            owned_territories=user["owned_territories"],
            created_at=user["created_at"],
            is_active=user["is_active"],
            last_login=user.get("last_login"),
            total_territories=len(user["owned_territories"]),
            account_status="Active" if user["is_active"] else "Inactive"
        ))
    
    return admin_users

@api_router.get("/admin/users/{user_id}", response_model=AdminUserResponse)
async def get_user_details(user_id: str, admin_user: dict = Depends(get_admin_user)):
    """Get detailed user information"""
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return AdminUserResponse(
        id=user["_id"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        role=user["role"],
        owned_territories=user["owned_territories"],
        created_at=user["created_at"],
        is_active=user["is_active"],
        last_login=user.get("last_login"),
        total_territories=len(user["owned_territories"]),
        account_status="Active" if user["is_active"] else "Inactive"
    )

@api_router.post("/admin/users/{user_id}/toggle-status")
async def toggle_user_status(user_id: str, admin_user: dict = Depends(get_admin_user)):
    """Toggle user active/inactive status"""
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    new_status = not user["is_active"]
    await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"is_active": new_status}}
    )
    
    return {"message": f"User status updated to {'Active' if new_status else 'Inactive'}"}

# Create super admin endpoint (for initial setup)
@api_router.post("/admin/cleanup-duplicate-territories")
async def cleanup_duplicate_territories(admin_user: dict = Depends(get_admin_user)):
    """Clean up duplicate territory assignments"""
    
    # Find all users with territories
    users_with_territories = await users_collection.find({"owned_territories": {"$ne": []}}).to_list(length=None)
    
    # Track ZIP assignments
    zip_assignments = {}
    duplicates_found = []
    duplicates_removed = 0
    
    for user in users_with_territories:
        for zip_code in user["owned_territories"]:
            if zip_code in zip_assignments:
                # Duplicate found!
                duplicates_found.append({
                    "zip_code": zip_code,
                    "first_user": zip_assignments[zip_code]["email"],
                    "duplicate_user": user["email"],
                    "first_user_date": zip_assignments[zip_code]["created_at"],
                    "duplicate_user_date": user["created_at"]
                })
                
                # Remove from the later user (keep first registration)
                if user["created_at"] > zip_assignments[zip_code]["created_at"]:
                    # Remove from current user
                    await users_collection.update_one(
                        {"_id": user["_id"]},
                        {"$pull": {"owned_territories": zip_code}}
                    )
                    duplicates_removed += 1
                else:
                    # Remove from previously tracked user
                    await users_collection.update_one(
                        {"_id": zip_assignments[zip_code]["user_id"]},
                        {"$pull": {"owned_territories": zip_code}}
                    )
                    zip_assignments[zip_code] = {
                        "user_id": user["_id"],
                        "email": user["email"],
                        "created_at": user["created_at"]
                    }
                    duplicates_removed += 1
            else:
                zip_assignments[zip_code] = {
                    "user_id": user["_id"],
                    "email": user["email"],
                    "created_at": user["created_at"]
                }
    
    return {
        "message": f"Cleanup complete. Removed {duplicates_removed} duplicate assignments.",
        "duplicates_found": duplicates_found,
        "total_unique_territories": len(zip_assignments)
    }
async def create_super_admin(admin_data: UserCreate):
    """Create the first super admin account"""
    # Check if any super admin already exists
    existing_admin = await users_collection.find_one({"role": "super_admin"})
    if existing_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Super admin already exists")
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": admin_data.email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Create super admin
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(admin_data.password)
    
    new_admin = {
        "_id": user_id,
        "email": admin_data.email,
        "password_hash": hashed_password,
        "first_name": admin_data.first_name,
        "last_name": admin_data.last_name,
        "role": "super_admin",
        "owned_territories": [],
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    await users_collection.insert_one(new_admin)
    
    # Create access token
    access_token = create_access_token({"user_id": user_id, "email": admin_data.email})
    
    # Return user data and token
    user_response = UserResponse(
        id=user_id,
        email=admin_data.email,
        first_name=admin_data.first_name,
        last_name=admin_data.last_name,
        role="super_admin",
        owned_territories=[],
        created_at=new_admin["created_at"],
        is_active=True
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)

@api_router.post("/zip-availability/check")
async def check_zip_availability(zip_data: dict):
    """Check if a ZIP code is available and get real location data"""
    zip_code = zip_data.get("zip_code", "").strip()
    
    if not zip_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ZIP code is required")
    
    # Validate ZIP format
    if not re.match(r'^\d{5}(-\d{4})?$', zip_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ZIP code format")
    
    try:
        # Get real location data using geopy
        geolocator = Nominatim(user_agent="zip-intel-generator")
        location = geolocator.geocode(f"{zip_code}, USA")
        
        if not location:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ZIP code not found")
        
        # Parse location data from geocoded address
        address_parts = location.address.split(', ')
        print(f"Geocoded address: {location.address}")  # Debug log
        
        # Initialize defaults
        city = "Unknown"
        state = "Unknown" 
        county = "Unknown County"
        
        # Common US state abbreviations and full names
        us_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
        us_state_names = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
        
        # Parse the geocoded address (format: ZIP, City, County, State, Country)
        for i, part in enumerate(address_parts):
            part = part.strip()
            
            # Look for state (abbreviation or full name)
            if any(state_abbr in part for state_abbr in us_states) or any(state_name in part for state_name in us_state_names):
                state = part
                # Convert full state name to abbreviation for consistency
                if part == 'Georgia':
                    state = 'GA'
                elif part == 'California':
                    state = 'CA'
                elif part == 'New York':
                    state = 'NY'
                elif part == 'Texas':
                    state = 'TX'
                elif part == 'Florida':
                    state = 'FL'
                # Add more as needed
                    
                # City is usually before state
                if i >= 2:  # Skip ZIP code (index 0)
                    city = address_parts[1].strip()  # Usually index 1 is city
                    if i >= 3 and ('County' in address_parts[2] or 'Parish' in address_parts[2]):
                        county = address_parts[2].strip()
                break
        
        print(f"Parsed location: city={city}, state={state}, county={county}")  # Debug log
        
        # **CRITICAL FIX**: Check if ZIP is actually taken by checking user database
        user_with_zip = await users_collection.find_one({"owned_territories": zip_code})
        is_available = user_with_zip is None  # Available if no user owns it
        
        # Get waitlist count if ZIP is taken
        waitlist_count = None
        if not is_available:
            # Count how many people might be on waitlist (mock for now)
            import random
            random.seed(hash(zip_code))
            waitlist_count = random.randint(5, 30)
        
        result = {
            "zip_code": zip_code,
            "available": is_available,
            "location_info": {
                "city": city,
                "state": state, 
                "county": county,
                "latitude": location.latitude,
                "longitude": location.longitude
            },
            "pricing": {
                "monthly_fee": 299,
                "setup_fee": 99,
                "annual_discount": 0.15
            } if is_available else None,
            "waitlist_count": waitlist_count,
            "assigned_to": user_with_zip["email"] if user_with_zip else None  # Debug info
        }
        
        return result
        
    except Exception as e:
        print(f"Geocoding error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to lookup ZIP code location")
async def analyze_zip_code(request: ZipAnalysisRequest, background_tasks: BackgroundTasks):
    try:
        zip_code = request.zip_code
        existing = await db.market_intelligence.find_one({
            "zip_code": zip_code,
            "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)},
        })
        if existing:
            return MarketIntelligence(**existing)
        svc = ZipIntelligenceService()
        location_info = await svc.get_location_info(zip_code)
        buyer_migration = await svc.generate_buyer_migration_intel(zip_code, location_info)
        seo = await svc.generate_seo_social_trends(zip_code, location_info)
        strategy = await svc.generate_content_strategy(zip_code, location_info)
        assets = await svc.generate_content_assets(zip_code, location_info)
        intelligence = MarketIntelligence(
            zip_code=zip_code,
            buyer_migration=buyer_migration,
            seo_social_trends=seo,
            content_strategy=strategy,
            hidden_listings={"summary": "Pending generation", "analysis_content": "Not generated yet."},
            market_hooks={"summary": "Pending generation", "detailed_analysis": "Not generated yet."},
            content_assets=assets,
        )
        await db.market_intelligence.insert_one(intelligence.dict())
        return intelligence
    except Exception as e:
        logging.error(f"Error analyzing ZIP code {request.zip_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating analysis: {str(e)}")

@api_router.post("/zip-analysis/start")
async def start_zip_analysis(request: ZipAnalysisRequest):
    zip_code = request.zip_code
    existing = await db.market_intelligence.find_one({
        "zip_code": zip_code,
        "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)},
    })
    if existing:
        await db.analysis_status.update_one(
            {"zip_code": zip_code},
            {"$set": {"zip_code": zip_code, "state": "done", "overall_percent": 100, "updated_at": datetime.utcnow()}},
            upsert=True,
        )
        status_doc = await db.analysis_status.find_one({"zip_code": zip_code}, {"_id": 0})
        return status_doc
    status_doc = await _init_status(zip_code)
    asyncio.create_task(_run_zip_job(zip_code))
    status_doc.pop('_id', None)
    return status_doc

@api_router.get("/zip-analysis/status/{zip_code}")
async def get_zip_status(zip_code: str):
    status_doc = await db.analysis_status.find_one({"zip_code": zip_code})
    if not status_doc:
        raise HTTPException(status_code=404, detail="Status not found")
    status_doc.pop('_id', None)
    return status_doc

@api_router.get("/zip-analysis/{zip_code}", response_model=MarketIntelligence)
async def get_zip_analysis(zip_code: str):
    try:
        analysis = await db.market_intelligence.find_one({"zip_code": zip_code})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return MarketIntelligence(**analysis)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/generate-pdf/{zip_code}")
async def generate_hidden_listings_pdf(zip_code: str):
    try:
        analysis = await db.market_intelligence.find_one({"zip_code": zip_code})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        title = Paragraph(f"Hidden Listings Analysis - {zip_code}", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        content = analysis['hidden_listings'].get('detailed_analysis') or analysis['hidden_listings'].get('analysis_content', '')
        for line in content.split('\n'):
            if line.strip():
                if line.startswith('#'):
                    para = Paragraph(line.replace('#', '').strip(), styles['Heading2'])
                else:
                    para = Paragraph(line.strip(), styles['Normal'])
                story.append(para)
                story.append(Spacer(1, 6))
        doc.build(story)
        return FileResponse(
            temp_file.name,
            media_type='application/pdf',
            filename=f"{zip_code}-hidden-listings.pdf",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@api_router.get("/content-asset/{zip_code}/{asset_type}/{asset_name}")
async def get_content_asset(zip_code: str, asset_type: str, asset_name: str):
    try:
        analysis = await db.market_intelligence.find_one({"zip_code": zip_code})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        content_assets = analysis['content_assets']
        if asset_type == "blogs":
            assets = content_assets.get('blog_posts', [])
        elif asset_type == "emails":
            assets = content_assets.get('email_campaigns', [])
        else:
            raise HTTPException(status_code=400, detail="Invalid asset type")
        for asset in assets:
            if asset['name'] == asset_name:
                return {"content": asset['content']}
        raise HTTPException(status_code=404, detail="Asset not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/zip-analysis/assets/regenerate")
async def regenerate_assets(request: ZipAnalysisRequest):
    """Regenerate only content assets for an existing analysis."""
    zip_code = request.zip_code
    analysis = await db.market_intelligence.find_one({"zip_code": zip_code})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    location_info = analysis.get('buyer_migration', {}).get('location') or {}
    try:
        svc = ZipIntelligenceService()
        assets = await svc.generate_content_assets(zip_code, location_info)
        await db.market_intelligence.update_one(
            {"zip_code": zip_code},
            {"$set": {"content_assets": assets, "updated_at": datetime.utcnow()}},
        )
        return assets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating assets: {str(e)}")

@api_router.get("/")
async def root():
    return {"message": "ZIP Intel Generator API v2.0 (buyer+seo+strategy+assets)"}

# Mount router and middleware
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()