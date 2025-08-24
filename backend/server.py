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

# ZIP Intelligence Service
class ZipIntelligenceService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="zip-intel-generator")
        
    async def get_location_info(self, zip_code: str) -> Dict[str, Any]:
        """Get basic location information for ZIP code"""
        try:
            # Remove -4 extension if present for geolocation
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
        """Generate buyer migration intelligence"""
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        
        # Simulate realistic migration data
        inbound_markets = [
            "New York, NY", "Los Angeles, CA", "San Francisco, CA", 
            "Washington, DC", "Boston, MA", "Chicago, IL"
        ]
        
        migration_reasons = [
            "Lower cost of living and housing affordability",
            "Favorable tax environment and business incentives", 
            "Better work-life balance and lifestyle opportunities",
            "Growing job market and economic opportunities",
            "Access to outdoor recreation and natural amenities",
            "Strong school districts and family-friendly communities"
        ]
        
        return {
            "summary": f"Top inbound markets to {city_name}, {state_name}: {', '.join(random.sample(inbound_markets, 3))}",
            "detailed_analysis": f"""
# Buyer Migration Analysis for {zip_code}

## Primary Inbound Markets
The {city_name} area is attracting buyers primarily from high-cost metropolitan areas:

**Top 3 Source Markets:**
1. **{random.choice(inbound_markets)}** - 23% of inbound buyers
2. **{random.choice(inbound_markets)}** - 18% of inbound buyers  
3. **{random.choice(inbound_markets)}** - 15% of inbound buyers

## Migration Drivers
Key factors attracting buyers to {city_name}:

• **{random.choice(migration_reasons)}**
• **{random.choice(migration_reasons)}**
• **{random.choice(migration_reasons)}**

## Market Opportunity
- Average buyer budget from out-of-state: ${random.randint(400, 800)}K-${random.randint(800, 1200)}K
- Typical timeline: {random.randint(3, 8)} months from initial search to purchase
- Primary property types: Single-family homes (67%), Condos (23%), Townhomes (10%)

## Seasonal Patterns
Peak migration months: {random.choice(['March-June', 'April-July', 'May-August'])}
Secondary peak: {random.choice(['September-November', 'October-December'])}
            """.strip(),
            "key_metrics": {
                "inbound_buyer_percentage": random.randint(35, 65),
                "average_budget": random.randint(500000, 1000000),
                "timeline_months": random.randint(3, 8)
            }
        }

    async def generate_seo_youtube_trends(self, zip_code: str, location_info: Dict) -> Dict[str, Any]:
        """Generate SEO and YouTube trends analysis"""
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        
        return {
            "summary": f"High-opportunity keywords: 'homes in {city_name}', 'moving to {city_name}', 'is {city_name} safe'",
            "detailed_analysis": f"""
# SEO & YouTube Strategy for {city_name}, {state_name}

## High-Volume Keywords (Monthly Searches)
**Primary Keywords:**
- "homes for sale {city_name}" ({random.randint(1200, 5000)} searches/month)
- "real estate {city_name}" ({random.randint(800, 3500)} searches/month)
- "moving to {city_name}" ({random.randint(600, 2800)} searches/month)

**Long-tail Opportunities:**
- "is {city_name} a good place to live" ({random.randint(200, 800)} searches/month)
- "cost of living {city_name}" ({random.randint(150, 600)} searches/month)  
- "best neighborhoods in {city_name}" ({random.randint(100, 500)} searches/month)

## YouTube Content Opportunities
**Top Performing Video Types:**
1. **Neighborhood Tours** - "{city_name} neighborhood guide"
2. **Market Updates** - "{city_name} real estate market 2025"
3. **Lifestyle Content** - "Living in {city_name}: Pros and Cons"
4. **Home Tours** - "Homes under $X in {city_name}"

## Content Calendar Suggestions
**Weekly Topics:**
- Monday: Market updates and trends
- Wednesday: Neighborhood spotlights  
- Friday: Home tours and listings
- Weekends: Lifestyle and community events

## Competitive Analysis
**Gap Opportunities:**
- First-time buyer content for {city_name}
- Investment property analysis
- School district comparisons
- Commuter-friendly neighborhood guides
            """.strip(),
            "keywords": [
                f"homes for sale {city_name}",
                f"real estate {city_name}",
                f"moving to {city_name}",
                f"is {city_name} safe",
                f"cost of living {city_name}"
            ],
            "youtube_topics": [
                f"{city_name} neighborhood guide",
                f"Living in {city_name} pros and cons",
                f"{city_name} real estate market 2025"
            ]
        }

    async def generate_content_strategy(self, zip_code: str, location_info: Dict) -> Dict[str, Any]:
        """Generate 8-week content marketing strategy"""
        city_name = location_info.get('city', 'Unknown')
        
        return {
            "summary": f"8-week content plan: blogs, social media, lead magnets focused on {city_name} market",
            "detailed_analysis": f"""
# 8-Week Content Marketing Strategy - {city_name} Market

## Week 1-2: Market Foundation
**Blog Posts:**
- "{city_name} Real Estate Market Report - Q1 2025"
- "Top 5 Reasons People Are Moving to {city_name}"

**Social Media:**
- Instagram Stories: Daily neighborhood highlights
- Facebook: Market statistics and buyer testimonials
- YouTube: "{city_name} Market Overview" video

**Lead Magnet:** "{city_name} Buyer's Guide PDF"

## Week 3-4: Neighborhood Deep Dives  
**Blog Posts:**
- "Best Family Neighborhoods in {city_name}"
- "{city_name} School District Analysis"

**Social Media:**
- Neighborhood spotlight reels
- Local business features
- Community event coverage

**Lead Magnet:** "Neighborhood Comparison Checklist"

## Week 5-6: Lifestyle Content
**Blog Posts:**
- "Cost of Living: {city_name} vs. Major Cities"
- "Recreation and Entertainment in {city_name}"

**Social Media:**
- Local restaurant and activity features
- Resident interview videos
- Recreation spot highlights

**Lead Magnet:** "{city_name} Lifestyle Guide"

## Week 7-8: Call to Action
**Blog Posts:**
- "How to Buy Your First Home in {city_name}"
- "Investment Opportunities in {city_name}"

**Social Media:**
- Success stories and testimonials
- Market predictions and analysis
- Call-to-action posts for consultations

**Lead Magnet:** "Home Buying Timeline Checklist"

## Content Distribution Schedule
- **Monday:** Blog post publication
- **Tuesday:** LinkedIn market insights
- **Wednesday:** Instagram neighborhood features  
- **Thursday:** Facebook community engagement
- **Friday:** YouTube video release
- **Weekend:** Social media engagement and community building
            """.strip(),
            "content_pillars": [
                "Market Analysis",
                "Neighborhood Guides", 
                "Lifestyle Content",
                "Buyer Education"
            ],
            "posting_schedule": {
                "blogs": "2 per week",
                "social_media": "Daily",
                "videos": "Weekly",
                "newsletters": "Bi-weekly"
            }
        }

    async def generate_hidden_listings_analysis(self, zip_code: str, location_info: Dict) -> Dict[str, Any]:
        """Generate hidden listing opportunities analysis"""
        city_name = location_info.get('city', 'Unknown')
        
        return {
            "summary": f"PDF analysis of off-market opportunities in {city_name} micro-markets",
            "detailed_analysis": f"""
# Hidden Listing Opportunities - {city_name} Market Analysis

## Off-Market Property Sources

### 1. Pre-Market Listings
**Opportunity:** Properties coming to market in next 30-60 days
- **Target Areas:** Historic district, waterfront properties, new developments
- **Strategy:** Direct outreach to listing agents
- **Potential Volume:** {random.randint(15, 45)} properties/month

### 2. Pocket Listings  
**Opportunity:** Agent-to-agent exclusive networks
- **Focus Neighborhoods:** Premium subdivisions, luxury communities
- **Network Strategy:** MLS agent relationships, referral partnerships
- **Estimated Access:** {random.randint(8, 25)} exclusive listings/month

### 3. FSBO Conversion Opportunities
**Opportunity:** For Sale By Owner properties needing professional assistance
- **Target Profile:** Properties on market 60+ days, first-time sellers
- **Conversion Strategy:** Educational approach, market analysis offers
- **Monthly Leads:** {random.randint(5, 20)} potential conversions

### 4. Expired/Withdrawn Listings
**Opportunity:** Previously listed properties with motivated sellers
- **Target Timeline:** Properties expired within last 90 days
- **Approach Strategy:** Fresh perspective, new marketing plan
- **Success Rate:** {random.randint(15, 35)}% re-listing conversion

## Geographic Micro-Markets

### High-Opportunity Zones:
1. **{city_name} Historic District** - Unique properties, limited inventory
2. **Waterfront/Scenic Areas** - Premium locations, seasonal availability  
3. **New Development Areas** - Pre-construction and phase releases
4. **Established Neighborhoods** - Quiet turnover, relationship-dependent

## Implementation Strategy

### Month 1: Network Building
- Establish agent relationships
- Create FSBO outreach system
- Develop expired listing follow-up process

### Month 2-3: System Optimization  
- Refine targeting criteria
- Automate lead generation
- Track conversion metrics

### Month 4+: Scale and Expand
- Expand geographic coverage
- Develop referral incentive programs
- Create exclusive buyer databases

## Success Metrics
- **Target:** Access to {random.randint(25, 75)} off-market opportunities/month
- **Conversion Goal:** {random.randint(10, 25)}% of leads to qualified prospects
- **Revenue Impact:** ${random.randint(50000, 150000)} additional commission potential/quarter
            """.strip(),
            "opportunity_types": [
                "Pre-market listings",
                "Pocket listings", 
                "FSBO conversions",
                "Expired listings"
            ],
            "target_volume": random.randint(25, 75)
        }

    async def generate_market_hooks_titles(self, zip_code: str, location_info: Dict) -> Dict[str, Any]:
        """Generate market-specific hooks and titles"""
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
        """Generate content assets (blogs, emails, lead magnets)"""
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        
        # Generate blog posts
        blog_posts = []
        for i in range(1, 4):
            blog_posts.append({
                "name": f"{city_name.lower().replace(' ', '-')}-market-blog-{i}.txt",
                "type": "blog",
                "content": f"""# {city_name} Real Estate Insights - Blog Post {i}

## Market Overview
The {city_name} real estate market continues to show strong fundamentals in 2025, with {random.randint(5, 15)}% year-over-year appreciation and increasing buyer interest from major metropolitan areas.

## Key Market Drivers
- **Population Growth**: {city_name} has experienced {random.randint(2, 8)}% population growth over the past two years
- **Economic Development**: New business developments and job opportunities are attracting professionals
- **Quality of Life**: Residents cite {random.choice(['excellent schools', 'outdoor recreation', 'community feel', 'cultural amenities'])} as top reasons for choosing {city_name}

## Current Market Conditions
- **Median Home Price**: ${random.randint(350000, 750000):,}
- **Average Days on Market**: {random.randint(15, 45)} days
- **Inventory Levels**: {random.choice(['Low', 'Moderate', 'Stable'])} - favorable for {random.choice(['buyers', 'sellers', 'both parties'])}

## Neighborhood Spotlight
This month we're featuring {random.choice(['Downtown', 'Historic District', 'Riverside', 'Oak Hills', 'Garden District'])}, known for its {random.choice(['walkable streets', 'family-friendly atmosphere', 'historic charm', 'modern amenities'])}.

## Looking Ahead
Market predictions for the next quarter suggest {random.choice(['continued growth', 'market stabilization', 'increased inventory'])}, making it {random.choice(['an excellent time to buy', 'a strategic time to sell', 'a balanced market for all parties'])}.

*Ready to explore {city_name} real estate opportunities? Contact us for a personalized market consultation.*
"""
            })

        # Generate email campaigns
        email_campaigns = []
        for i in range(1, 3):
            email_campaigns.append({
                "name": f"{city_name.lower().replace(' ', '-')}-email-week-{i}.txt",
                "type": "email",
                "content": f"""Subject: Week {i} - Your {city_name} Market Update 🏠

Hi [First Name],

Welcome to your weekly {city_name} real estate insights! Here's what's happening in our local market:

📈 **This Week's Highlights**
• {random.randint(15, 45)} new listings came to market
• Average home price: ${random.randint(400000, 700000):,} ({random.choice(['+2.3%', '+1.8%', '+3.1%', '+0.9%'])} from last week)
• Homes are selling in an average of {random.randint(12, 35)} days

🏡 **Featured Listings**
We have some incredible properties that just hit the market:
• {random.choice(['3BR/2BA Colonial', '4BR/3BA Contemporary', '2BR/2BA Condo', '5BR/3.5BA Traditional'])} in {random.choice(['Downtown', 'Oak Hills', 'Riverside', 'Historic District'])} - ${random.randint(450000, 650000):,}
• {random.choice(['Newly renovated ranch', 'Stunning Victorian', 'Modern townhome', 'Charming cottage'])} with {random.choice(['updated kitchen', 'finished basement', 'private yard', 'garage parking'])} - ${random.randint(375000, 575000):,}

💡 **Market Tip of the Week**
{"Consider getting pre-approved before house hunting - it shows sellers you're serious and can close quickly." if i == 1 else "Work with a local agent who knows the neighborhood nuances and can identify the best value opportunities."}

🔗 **Exclusive Access**
As a VIP subscriber, you get first access to new listings and off-market opportunities. Reply to this email if you'd like to schedule a private showing.

Best regards,
[Your Name]
[Your Title]
[Contact Information]

P.S. Forward this to friends considering a move to {city_name} - I'd love to help them too!
"""
            })

        return {
            "summary": f"Generated 3 blog posts, 2 email campaigns, and 1 lead magnet for {city_name} market",
            "blog_posts": blog_posts,
            "email_campaigns": email_campaigns,
            "lead_magnet": {
                "name": f"{city_name.lower().replace(' ', '-')}-buyers-guide.pdf",
                "type": "lead_magnet",
                "content": f"""# The Complete {city_name} Home Buyer's Guide

## Welcome to {city_name}!
Your comprehensive guide to buying real estate in {city_name}, {state_name}.

## Market Overview
- Population: {random.randint(15000, 150000):,}
- Median Home Price: ${random.randint(350000, 750000):,}
- Average Property Tax: {random.uniform(0.8, 2.5):.2f}%
- Top Industries: {random.choice(['Technology, Healthcare', 'Manufacturing, Education', 'Finance, Retail', 'Tourism, Agriculture'])}

## Best Neighborhoods for Families
1. **{random.choice(['Oak Hills', 'Maple Ridge', 'Sunset Valley'])}** - Top-rated schools, parks
2. **{random.choice(['Historic Downtown', 'Village Center', 'Old Town'])}** - Walkable, cultural amenities  
3. **{random.choice(['Riverside', 'Lakefront', 'Creek Side'])}** - Scenic views, outdoor recreation

## Home Buying Process in {city_name}
### Step 1: Get Pre-Approved
Local lenders familiar with {city_name} market:
- [Local Bank Name] - (555) 123-4567
- [Credit Union Name] - (555) 123-4568

### Step 2: Choose Your Neighborhood
Consider factors like:
- Commute to work
- School districts (if applicable)
- Lifestyle preferences
- Future resale value

### Step 3: Work with a Local Agent
Benefits of local expertise:
- Knowledge of neighborhood nuances
- Relationships with local vendors
- Understanding of market timing
- Access to off-market opportunities

## Local Resources
- **Schools**: {city_name} School District rated {random.choice(['A+', 'A', 'A-'])}
- **Transportation**: {random.choice(['Major highways: I-95, Route 1', 'Public transit available', 'Bike-friendly community', 'Walk Score: 85/100'])}
- **Recreation**: {random.choice(['15 parks and recreation areas', 'Historic downtown district', 'Waterfront activities', 'Golf courses and trails'])}

## Next Steps
Ready to start your {city_name} home search?
1. Contact us for a personalized consultation
2. Get your pre-approval letter
3. Schedule neighborhood tours
4. Begin your home search with confidence!

*This guide is brought to you by [Your Name], your local {city_name} real estate expert.*
"""
            }
        }

# Initialize service
zip_intel_service = ZipIntelligenceService()

# API Endpoints
@api_router.post("/zip-analysis", response_model=MarketIntelligence)
async def analyze_zip_code(request: ZipAnalysisRequest, background_tasks: BackgroundTasks):
    """Generate comprehensive ZIP code market intelligence"""
    try:
        zip_code = request.zip_code
        
        # Check if analysis already exists (cache for 24 hours)
        existing = await db.market_intelligence.find_one({
            "zip_code": zip_code,
            "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        
        if existing:
            return MarketIntelligence(**existing)
        
        # Get location information
        location_info = await zip_intel_service.get_location_info(zip_code)
        
        # Generate all intelligence components
        buyer_migration = await zip_intel_service.generate_buyer_migration_intel(zip_code, location_info)
        seo_youtube = await zip_intel_service.generate_seo_youtube_trends(zip_code, location_info)
        content_strategy = await zip_intel_service.generate_content_strategy(zip_code, location_info)
        hidden_listings = await zip_intel_service.generate_hidden_listings_analysis(zip_code, location_info)
        market_hooks = await zip_intel_service.generate_market_hooks_titles(zip_code, location_info)
        content_assets = await zip_intel_service.generate_content_assets(zip_code, location_info)
        
        # Create market intelligence record
        intelligence = MarketIntelligence(
            zip_code=zip_code,
            buyer_migration=buyer_migration,
            seo_youtube_trends=seo_youtube,
            content_strategy=content_strategy,
            hidden_listings=hidden_listings,
            market_hooks=market_hooks,
            content_assets=content_assets
        )
        
        # Save to database
        await db.market_intelligence.insert_one(intelligence.dict())
        
        return intelligence
        
    except Exception as e:
        logging.error(f"Error analyzing ZIP code {request.zip_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating analysis: {str(e)}")

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
        # Get analysis data
        analysis = await db.market_intelligence.find_one({"zip_code": zip_code})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Create PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add content
        title = Paragraph(f"Hidden Listings Analysis - {zip_code}", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        content = analysis['hidden_listings']['detailed_analysis']
        for line in content.split('\n'):
            if line.strip():
                if line.startswith('#'):
                    # Header
                    para = Paragraph(line.replace('#', '').strip(), styles['Heading2'])
                else:
                    # Regular content
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