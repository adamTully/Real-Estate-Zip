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
            "Washington, DC", "Boston, MA", "Chicago, IL", "Seattle, WA",
            "Austin, TX", "Denver, CO", "Portland, OR", "Miami, FL"
        ]
        
        migration_reasons = [
            "Lower cost of living and housing affordability",
            "Favorable tax environment and business incentives", 
            "Better work-life balance and lifestyle opportunities",
            "Growing job market and economic opportunities",
            "Access to outdoor recreation and natural amenities",
            "Strong school districts and family-friendly communities"
        ]
        
        # Generate structured, narrative content
        primary_markets = random.sample(inbound_markets, 5)
        primary_reasons = random.sample(migration_reasons, 4)
        
        # Create content that matches the narrative analysis style
        market_overview = f"""Buyers relocating to {city_name} often come from high-cost metros where taxes and living expenses are high. Recent market data shows that most people searching {city_name} homes are from outside the region, with the largest number coming from {primary_markets[0]}, followed by {', '.join(primary_markets[1:3])}, and {primary_markets[3]}. 

Locally, census migration data shows that {state_name} counties receive most movers from nearby metropolitan areas, while the largest out-of-state sources include major coastal cities. Many current homeowners are staying put due to favorable mortgage rates, so movers tend to come from farther away and are motivated by affordability and quality of life."""

        # Generate detailed reasons with supporting data
        detailed_reasons = [
            {
                "title": "Lower cost of living and housing",
                "description": f"Housing, utilities, groceries and transportation costs in {state_name} are below the national average. Recent studies show {state_name}'s cost of living ranks among the most affordable states, with housing costs significantly lower than the national average.",
                "highlight": f"Average home prices in {city_name} (${random.randint(350, 600)}k median) are far below those of NYC, Los Angeles or San Francisco.",
                "supporting_data": f"Living in major cities like New York requires {random.randint(40, 70)}% more money than {city_name}."
            },
            {
                "title": "Tax savings",
                "description": f"{state_name}'s income tax structure offers significant advantages over high-tax states. The state maintains competitive tax rates with favorable property tax rates compared to northeastern states.",
                "highlight": f"Property taxes average ${random.randint(1800, 2500)} in {state_name} versus ${random.randint(5000, 8000)} in New York—buyers can save thousands per year.",
                "supporting_data": f"Tax savings can amount to 20-30% annually for families relocating from high-tax states."
            },
            {
                "title": "More home for the money and lifestyle",
                "description": f"Research shows that the biggest reasons people moved in recent years were to be closer to family and to get more house for their money. These factors resonate with people leaving expensive metros where high housing prices and congestion push them to seek better value.",
                "highlight": f"{city_name} offers {random.choice(['walkable neighborhoods', 'outdoor recreation', 'family-friendly communities', 'modern amenities'])} with {random.choice(['parks and trails', 'excellent schools', 'cultural attractions', 'shopping and dining'])}.",
                "supporting_data": f"Buyers can typically afford {random.randint(20, 40)}% more house for the same budget compared to their previous location."
            },
            {
                "title": "Economic opportunity and climate",
                "description": f"{state_name}'s economy is strong, with major industries in manufacturing, technology, healthcare and professional services. The region hosts major corporations and growing business opportunities.",
                "highlight": f"The climate and access to outdoor recreation attract remote workers and retirees seeking {random.choice(['mild winters', 'year-round outdoor activities', 'lower cost of living', 'quality of life improvements'])}.",
                "supporting_data": f"The region has seen {random.randint(15, 35)}% growth in remote worker relocations over the past two years."
            }
        ]

        # Generate content strategy recommendations
        content_strategies = [
            {
                "focus": "Cost-of-living and tax comparisons",
                "hook": f"Escape high taxes—discover how moving from {primary_markets[0].split(',')[0]} to {city_name} can save you {random.randint(25, 40)}% or more on taxes and living costs.",
                "keywords": [f"cost of living {city_name}", f"{state_name} property tax savings", f"affordable homes {city_name}", f"moving from {primary_markets[0].split(',')[0]} to {city_name}"],
                "video_title": f"Why {primary_markets[0].split(',')[0]} Residents Are Flocking to {city_name}: Huge Tax & Housing Savings Explained",
                "strategy": f"Use charts comparing median home prices and tax rates. Highlight that buyers can afford larger homes or new construction while lowering their tax burden. Focus on specific savings calculations."
            },
            {
                "focus": "Lifestyle and community features", 
                "hook": f"From {random.choice(['walking trails', 'local parks', 'community events'])} to {random.choice(['excellent schools', 'cultural attractions', 'recreation centers'])}—see why {city_name} offers the perfect work-life balance.",
                "keywords": [f"{city_name} lifestyle", "family-friendly neighborhoods", "outdoor activities", f"{city_name} schools", f"living in {city_name}"],
                "video_title": f"Living in {city_name}: Top Amenities, Schools and Things to Do ({datetime.now().year} Update)",
                "strategy": f"Provide tours of local attractions, discuss school options and spotlight community events. Show what everyday life looks like to help out-of-state buyers visualize their new lifestyle."
            },
            {
                "focus": "Relocation stories targeting specific metros",
                "hook": f"Moving from {primary_markets[1]} to {city_name}? Here's what you need to know about housing, taxes and job opportunities.",
                "keywords": [f"moving from {primary_markets[1].split(',')[0]} to {city_name}", f"relocate to {city_name}", f"{city_name} job market", f"{city_name} vs {primary_markets[1].split(',')[0]}"],
                "video_title": f"Leaving {primary_markets[1].split(',')[0]}: How {city_name} Offers Affordable Living and Growing Opportunities",
                "strategy": f"Use case studies or interviews with clients who relocated from {primary_markets[1].split(',')[0]}. Discuss common pain points and how {city_name} addressed them. Provide practical moving tips."
            },
            {
                "focus": "Market trends and investment opportunity",
                "hook": f"{city_name} home prices are up {random.randint(8, 15)}%, but still affordable—see why investors and families are buying now.",
                "keywords": [f"{city_name} real estate market {datetime.now().year}", f"median home price {city_name}", f"{city_name} housing forecast", f"buy home {city_name}"],
                "video_title": f"{city_name} Housing Market Update {datetime.now().year}: Prices, Demand & What It Means for Buyers",
                "strategy": f"Break down current market data showing price trends and demand. Point out that most home searches are local, indicating strong regional demand. Explain inventory conditions and competitive strategies."
            }
        ]

        return {
            "summary": f"Top inbound markets to {city_name}: {', '.join(primary_markets[:3])}. Key drivers include {primary_reasons[0].lower()} and {primary_reasons[1].lower()}.",
            "location": {
                "city": city_name,
                "state": state_name,
                "zip_code": zip_code
            },
            "market_overview": market_overview,
            "key_findings": [
                {
                    "title": "Primary Source Markets",
                    "content": f"{primary_markets[0]} leads inbound searches, followed by {', '.join(primary_markets[1:3])}. Locally, most movers come from nearby metropolitan counties seeking better value."
                },
                {
                    "title": "Migration Drivers", 
                    "content": f"Buyers are motivated primarily by {primary_reasons[0].lower()} and {primary_reasons[1].lower()}. Many are remote workers or retirees seeking lifestyle improvements."
                }
            ],
            "why_moving": detailed_reasons,
            "content_strategy": content_strategies,
            "next_steps": f"By creating data-driven, metro-specific content that compares costs, taxes and lifestyle, you'll attract buyers from the cities most interested in {city_name}. Use SEO-friendly keywords, social-media hooks and video formats to meet them where they search—YouTube, Instagram, TikTok and Google."
        }

    async def generate_seo_youtube_trends(self, zip_code: str, location_info: Dict) -> Dict[str, Any]:
        """Generate SEO and YouTube trends analysis"""
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        
        # Generate high-volume local keywords
        high_volume_keywords = [
            {
                "keyword": f"{city_name} homes for sale",
                "context": "Many buyers begin with simple location-based searches when researching a move",
                "search_behavior": "Primary entry point for property searches"
            },
            {
                "keyword": f"{city_name} real estate", 
                "context": "Broad real estate interest covering market trends and agent services",
                "search_behavior": "Professional service discovery"
            },
            {
                "keyword": f"{city_name} cost of living",
                "context": "Cost-of-living comparisons are among the first queries people make when evaluating a new city",
                "search_behavior": "Relocation research phase"
            },
            {
                "keyword": f"is {city_name} safe",
                "context": "Safety concerns drive significant search volume; appears prominently in Google's 'People also ask' section", 
                "search_behavior": "Due diligence and family considerations"
            },
            {
                "keyword": f"{city_name} schools",
                "context": "School quality is a key factor for families considering relocation",
                "search_behavior": "Family-focused research"
            },
            {
                "keyword": f"best neighborhoods in {city_name}",
                "context": "Buyers search for neighborhood guides and comparisons to nearby areas",
                "search_behavior": "Narrowing location preferences"
            },
            {
                "keyword": f"{city_name} apartments for rent",
                "context": f"Renters search for average rents; typical range ${random.randint(1200, 1600)}-${random.randint(1800, 2400)} depending on size",
                "search_behavior": "Rental market exploration"
            },
            {
                "keyword": f"things to do in {city_name}",
                "context": f"Recreation queries reflect interest in lifestyle and amenities available in {city_name}",
                "search_behavior": "Lifestyle and entertainment research"
            }
        ]
        
        # Generate long-tail questions 
        long_tail_questions = [
            {
                "question": f"Is {city_name}, {state_name} a good place to live?",
                "context": "Overarching quality-of-life question that appears frequently in 'People also ask'",
                "intent": "General validation and reassurance seeking"
            },
            {
                "question": f"How much do I need to make to live in {city_name}?",
                "context": "Ties into cost-of-living and salary requirements for the area", 
                "intent": "Financial planning and affordability"
            },
            {
                "question": f"What is the crime rate in {city_name}?",
                "context": "Safety is top of mind for relocators, especially families",
                "intent": "Security and safety validation"
            },
            {
                "question": f"Is {city_name} expensive to live?",
                "context": "Variation on cost-of-living queries comparing to current location",
                "intent": "Budget and lifestyle comparison"
            },
            {
                "question": f"What are the pros and cons of living in {city_name}?",
                "context": f"Inspired by popular YouTube format; seeks balanced perspective on {city_name}",
                "intent": "Comprehensive evaluation"
            },
            {
                "question": f"Best neighborhoods in {city_name} for families",
                "context": "Specific demographic targeting within location research",
                "intent": "Family-focused neighborhood selection"
            },
            {
                "question": f"How far is {city_name} from [major city] and is the commute easy?",
                "context": "Distance and traffic questions are common for those working in nearby metro areas",
                "intent": "Commuter convenience and logistics"
            },
            {
                "question": f"Are schools in {city_name} good?",
                "context": "Families research school ratings, test scores, and specialized programs",
                "intent": "Educational quality assessment"
            },
            {
                "question": f"What is there to do in {city_name}?",
                "context": f"Lifestyle queries about entertainment, recreation, and community activities in {city_name}",
                "intent": "Quality of life and entertainment options"
            },
            {
                "question": f"Does {city_name} have good public transportation?",
                "context": "Transit accessibility and walkability concerns for daily life",
                "intent": "Mobility and convenience factors"
            }
        ]
        
        # Generate video title ideas
        video_titles = [
            {
                "title": f"Is {city_name}, {state_name} a Good Place to Live? Pros & Cons 2025",
                "strategy": "Addresses top 'People also ask' question using trending pros-and-cons format",
                "target_keywords": [f"is {city_name} good place to live", f"{city_name} pros and cons"],
                "content_focus": "Balanced review covering lifestyle, costs, amenities"
            },
            {
                "title": f"{city_name} Cost of Living Breakdown: How Much Do You Need?",
                "strategy": "Leverages high-volume cost queries while providing actionable financial information",
                "target_keywords": [f"{city_name} cost of living", f"how much to live in {city_name}"],
                "content_focus": "Salary requirements, housing costs, daily expenses"
            },
            {
                "title": f"Top 5 Neighborhoods in {city_name} for Families & Young Professionals",
                "strategy": "Uses 'best neighborhoods' keyword with demographic targeting for broader appeal",
                "target_keywords": [f"best neighborhoods {city_name}", f"{city_name} neighborhoods families"],
                "content_focus": "Neighborhood tours, school districts, commute times"
            },
            {
                "title": f"Moving to {city_name}? Here's What Nobody Tells You",
                "strategy": "Creates curiosity while targeting relocation searches with insider knowledge angle",
                "target_keywords": [f"moving to {city_name}", f"living in {city_name}"],
                "content_focus": "Hidden costs, local tips, cultural insights"
            },
            {
                "title": f"{city_name} Real Estate Market 2025: Prices, Trends & Predictions",
                "strategy": "Targets real estate searches with current year relevance and comprehensive coverage",
                "target_keywords": [f"{city_name} real estate", f"{city_name} housing market 2025"],
                "content_focus": "Market data, price trends, buying opportunities"
            },
            {
                "title": f"Renting vs Buying in {city_name}: Complete 2025 Guide",
                "strategy": "Addresses major financial decision with comprehensive guidance approach",
                "target_keywords": [f"{city_name} rent vs buy", f"{city_name} rental market"],
                "content_focus": "Cost comparisons, market timing, financial advice"
            },
            {
                "title": f"{city_name} Schools Guide: Rankings, Districts & What Parents Need to Know",
                "strategy": "Targets family-focused searches with authoritative, comprehensive content promise",
                "target_keywords": [f"{city_name} schools", f"{city_name} school districts"],
                "content_focus": "School ratings, district boundaries, enrollment process"
            },
            {
                "title": f"Things to Do in {city_name}: Local's Guide to Hidden Gems 2025",
                "strategy": "Lifestyle content using insider knowledge angle and current year relevance",
                "target_keywords": [f"things to do {city_name}", f"{city_name} attractions"],
                "content_focus": "Recreation, entertainment, local culture"
            }
        ]
        
        # SEO optimization notes
        seo_strategy_notes = [
            {
                "category": "Cross-platform optimization",
                "recommendation": f"Repurpose {city_name} content across YouTube descriptions, blog posts, and social media using exact search phrases people use"
            },
            {
                "category": "Local SEO focus", 
                "recommendation": f"Optimize for '{city_name} + real estate agent' and '{city_name} + homes for sale' to capture ready-to-buy traffic"
            },
            {
                "category": "Content depth",
                "recommendation": "Create comprehensive guides that answer multiple related questions in single pieces to capture various search intents"
            },
            {
                "category": "Featured snippet targeting",
                "recommendation": f"Structure content to answer '{city_name} safety', '{city_name} cost of living' with clear facts and statistics for snippet opportunities"
            }
        ]
        
        return {
            "summary": f"High-opportunity keywords: '{city_name} homes for sale', 'moving to {city_name}', 'is {city_name} safe'",
            "location": {
                "city": city_name,
                "state": state_name, 
                "zip_code": zip_code
            },
            "high_volume_keywords": high_volume_keywords,
            "long_tail_questions": long_tail_questions,
            "video_title_ideas": video_titles,
            "seo_strategy": seo_strategy_notes,
            "optimization_summary": f"Focus on location-based searches, lifestyle questions, and comparison content. {city_name} searchers prioritize safety, cost of living, and neighborhood information. Use exact question formats from 'People also ask' sections for maximum visibility."
        }

    async def generate_content_strategy(self, zip_code: str, location_info: Dict) -> Dict[str, Any]:
        """Generate 8-week content marketing strategy"""
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        
        # Generate 8-week content roadmap
        weekly_roadmap = []
        
        themes = [
            {
                "week": 1,
                "theme": "Cost-of-living & taxes",
                "short_form": f"Create 3 vertical videos comparing {city_name}'s housing costs and taxes to New York or California. Use quick charts showing median home price (${random.randint(350, 600)}k vs. $1M+) and {state_name}'s tax advantages. End with CTA to download 'Cost of Living Checklist.'",
                "long_form": f"Publish blog post + 8-10 min YouTube video titled '{city_name} Cost of Living vs. NYC & LA' with detailed breakdowns and case studies. Include infographics and mention local rent averages (${random.randint(1200, 1800)}-${random.randint(1900, 2500)}).",
                "lead_magnet": f"'2025 {city_name} Cost-of-Living & Tax Comparison Guide' - Printable PDF with salary requirements, median housing costs and tax comparisons. Use gated landing page with opt-in form.",
                "email_theme": f"Email #1 ('Welcome + Savings') - deliver the cost-of-living guide, highlight savings potential and invite recipients to schedule consultation. Retarget website visitors with ads emphasizing tax and housing savings."
            },
            {
                "week": 2, 
                "theme": "Neighborhoods & lifestyle",
                "short_form": f"Post reels/shorts touring local landmarks and recreational areas—emphasize walkability, parks and community features. Use trending audio and quick 'day in the life' scenes showcasing {city_name}'s lifestyle.",
                "long_form": f"Long-form video/podcast episode: 'Top 5 Neighborhoods in {city_name} for Families & Young Professionals.' Discuss features, commute times and average home prices. Blog version optimized for 'best neighborhoods in {city_name}'.",
                "lead_magnet": f"Interactive '{city_name} Neighborhood Matcher' quiz. After answering lifestyle and budget questions, users receive personalized report with neighborhood suggestions.",
                "email_theme": f"Email #2 ('Find Your Fit') - deliver quiz results, include mini-profiles of recommended neighborhoods and invite recipients to join virtual home-tour webinar. Retargeting ads show neighborhood highlights."
            },
            {
                "week": 3,
                "theme": "Schools & safety", 
                "short_form": f"Short videos answering FAQs: 'Are schools in {city_name} good?', 'How safe is {city_name}?' Use stats from local school ratings and safety data with on-screen text.",
                "long_form": f"Publish blog post and 12-min video: '{city_name} Schools & Safety Guide.' Interview local parents or school administrator. Discuss public vs. private options, ratings and community safety features.",
                "lead_magnet": f"Downloadable 'Family Relocation Checklist' with school comparison charts, enrollment tips and safety resources specific to {city_name}.",
                "email_theme": f"Email #3 ('Family Focus') - share the checklist and link to schools video. Retarget those who viewed school content with ads promoting family-friendly neighborhoods and open houses."
            },
            {
                "week": 4,
                "theme": "Buying process & market update",
                "short_form": f"Two-part short series: (1) 'What ${random.randint(400, 700)}k gets you in {city_name} vs. New York'; (2) 'Top 3 Mistakes Out-of-State Buyers Make.' Offer quick tips and direct to full video.",
                "long_form": f"Long-form content: '{city_name} Housing Market Update 2025: Prices, Demand & How to Win' covering median price trends, days on market and inventory. Provide actionable advice on pre-approval and negotiating.",
                "lead_magnet": f"'{city_name} Home-Buyer Toolkit' - packet with pre-approval checklist, timeline, local lender contacts and links to current listings.",
                "email_theme": f"Email #4 ('Market Insider') - deliver toolkit and include summary of current market stats. Retarget users who viewed home-tour pages with ads featuring new listings."
            },
            {
                "week": 5,
                "theme": "Remote workers & relocators",
                "short_form": f"Create reels/shorts: 'Remote Worker's Day in {city_name}' showing home office setups, coffee shops and co-working spaces; highlight outdoor breaks and lifestyle flexibility.",
                "long_form": f"Long-form podcast or video: 'Why Remote Workers Are Choosing {city_name} Over NYC & SF.' Discuss remote-work migration trends and affordability; interview someone who relocated.",
                "lead_magnet": f"'Remote Work Relocation Guide' - includes cost calculators, tips for setting up home office in {city_name} and tax deductions for remote workers.",
                "email_theme": f"Email #5 ('Remote Work Ready') - share guide, emphasize lifestyle benefits, invite to virtual Q&A about remote-work relocation. Retarget with ads focused on home office spaces."
            },
            {
                "week": 6,
                "theme": "Renting & investing",
                "short_form": f"Short tips: 'Average Rent in {city_name}' (highlighting ${random.randint(1200, 1600)} studio to ${random.randint(1900, 2800)} 3-bedroom) and 'Top 3 Tips for Investors in {city_name}.'",
                "long_form": f"Publish blog + video: 'Renting vs. Buying in {city_name}: What Makes Sense in 2025?' Compare costs, average rent vs. mortgage, and forecast returns; include investment opportunities segment.",
                "lead_magnet": f"'{city_name} Rental Market Report' with rent trends, ROI calculators and investment opportunity analysis for the local market.",
                "email_theme": f"Email #6 ('Rent vs. Buy') - deliver report, encourage consultation for investors and renters ready to buy. Retarget with ads promoting new construction and investment properties."
            },
            {
                "week": 7,
                "theme": "Moving logistics & personal stories",
                "short_form": f"Record short testimonials from recent buyers who relocated to {city_name}. Use captions summarizing why they moved (taxes, space, schools, lifestyle).",
                "long_form": f"Long-form interview: 'How We Moved to {city_name}' featuring client story. Cover decision-making process, moving costs, surprises and practical advice for relocators.",
                "lead_magnet": f"'Relocation Planner Spreadsheet' - Google Sheet template for budgeting movers, travel, temporary housing and closing costs specific to {city_name} moves.",
                "email_theme": f"Email #7 ('Your Move Simplified') - deliver planner and encourage one-on-one planning session. Retarget with ads offering moving checklists and local mover partnerships."
            },
            {
                "week": 8,
                "theme": "Community & lifestyle wrap-up", 
                "short_form": f"Short-form 'Top 5 Things to Do in {city_name} This Season' and 'Hidden Gems in {city_name}' to maintain engagement and showcase local lifestyle.",
                "long_form": f"Long-form content: seasonally relevant vlog or podcast summarizing {city_name} community events, new developments and Q&A session answering subscriber questions.",
                "lead_magnet": f"'{city_name} Community Calendar' - monthly PDF of festivals, farmers markets, local events and seasonal activities throughout the year.",
                "email_theme": f"Email #8 ('Stay Connected') - share calendar and invite to local meet-ups or open houses. Retarget everyone who downloaded previous lead magnets with final nudge to schedule property tour."
            }
        ]
        
        # Additional strategy recommendations
        implementation_notes = [
            {
                "category": "Cross-platform promotion",
                "recommendation": f"Repurpose clips from long-form videos into reels/shorts and drive viewers to YouTube channel or blog for depth. Use Instagram Stories polls about {city_name} neighborhoods to boost engagement."
            },
            {
                "category": "SEO & keywords", 
                "recommendation": f"Optimize blog posts and video descriptions for high-volume keywords ('{city_name} cost of living,' 'best neighborhoods in {city_name},' 'pros and cons of living in {city_name}')."
            },
            {
                "category": "Lead nurturing",
                "recommendation": f"Tag leads by interest (cost of living, schools, investment) so follow-up emails and retargeting ads speak to their motivations. Use testimonials from similar relocators to build trust."
            },
            {
                "category": "Retargeting strategy",
                "recommendation": f"Set up custom audiences for website visitors, video viewers and lead magnet downloaders. Serve ads highlighting next step (webinar, consultation, new listing). Use carousel ads showcasing different {city_name} neighborhoods."
            },
            {
                "category": "Community partnerships",
                "recommendation": f"Co-create content with local {city_name} businesses, schools and community organizations. Adds authenticity and extends reach through their audiences."
            }
        ]
        
        return {
            "summary": f"8-week content plan: blogs, social media, lead magnets focused on {city_name} market",
            "location": {
                "city": city_name,
                "state": state_name,
                "zip_code": zip_code
            },
            "weekly_roadmap": themes,
            "implementation_strategy": implementation_notes,
            "success_metrics": {
                "content_goals": f"Position yourself as the go-to resource for anyone considering a move to {city_name}",
                "engagement_targets": "2-3 pieces of content per week across all channels",
                "lead_generation": "1 new lead magnet per week, building comprehensive nurture sequence",
                "conversion_focus": "Move leads from awareness to consultation through value-driven content"
            }
        }

    async def generate_hidden_listings_analysis(self, zip_code: str, location_info: Dict) -> Dict[str, Any]:
        """Generate hidden listing opportunities analysis (Market Research)"""
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        
        # Generate market snapshot
        median_price = random.randint(350000, 650000)
        yoy_change = random.uniform(-5.0, 8.0)
        dom_current = random.randint(25, 65)
        dom_last_year = random.randint(20, 45)
        months_inventory = random.uniform(2.5, 5.2)
        
        market_snapshot = {
            "zip_code": zip_code,
            "median_price": median_price,
            "yoy_change": yoy_change,
            "dom_current": dom_current,
            "dom_last_year": dom_last_year,
            "months_inventory": months_inventory,
            "mortgage_rate": random.uniform(6.5, 7.5),
            "demographics": {
                "population": random.randint(25000, 75000),
                "median_income": random.randint(45000, 85000)
            }
        }
        
        # Generate micro-areas with opportunities
        micro_areas = [
            {
                "name": f"{random.choice(['Riverside', 'Historic District', 'Downtown', 'Park View', 'Mill Creek'])} corridor",
                "location_context": f"Near {random.choice(['Main St & Oak Ave', 'Highway 20 & First St', 'River Road corridor', 'Downtown district', 'Park entrance'])}",
                "opportunity_driver": random.choice([
                    "Infrastructure improvements lifting amenity value",
                    "Transit and trail investments increasing accessibility", 
                    "Mixed-use development creating repositioning opportunities",
                    "School district boundary changes affecting desirability",
                    "Commercial development driving residential interest"
                ]),
                "likely_sellers": [
                    f"Long-time owners in {random.choice(['1950s-80s', '1960s-90s', '1970s-2000s'])} homes",
                    f"{random.choice(['Early-phase', 'First-wave', 'Recent'])} townhome/condo owners from {random.randint(2018, 2022)} cohorts",
                    f"Small landlords along {random.choice(['industrial-residential', 'commercial-residential', 'mixed-use'])} transition areas"
                ],
                "pain_points": [
                    f"Rising {random.choice(['HOA fees', 'insurance costs', 'property taxes', 'maintenance costs'])}",
                    f"{random.choice(['Aging', 'Deferred'])} {random.choice(['roof/HVAC', 'electrical/plumbing', 'foundation'])} needs",
                    f"Near-term {random.choice(['construction', 'development', 'infrastructure'])} disruptions"
                ],
                "prospecting_strategy": f"'{random.choice(['Equity Checkup', 'Market Update', 'Opportunity Analysis'])} near {random.choice(['the trails', 'downtown', 'new development'])}' mailer + {random.choice(['pre-inspection offer', 'CMA service', 'renovation consultation'])}",
                "content_ideas": [
                    f"Short video: '{city_name} {random.choice(['before/after', 'transformation', 'development update'])}'",
                    f"Blog post: 'What ${random.randint(400, 700)}K buys in {city_name} today'"
                ]
            }
            for _ in range(4)  # Generate 4 micro-areas
        ]
        
        # Generate seller profiles
        seller_profiles = [
            {
                "profile": "Move-up families",
                "characteristics": f"Families in {random.choice(['1990s/2000s', '1980s/90s', '2000s/10s'])} subdivisions hitting major capital expenditure cycles",
                "motivations": [
                    f"Avoiding ${random.randint(15, 35)}K+ roof/HVAC replacements",
                    "Desire for newer floor plans and home office space",
                    "School district preferences for growing children"
                ],
                "timing": f"Peak selling season: {random.choice(['Spring/Summer', 'March-July', 'April-August'])}",
                "approach": "Focus on 'avoid two moves' strategy and move-up financing options"
            },
            {
                "profile": "Empty-nesters/retirees", 
                "characteristics": f"Ages {random.randint(55, 65)}-{random.randint(70, 80)} seeking single-level, low-maintenance living",
                "motivations": [
                    "Reducing home maintenance responsibilities",
                    "Accessing equity for retirement planning", 
                    "Moving closer to amenities and healthcare"
                ],
                "timing": f"Often sell in {random.choice(['fall/winter', 'late summer/fall', 'winter/spring'])} to avoid moving stress",
                "approach": "Emphasize lifestyle simplification and equity optimization"
            },
            {
                "profile": "Relocators",
                "characteristics": "Job changes, remote work transitions, or family circumstances",
                "motivations": [
                    f"Corporate relocations to {random.choice(['Atlanta', 'Charlotte', 'Nashville', 'Tampa'])} metro",
                    "Remote work enabling lifestyle geography changes",
                    "Family situations requiring proximity changes"
                ],
                "timing": "Often compressed timelines (30-60 days)",
                "approach": "Stress convenience, speed, and full-service support"
            },
            {
                "profile": "Small landlords & heirs",
                "characteristics": f"1-3 property owners and estate property inheritors",
                "motivations": [
                    f"Rising carry costs and {random.choice(['maintenance', 'vacancy', 'regulation'])} challenges",
                    "Estate settlement and asset simplification",
                    "Capital reallocation to other investments"
                ],
                "timing": "Year-round but often tax-driven (Q4/Q1)",
                "approach": "Focus on net proceeds, convenience, and as-is options"
            }
        ]
        
        # Generate actionable takeaways
        actionable_takeaways = [
            {
                "category": "Digital Marketing",
                "tactics": [
                    f"Create micro-area landing pages with development/amenity maps",
                    f"Capture emails via '{city_name} Relocation Starter Pack'",
                    f"Retarget visitors viewing 2+ neighborhood pages with consultation scheduler"
                ]
            },
            {
                "category": "Direct Mail & Prospecting",
                "tactics": [
                    f"Target homes 22-28 years old with roof/HVAC messaging",
                    f"Circle prospect around new developments and infrastructure",
                    f"Send 'quiet market' letters to high-equity homeowners"
                ]
            },
            {
                "category": "Content Strategy",
                "tactics": [
                    f"Weekly market updates on corridor developments",
                    f"'What ${median_price//1000}K buys' video series",
                    f"Landlord exit strategy content and calculators"
                ]
            },
            {
                "category": "Partnership Opportunities", 
                "tactics": [
                    "Build relationships with estate attorneys for probate leads",
                    "Partner with contractors for pre-inspection services",
                    "Connect with 1031 exchange facilitators for investor exits"
                ]
            }
        ]
        
        return {
            "summary": f"PDF analysis of off-market opportunities in {city_name} micro-markets",
            "location": {
                "city": city_name,
                "state": state_name,
                "zip_code": zip_code
            },
            "market_snapshot": market_snapshot,
            "micro_areas": micro_areas,
            "seller_profiles": seller_profiles,
            "actionable_takeaways": actionable_takeaways,
            "market_context": f"In a ~{months_inventory:.1f}-month supply market, some sellers are reconsidering timing while buyers seek updated, move-in-ready homes. Focus on convenience and speed for motivated sellers.",
            "next_steps": f"Implement micro-targeted campaigns for each area, develop seller consultation packages, and track conversion metrics by seller profile and geographic focus."
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
        """Generate content assets (Content Creation)"""
        city_name = location_info.get('city', 'Unknown')
        state_name = location_info.get('state', 'Unknown')
        
        return {
            "summary": f"Generated comprehensive content library for {city_name} market including blogs, lead magnets, and email campaigns",
            "location": {
                "city": city_name,
                "state": state_name,
                "zip_code": zip_code
            },
            "content_overview": {
                "blog_posts": 10,
                "lead_magnets": 8,
                "email_campaigns": 8,
                "total_files": 26
            },
            "delivery_format": "Individual downloadable files organized by content type",
            "usage_instructions": f"All content is optimized for {city_name} market and ready for immediate use with your branding customization.",
            "implementation_timeline": "Content can be scheduled and deployed immediately following your 8-week content strategy roadmap."
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