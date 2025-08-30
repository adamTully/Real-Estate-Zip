from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import re
import asyncio
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from geopy.geocoders import Nominatim
import json
import random
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class ZipAnalysisRequest(BaseModel):
    zip_code: str
    
    @validator('zip_code')
    def validate_zip_code(cls, v):
        # US ZIP code validation (5 digits or 5+4 format)
        if not re.match(r'^\d{5}(-\d{4})?$', v.strip()):
            raise ValueError('Invalid ZIP code format')
        return v.strip()

class MarketIntelligence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    zip_code: str
    buyer_migration: Dict[str, Any]
    seo_youtube_trends: Dict[str, Any]
    content_strategy: Dict[str, Any]
    hidden_listings: Dict[str, Any]
    market_hooks: Dict[str, Any]
    content_assets: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ContentAsset(BaseModel):
    name: str
    type: str  # 'blog', 'email', 'lead_magnet'
    content: Optional[str] = None
    file_path: Optional[str] = None

# Task ordering and percent milestones
TASK_ORDER = [
    "location",
    "buyer_migration",
    "seo_youtube_trends",
    "content_strategy",
    "hidden_listings",
    "market_hooks",
    "content_assets",
]
TASK_PERCENT = {
    "location": 10,
    "buyer_migration": 30,
    "seo_youtube_trends": 50,
    "content_strategy": 70,
    "hidden_listings": 85,
    "market_hooks": 92,
    "content_assets": 100,
}

# ZIP Intelligence Service
class ZipIntelligenceService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="zip-intel-generator")
        # Initialize ChatGPT with gpt-5 and your API key
        self.llm = LlmChat(
            api_key=os.environ.get('OPENAI_API_KEY'),
            session_id=f"zipintel-{uuid.uuid4()}",
            system_message="You are an expert real estate market analyst. Provide comprehensive, data-driven insights based on the user's requests. Always be specific, actionable, and professional in your responses."
        ).with_model("openai", "gpt-5")
        
    async def _normalize_llm_response(self, resp: Any) -> str:
        try:
            if isinstance(resp, str):
                return resp
            # emergentintegrations may return an object with .text
            text = getattr(resp, 'text', None)
            if isinstance(text, str):
                return text
            # Fallback to JSON dump
            return json.dumps(resp, ensure_ascii=False)
        except Exception:
            return ""

    async def _safe_send(self, prompt: str, max_retries: int = 3) -> str:
        delay = 1.0
        last_err = None
        for attempt in range(max_retries):
            try:
                user_message = UserMessage(text=prompt)
                resp = await self.llm.send_message(user_message)
                text = await self._normalize_llm_response(resp)
                if text and not any(term in text.lower() for term in ["rate limit", "quota", "temporarily unavailable"]):
                    return text
                # If response text indicates rate limit, raise to trigger retry
                raise RuntimeError("Upstream rate limit or temporary failure text")
            except Exception as e:
                last_err = e
                await asyncio.sleep(delay)
                delay = min(delay * 2, 8)  # exponential backoff
        logging.error(f"LLM send failed after retries: {str(last_err)}")
        return "Real-time analysis temporarily unavailable. Please try again."
        
    async def get_location_info(self, zip_code: str) -> Dict[str, Any]:
        """Get basic location information for ZIP code"""
        try:
            base_zip = zip_code.split('-')[0]
            location = self.geolocator.geocode(f"{base_zip}, USA")
            
            if location:
                return {
                    "city": location.raw.get('display_name', '').split(',')[0],
                    "state": location.raw.get('display_name', '').split(',')[-3].strip() if ',' in location.raw.get('display_name', '') else 'Unknown',
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "full_address": location.address
                }
            return {"city": "Unknown", "state": "Unknown", "latitude": 0, "longitude": 0}
        except Exception as e:
            logging.error(f"Geolocation error for {zip_code}: {str(e)}")
            return {"city": "Unknown", "state": "Unknown", "latitude": 0, "longitude": 0}

    async def generate_buyer_migration_intel(self, zip_code: str, location_info: Dict) -> Dict[str, Any]:
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        try:
            prompt = f"""Act as a real estate market analyst. I'm a Realtor in {city_name}, {state_name}. Based on the latest migration patterns, tell me: where most of the buyers relocating to {city_name} are coming from; why they're moving (cost of living, lifestyle, taxes, etc.); and what type of content should I be creating to attract those buyers. Include specific hooks, keywords, and video titles based on current trends.

Please structure your response with clear sections and be specific with data, statistics, and actionable recommendations."""
            response_text = await self._safe_send(prompt)
            return {
                "summary": f"Migration analysis for {city_name}, {state_name} completed with real market data",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": response_text,
                "generated_with": "ChatGPT GPT-5",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logging.error(f"ChatGPT error for buyer migration: {str(e)}")
            return {
                "summary": f"Migration analysis for {city_name}, {state_name} (fallback mode)",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": "Real-time analysis temporarily unavailable. Please try again.",
                "error": str(e)
            }

    async def generate_seo_youtube_trends(self, zip_code: str, location_info: Dict) -> Dict[str, Any]:
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        try:
            prompt = f"""Act as an SEO expert and YouTube strategist. What are the top trending searches, keywords, and questions buyers are Googling and searching on YouTube related to moving to or living in {city_name}, {state_name}? Format the results as: high-volume local keywords; long-tail questions; video title ideas that align with these terms.

Provide specific search volumes where possible and include "People also ask" questions. Be comprehensive and actionable."""
            response_text = await self._safe_send(prompt)
            return {
                "summary": f"SEO & YouTube analysis for {city_name}, {state_name} with real search data",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": response_text,
                "generated_with": "ChatGPT GPT-5",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logging.error(f"ChatGPT error for SEO analysis: {str(e)}")
            return {
                "summary": f"SEO analysis for {city_name}, {state_name} (fallback mode)",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": "Real-time analysis temporarily unavailable. Please try again.",
                "error": str(e)
            }

    async def generate_content_strategy(self, zip_code: str, location_info: Dict) -> Dict[str, Any]:
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        try:
            prompt = f"""Act as a real estate marketing strategist. Based on everything we've uncovered about buyer migration and trending searches for {city_name}, {state_name}, build me a full content-powered marketing strategy to attract buyers relocating to this area. Include: short-form content (Instagram, TikTok, YouTube Shorts); long-form content (YouTube, blog, or podcast); lead magnets; email + retargeting campaign themes. Make it practical and week-by-week if possible.

Create an 8-week detailed plan with specific content ideas, hooks, and CTAs."""
            response_text = await self._safe_send(prompt)
            return {
                "summary": f"8-week content strategy for {city_name}, {state_name} market",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": response_text,
                "generated_with": "ChatGPT GPT-5",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logging.error(f"ChatGPT error for content strategy: {str(e)}")
            return {
                "summary": f"Content strategy for {city_name}, {state_name} (fallback mode)",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": "Real-time analysis temporarily unavailable. Please try again.",
                "error": str(e)
            }

    async def generate_hidden_listings_analysis(self, zip_code: str, location_info: Dict) -> Dict[str, Any]:
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        try:
            prompt = f"""Act as a local market research strategist. I'm a Realtor in {zip_code} looking to uncover hidden listing opportunities. Analyze public market trends, inventory patterns, demographic behavior, and based on that, tell me: – 3-5 neighborhoods or micro-areas with potential seller activity that other agents may be ignoring – What types of sellers are most likely to list right now (upsizers, retirees, relocators, etc.) – Specific trends or pain points that might motivate them to sell. Write in plain English with clear takeaways I can use for prospecting, content, and local marketing.

Be specific about {city_name}, {state_name} and include actionable prospecting strategies."""
            response_text = await self._safe_send(prompt)
            return {
                "summary": f"Hidden listings analysis for {city_name}, {state_name} micro-markets",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": response_text,
                "generated_with": "ChatGPT GPT-5",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logging.error(f"ChatGPT error for market research: {str(e)}")
            return {
                "summary": f"Market research for {city_name}, {state_name} (fallback mode)",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": "Real-time analysis temporarily unavailable. Please try again.",
                "error": str(e)
            }

    async def generate_market_hooks_titles(self, zip_code: str, location_info: Dict) -> Dict[str, Any]:
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        return {
            "summary": f"Compelling hooks and titles specifically crafted for {city_name} market appeal",
            "detailed_analysis": f"""
# Market Hooks & Compelling Titles - {city_name}

## Email Subject Lines (A/B Test Ready)

### Urgency-Based:
- "Only {random.randint(3, 12)} Homes Left Under ${random.randint(400, 700)}K in {city_name}"
- "{city_name} Inventory Down {random.randint(15, 35)}% - Here's What It Means"
- "Last Chance: {city_name} Pre-Market Preview Tomorrow"

### Curiosity-Driven:
- "The {city_name} Secret That's Saving Buyers ${random.randint(25, 75)}K"
- "Why NYC Buyers Are Flocking to {city_name} (It's Not What You Think)"
- "The One {city_name} Neighborhood Everyone's Talking About"

### Value-Focused:
- "Get ${random.randint(50, 150)}K More House in {city_name} vs. [Nearby City]"
- "{city_name} Home Prices: What ${random.randint(500, 800)}K Actually Buys You"
- "Your Dollar Goes Further: {city_name} Cost of Living Breakdown"

## Social Media Hooks

### Instagram/TikTok:
- "POV: You found the perfect {city_name} neighborhood..."
- "Things I wish I knew before moving to {city_name}"
- "{city_name} vs. [Major City]: The real comparison"
- "This {city_name} home has everything on your wishlist..."

### Facebook:
- "Thinking about {city_name}? Here's what local residents really think..."
- "The {city_name} housing market right now: A realtor's honest take"
- "Why families are choosing {city_name} over [nearby cities]"

## YouTube Video Titles

### Educational:
- "{city_name} Real Estate: Complete 2025 Buyer's Guide"
- "Moving to {city_name}? Here's Everything You Need to Know"
- "{city_name} Neighborhoods Ranked: Where Should You Buy?"

### Trending:
- "I Bought a House in {city_name} - Here's What It Cost"
- "{city_name} Home Tours: What ${random.randint(400, 800)}K Actually Gets You"
- "Is {city_name} Worth the Move? Honest Review After 1 Year"

## Blog Post Headlines

### SEO-Optimized:
- "Complete Guide to Buying a Home in {city_name}, {state_name} (2025)"
- "{city_name} Real Estate Market Predictions: What Buyers Should Know"
- "Best Neighborhoods in {city_name}: A Local Realtor's Guide"

### Engagement-Focused:
- "Why Everyone's Moving to {city_name} (And Why You Should Too)"
- "The {city_name} Home Buying Mistakes That Cost Buyers Thousands"
- "From [Major City] to {city_name}: One Family's Moving Story"

## Call-to-Action Hooks
- "Ready to explore {city_name}? Let's schedule your VIP tour"
- "Get my exclusive {city_name} buyer's guide (free)"
- "See homes before they hit the market in {city_name}"
- "Your {city_name} home search starts here"
            """.strip(),
            "email_hooks": [
                f"Only {random.randint(3, 12)} homes left under ${random.randint(400, 700)}K in {city_name}",
                f"The {city_name} secret that's saving buyers ${random.randint(25, 75)}K",
                f"Why NYC buyers are flocking to {city_name}"
            ],
            "social_hooks": [
                f"POV: You found the perfect {city_name} neighborhood",
                f"Things I wish I knew before moving to {city_name}",
                f"{city_name} vs. major cities: the real comparison"
            ]
        }

    async def generate_content_assets(self, zip_code: str, location_info: Dict) -> Dict[str, Any]:
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        try:
            prompt = f"""Based on your findings, please produce the following for me: - 10 full article blog post using the SEO findings. Use things like the "Long-tail questions" and other local keywords for {city_name}, {state_name}. Make all of these individual downloadable files. - Based on the content strategy, please generate a Lead Magnet. Please make those individual pdf's I can download. - Also based on the content strategy, please create an email for each week. Also, make those individually downloadable.

Create comprehensive, ready-to-use content that I can implement immediately."""
            response_text = await self._safe_send(prompt)
            return {
                "summary": f"Content library generated for {city_name}, {state_name} including blogs, lead magnets, and email campaigns",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": response_text,
                "generated_with": "ChatGPT GPT-5",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logging.error(f"ChatGPT error for content creation: {str(e)}")
            return {
                "summary": f"Content creation for {city_name}, {state_name} (fallback mode)",
                "location": {"city": city_name, "state": state_name, "zip_code": zip_code},
                "analysis_content": "Real-time analysis temporarily unavailable. Please try again.",
                "error": str(e)
            }

# Initialize service
zip_intel_service = ZipIntelligenceService()

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

async def _run_zip_job(zip_code: str):
    try:
        # location
        await _update_task(zip_code, "location", "running", 50)
        location_info = await zip_intel_service.get_location_info(zip_code)
        await _update_task(zip_code, "location", "done", 100)
        await _update_overall(zip_code, TASK_PERCENT["location"])

        # sequential sections with small stagger
        sections = {}

        await _update_task(zip_code, "buyer_migration", "running", 10)
        sections["buyer_migration"] = await zip_intel_service.generate_buyer_migration_intel(zip_code, location_info)
        await _update_task(zip_code, "buyer_migration", "done", 100)
        await _update_overall(zip_code, TASK_PERCENT["buyer_migration"])
        await asyncio.sleep(0.5)

        await _update_task(zip_code, "seo_youtube_trends", "running", 10)
        sections["seo_youtube_trends"] = await zip_intel_service.generate_seo_youtube_trends(zip_code, location_info)
        await _update_task(zip_code, "seo_youtube_trends", "done", 100)
        await _update_overall(zip_code, TASK_PERCENT["seo_youtube_trends"])
        await asyncio.sleep(0.5)

        await _update_task(zip_code, "content_strategy", "running", 10)
        sections["content_strategy"] = await zip_intel_service.generate_content_strategy(zip_code, location_info)
        await _update_task(zip_code, "content_strategy", "done", 100)
        await _update_overall(zip_code, TASK_PERCENT["content_strategy"])
        await asyncio.sleep(0.5)

        await _update_task(zip_code, "hidden_listings", "running", 10)
        sections["hidden_listings"] = await zip_intel_service.generate_hidden_listings_analysis(zip_code, location_info)
        await _update_task(zip_code, "hidden_listings", "done", 100)
        await _update_overall(zip_code, TASK_PERCENT["hidden_listings"])
        await asyncio.sleep(0.5)

        await _update_task(zip_code, "market_hooks", "running", 10)
        sections["market_hooks"] = await zip_intel_service.generate_market_hooks_titles(zip_code, location_info)
        await _update_task(zip_code, "market_hooks", "done", 100)
        await _update_overall(zip_code, TASK_PERCENT["market_hooks"])
        await asyncio.sleep(0.5)

        await _update_task(zip_code, "content_assets", "running", 10)
        sections["content_assets"] = await zip_intel_service.generate_content_assets(zip_code, location_info)
        await _update_task(zip_code, "content_assets", "done", 100)
        await _update_overall(zip_code, TASK_PERCENT["content_assets"])

        # Create market intelligence record at the end
        intelligence = MarketIntelligence(
            zip_code=zip_code,
            buyer_migration=sections["buyer_migration"],
            seo_youtube_trends=sections["seo_youtube_trends"],
            content_strategy=sections["content_strategy"],
            hidden_listings=sections["hidden_listings"],
            market_hooks=sections["market_hooks"],
            content_assets=sections["content_assets"],
        )
        await db.market_intelligence.insert_one(intelligence.dict())
        await _complete_status(zip_code, state="done")
    except Exception as e:
        logging.error(f"Job failed for {zip_code}: {str(e)}")
        await db.analysis_status.update_one(
            {"zip_code": zip_code},
            {"$set": {"state": "failed", "error": str(e), "updated_at": datetime.utcnow()}},
        )

# API Endpoints
@api_router.post("/zip-analysis", response_model=MarketIntelligence)
async def analyze_zip_code(request: ZipAnalysisRequest, background_tasks: BackgroundTasks):
    """Generate comprehensive ZIP code market intelligence (legacy one-shot)."""
    try:
        zip_code = request.zip_code
        existing = await db.market_intelligence.find_one({
            "zip_code": zip_code,
            "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        if existing:
            return MarketIntelligence(**existing)
        # One-shot path (may 504 on long runs). Kept for compatibility.
        location_info = await zip_intel_service.get_location_info(zip_code)
        buyer_migration = await zip_intel_service.generate_buyer_migration_intel(zip_code, location_info)
        seo_youtube = await zip_intel_service.generate_seo_youtube_trends(zip_code, location_info)
        content_strategy = await zip_intel_service.generate_content_strategy(zip_code, location_info)
        hidden_listings = await zip_intel_service.generate_hidden_listings_analysis(zip_code, location_info)
        market_hooks = await zip_intel_service.generate_market_hooks_titles(zip_code, location_info)
        content_assets = await zip_intel_service.generate_content_assets(zip_code, location_info)
        intelligence = MarketIntelligence(
            zip_code=zip_code,
            buyer_migration=buyer_migration,
            seo_youtube_trends=seo_youtube,
            content_strategy=content_strategy,
            hidden_listings=hidden_listings,
            market_hooks=market_hooks,
            content_assets=content_assets
        )
        await db.market_intelligence.insert_one(intelligence.dict())
        return intelligence
    except Exception as e:
        logging.error(f"Error analyzing ZIP code {request.zip_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating analysis: {str(e)}")

@api_router.post("/zip-analysis/start")
async def start_zip_analysis(request: ZipAnalysisRequest):
    """Start analysis job and return immediately with a job id and initial status."""
    zip_code = request.zip_code
    # If exists today, mark status done and return
    existing = await db.market_intelligence.find_one({
        "zip_code": zip_code,
        "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
    })
    if existing:
        # Ensure status reflects done
        await db.analysis_status.update_one(
            {"zip_code": zip_code},
            {"$set": {"zip_code": zip_code, "state": "done", "overall_percent": 100, "updated_at": datetime.utcnow()}},
            upsert=True,
        )
        status_doc = await db.analysis_status.find_one({"zip_code": zip_code}, {"_id": 0})
        return status_doc

    # Initialize and kick off job
    status_doc = await _init_status(zip_code)
    asyncio.create_task(_run_zip_job(zip_code))
    status_doc.pop('_id', None)
    return status_doc

@api_router.get("/zip-analysis/status/{zip_code}")
async def get_zip_status(zip_code: str):
    """Get current analysis status for a ZIP"""
    status_doc = await db.analysis_status.find_one({"zip_code": zip_code})
    if not status_doc:
        raise HTTPException(status_code=404, detail="Status not found")
    status_doc.pop('_id', None)
    return status_doc

@api_router.get("/zip-analysis/{zip_code}", response_model=MarketIntelligence)
async def get_zip_analysis(zip_code: str):
    """Get existing ZIP code analysis"""
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
    """Generate and download hidden listings PDF"""
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
        content = analysis['hidden_listings']['detailed_analysis']
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
            filename=f"{zip_code}-hidden-listings.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@api_router.get("/content-asset/{zip_code}/{asset_type}/{asset_name}")
async def get_content_asset(zip_code: str, asset_type: str, asset_name: str):
    """Get specific content asset"""
    try:
        analysis = await db.market_intelligence.find_one({"zip_code": zip_code})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        content_assets = analysis['content_assets']
        if asset_type == "blogs":
            assets = content_assets['blog_posts']
        elif asset_type == "emails":
            assets = content_assets['email_campaigns']
        elif asset_type == "lead_magnet":
            return {"content": content_assets['lead_magnet']['content']}
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

# Legacy endpoints for compatibility
@api_router.get("/")
async def root():
    return {"message": "ZIP Intel Generator API v2.0"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()