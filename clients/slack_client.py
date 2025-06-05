import os
import aiohttp
import asyncio
import json
from typing import Union, Dict, Any


SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL", "")

async def send_slack_webhook(message: Union[str, Dict[str, Any]]) -> bool:
    """
    Send a message to Slack using webhook URL.
    
    Args:
        message: Either a string message or a dictionary with Slack message format
        
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    webhook_url = SLACK_WEBHOOK
    
    if not webhook_url:
        print("Warning: SLACK_WEBHOOK_URL environment variable is not set")
        return False
    
    # Handle both string and dict message formats
    if isinstance(message, str):
        payload = {"text": message}
    else:
        payload = message
    
    max_retries = 3
    timeout = aiohttp.ClientTimeout(total=10)
    
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    webhook_url,
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps(payload)
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        print(f"Slack webhook failed with status: {response.status}")
                        
        except aiohttp.ClientError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                return False
            await asyncio.sleep(1)  # Wait 1 second before retry
        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                return False
            await asyncio.sleep(1)
    
    return False

# Example usage
import asyncio
asyncio.run(send_slack_webhook("Hello, this is from hackathon team Beta Than You!"))