from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from clients.slack_client import send_slack_webhook
from router.ad_info import router as ad_info_router
from router.ads_register import router as ads_register_router
from contextlib import asynccontextmanager
from datetime import datetime
import logging
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Initialize scheduler
    scheduler = AsyncIOScheduler()
    
    # Startup
    logger.info("FastAPI application is starting up...")
    
    scheduler.add_job(
        send_periodic_slack_message,
        CronTrigger(minute="*/30"),  # Every 30 minutes
        id="periodic_slack_message",
        name="Send periodic Slack message",
        replace_existing=True,
        max_instances=1
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Cron scheduler started - messages will be sent every 30 minutes")

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
