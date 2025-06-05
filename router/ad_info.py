from fastapi import HTTPException, APIRouter
from database.ad_info import AdInfoDatabase
from database.ad_performance import AdPerformanceDatabase
from database.orders import OrdersDatabase
from llm.factory import get_llm_model

import json
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

    print(f"Retrieved ad info for user_id {user_id}")
    ad_info = ad_info_db.read_ads_by_user_id(user_id)
    ads = []
    for ad in ad_info:
        ad_performance = ad_performance_db.read_performance_by_ad_id(ad["ad_id"])
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
            "qualifiedCriteria": ad.get("qualified_criteria", 0),  # Assuming qualified_criteria is optional
            "totalCriteria": ad.get("total_criteria", 5),  # Assuming total_criteria is optional
            "criteriaDetails": {
                "A": ad.get("title_relevance", False),  # Assuming title relevance is optional
                "B": ad.get("image_quality", False),  # Assuming image quality is optional
                "C": ad.get("brand_information", False),  # Assuming brand information is optional
                "D": ad.get("product_description", False),  # Assuming product description is optional
                "E": ad.get("category_classification", False)  # Assuming category classification is optional
            }, 
            "status": ad.get("status", "Active"),  # Assuming status is optional
            "performanceData": ad_performance  # Placeholder for performance data
        }
        summarized_ad = await ad_summary_model.generate_content(json.dumps(summary_ad))
        summarized_ad = json.loads(summarized_ad)
        summary_ad["insights"] = summarized_ad.get("performance_insight", "")
        summary_ad["recommendations"] = summarized_ad.get("suggestions", [])
        
        ads.append(summary_ad)

    if not ads:
        raise HTTPException(status_code=404, detail="No ads found for this user ID")
    return {
        "ads": ads
    }