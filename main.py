from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from clients.slack_client import send_slack_webhook
from router.ad_info import router as ad_info_router
from contextlib import asynccontextmanager
from datetime import datetime
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_periodic_slack_message():
    """Send periodic Slack messages"""
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"Hi, I am Beta Than You Assistant! Datetime: {current_time}"
        await send_slack_webhook(message)
        logger.info(f"Periodic Slack message sent at {current_time}")
    except Exception as e:
        logger.error(f"Failed to send periodic Slack message: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Initialize scheduler
    scheduler = AsyncIOScheduler()
    
    # Startup
    logger.info("FastAPI application is starting up...")
    
    # Schedule periodic Slack messages every 10 minutes using cron
    scheduler.add_job(
        send_periodic_slack_message,
        CronTrigger(minute="*/2"),  # Every 2 minutes
        id="periodic_slack_message",
        name="Send periodic Slack message",
        replace_existing=True,
        max_instances=1
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Cron scheduler started - messages will be sent every 2 minutes")

    yield
    
    # Shutdown
    logger.info("FastAPI application is shutting down...")
    
    # Shutdown the scheduler
    scheduler.shutdown(wait=True)
    logger.info("Cron scheduler stopped")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Hello from agent-test!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Include the ad_info router
app.include_router(ad_info_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
