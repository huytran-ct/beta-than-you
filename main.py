from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from clients.slack_client import send_slack_webhook
from router.ad_info import router as ad_info_router
from router.ads_register import router as ads_register_router
from database.ads_register import AdsRegisterDatabase
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import timezone, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of 10 Vietnamese first names for Slack messages
vietnamese_names = {
    "Minh": "Anh",
    "Hương": "Chị", 
    "Nam": "Anh",
    "Lan": "Chị",
    "Đức": "Anh",
    "Mai": "Chị",
    "Bảo": "Anh",
    "Linh": "Chị",
    "Thành": "Anh",
    "Thu": "Chị"
}

async def send_periodic_slack_message():
    """Send periodic Slack messages"""
    try:
        current_time = datetime.now(timezone(timedelta(hours=7))).strftime('%d-%m-%Y')
        for name, title in vietnamese_names.items():
            message = f"{title} {name} ơi, xem tóm tắt hiệu quả tin đăng ngày {current_time} <http://localhost:8080|tại đây> nha"
            await send_slack_webhook(message)
            logger.info(f"Slack message sent to {name} at {current_time}")
    except Exception as e:
        logger.error(f"Failed to send periodic Slack message: {e}")

async def send_ad_bump_messages():
    """Send ad bump Slack messages for randomly selected ads"""
    try:
        # Initialize database
        db = AdsRegisterDatabase()
        
        # Get all unbumped ads
        unbumped_ads = db.get_unbumped_ads()
        
        if len(unbumped_ads) == 0:
            logger.info("No unbumped ads available. Resetting bumped status for new cycle.")
            db.reset_bumped_ads()
            unbumped_ads = db.get_unbumped_ads()
        
        if len(unbumped_ads) == 0:
            logger.info("No ads available for bumping")
            return
        
        # Randomly select up to 2 ads
        selected_count = min(2, len(unbumped_ads))
        selected_ads = random.sample(unbumped_ads, selected_count)
        
        current_time = datetime.now(timezone(timedelta(hours=7))).strftime('%d-%m-%Y %H:%M')
        
        for ad in selected_ads:
            # Create bump message
            message = f"🔥 Ad BUMPED! Tin đăng '{ad['title']}' (ID: {ad['ad_id']}) đã được bump lúc {current_time}. Check hiệu quả <http://localhost:8080|tại đây>!"
            
            # Send Slack message
            await send_slack_webhook(message)
            
            # Mark ad as bumped
            db.mark_ad_as_bumped(ad['user_id'], ad['ad_id'])
            
            logger.info(f"Ad bumped - User: {ad['user_id']}, Ad: {ad['ad_id']}, Title: {ad['title']}")
        
        total_bumped = db.get_bumped_ads_count()
        total_ads = len(db.get_unbumped_ads()) + total_bumped
        logger.info(f"Bump cycle complete. {selected_count} ads bumped. Progress: {total_bumped}/{total_ads} ads bumped")
        
    except Exception as e:
        logger.error(f"Failed to send ad bump messages: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Initialize scheduler
    scheduler = AsyncIOScheduler()
    
    # Startup
    logger.info("FastAPI application is starting up...")
    
    scheduler.add_job(
        send_periodic_slack_message,
        CronTrigger(hour=4, minute=0, timezone='Asia/Ho_Chi_Minh'),  # Daily at 4:00 AM UTC+7
        id="periodic_slack_message",
        name="Send periodic Slack message",
        replace_existing=True,
        max_instances=1
    )
    
    scheduler.add_job(
        send_ad_bump_messages,
        CronTrigger(minute="*/1"),  # Every 15 minutes
        id="ad_bump_messages",
        name="Send ad bump messages",
        replace_existing=True,
        max_instances=1
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Cron scheduler started:")
    logger.info("- Periodic messages: every 30 minutes")
    logger.info("- Ad bump messages: every 15 minutes")

    yield
    
    # Shutdown
    logger.info("FastAPI application is shutting down...")
    
    # Shutdown the scheduler
    scheduler.shutdown(wait=True)
    logger.info("Cron scheduler stopped")

app = FastAPI(lifespan=lifespan)

# Allow CORS from your frontend origin
origins = [
    "http://localhost:8080",  # or whatever your frontend address is
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Can use ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],  # Or specify: ["GET", "POST", "OPTIONS"]
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from agent-test!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Include the ad_info router
app.include_router(ad_info_router)

# Include the ads_register router
app.include_router(ads_register_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
