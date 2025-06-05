from fastapi import HTTPException, APIRouter
from database.ad_info import AdInfoDatabase
from database.ad_performance import AdPerformanceDatabase
from database.orders import OrdersDatabase
from database.ad_quality import AdQualityDatabase
from llm.factory import get_llm_model

import json
import asyncio
router = APIRouter(tags=["ads"])
ad_summary_model = get_llm_model("ad_performance_summary")

@router.get("/summary_ad/{user_id}")
async def get_ads(user_id: int):
    """
    Get ad information by user ID.
    """
    ad_info_db = AdInfoDatabase()
    ad_performance_db = AdPerformanceDatabase()
    order_db = OrdersDatabase()
    ad_quality_db = AdQualityDatabase()

    print(f"Retrieved ad info for user_id {user_id}")
    ad_info = ad_info_db.read_ads_by_user_id(user_id)
    ads = []
    for ad in ad_info:
        ad_performance = ad_performance_db.read_performance_by_ad_id(ad["ad_id"])
        ad_quality = ad_quality_db.get_ad_quality_score(ad["ad_id"])
        qualified_criteria = 0
        for quality_criteria_name, quality_criteria_value in ad_quality.items():
            if quality_criteria_value:
                qualified_criteria += 1

        order_info = order_db.read_orders_by_ad_id(ad["ad_id"])
        total_clicks = sum([perf["adview_count"] for perf in ad_performance]) 
        total_spend = sum([order["price"] for order in order_info]) if order_info else 0
        summary_ad = {
            "id": ad["ad_id"],
            "title": ad["subject"],
            "body": ad["body"],
            "category": ad.get("category", "PTY"),  # Assuming category is optional
            "price": ad["unit_price"],
            "location": ad.get("city", "Unknown"),  # Assuming city is optional
            "postedDate": ad.get("first_approved_time", "Unknown"),  # Assuming start_date is optional
            "image": ad.get("image_link", "/default-image.png"),  # Assuming image_url is optional
            "clicks": total_clicks,  # Assuming clicks is optional
            "spend": total_spend,  # Assuming spend is optional
            "qualifiedCriteria": qualified_criteria,  # Assuming qualified_criteria is optional
            "totalCriteria": 6,  # Assuming total_criteria is optional
            "criteriaDetails": {
                "A": ad_quality.get("unit_price", False),  # Assuming title relevance is optional
                "B": ad_quality.get("image_count", False),  # Assuming image quality is optional
                "C": ad_quality.get("video_count", False),  # Assuming brand information is optional
                "D": ad_quality.get("have_width_length", False),  # Assuming product description is optional
                "E": ad_quality.get("is_consistency", False),
                "F": ad_quality.get("have_living_size", False)  # Assuming category classification is optional
            }, 
            "status": ad.get("status", "Active"),  # Assuming status is optional
            "performanceData": ad_performance  # Placeholder for performance data
        }
        ads.append(summary_ad)
    recommendation_tasks = [ad_summary_model.generate_content(json.dumps(ad)) for ad in ads]
    recommendations = await asyncio.gather(*recommendation_tasks)

    for recommendation, ad in zip(recommendations, ads):
        summarized_ad = json.loads(recommendation)
        ad["insights"] = summarized_ad.get("performance_insight", "")
        ad["recommendations"] = summarized_ad.get("suggestions", [])
    if not ads:
        raise HTTPException(status_code=404, detail="No ads found for this user ID")
    return {
        "ads": ads
    }