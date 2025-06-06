from fastapi import HTTPException, APIRouter, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from database.ads_register import AdsRegisterDatabase
from clients.slack_client import send_slack_webhook

# Pydantic models for request/response validation
class AdRegistration(BaseModel):
    """Model for ad registration data."""
    ad_id: int = Field(..., description="The ad ID to register")
    title: str = Field(..., min_length=1, description="The title of the ad")


class UserRegistrationRequest(BaseModel):
    """Model for creating/updating user ad registrations."""
    user_id: int = Field(..., gt=0, description="User ID must be positive")
    user_name: Optional[str] = Field(None, description="User name for reference")
    ads: List[AdRegistration] = Field(..., min_items=1, description="List of ads to register")


class UserRegistrationResponse(BaseModel):
    """Model for user registration response."""
    user_id: int
    list_ad_ids: List[int]
    list_titles: List[str]
    total_ads: int


class SingleAdRequest(BaseModel):
    """Model for adding/removing a single ad."""
    user_id: int = Field(..., gt=0, description="User ID must be positive")
    ad_id: int = Field(..., description="The ad ID")
    title: Optional[str] = Field(None, description="The title of the ad (required for adding)")


class ApiResponse(BaseModel):
    """Standard API response model."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


# Initialize router
router = APIRouter(prefix="/ads-register", tags=["Ads Registration"])


@router.post("/register", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def register_user_ads(request: UserRegistrationRequest):
    """
    Register a list of ads for a user.
    
    Args:
        request: User registration request containing user_id and list of ads
        
    Returns:
        API response with registration details
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        ads_register_db = AdsRegisterDatabase()
        
        # Extract ad_ids and titles from the request
        ad_ids = [ad.ad_id for ad in request.ads]
        titles = [ad.title for ad in request.ads]
        
        # Create user registration
        success = ads_register_db.create_user_registration(
            user_id=request.user_id,
            ad_ids=ad_ids,
            titles=titles
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register user ads"
            )
        
        await send_slack_webhook(
            message=f"Chị Tốt AI đã tự động chăm sóc các tin đăng của {request.user_name} rồi. Chờ xem kết quả trong vài ngày tới nhé.",
        )
        # Return success response with registration data
        return ApiResponse(
            success=True,
            message=f"Successfully registered {len(ad_ids)} ads for user {request.user_id}",
            data={
                "user_id": request.user_id,
                "registered_ads": len(ad_ids),
                "ad_ids": ad_ids,
                "titles": titles
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=UserRegistrationResponse)
async def get_user_registration(user_id: int):
    """
    Get user ad registration by user ID.
    
    Args:
        user_id: The user ID to retrieve registration for
        
    Returns:
        User registration data
        
    Raises:
        HTTPException: If user not found
    """
    try:
        ads_register_db = AdsRegisterDatabase()
        registration = ads_register_db.read_user_registration(user_id)
        
        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No registration found for user {user_id}"
            )
        
        return UserRegistrationResponse(
            user_id=registration['user_id'],
            list_ad_ids=registration['list_ad_ids'],
            list_titles=registration['list_titles'],
            total_ads=len(registration['list_ad_ids'])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving registration: {str(e)}"
        )


@router.put("/update", response_model=ApiResponse)
async def update_user_registration(request: UserRegistrationRequest):
    """
    Update an existing user ad registration.
    
    Args:
        request: User registration request with updated ads list
        
    Returns:
        API response with update status
        
    Raises:
        HTTPException: If update fails or user not found
    """
    try:
        ads_register_db = AdsRegisterDatabase()
        
        # Check if user exists
        existing_registration = ads_register_db.read_user_registration(request.user_id)
        if not existing_registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No registration found for user {request.user_id}"
            )
        
        # Extract ad_ids and titles from the request
        ad_ids = [ad.ad_id for ad in request.ads]
        titles = [ad.title for ad in request.ads]
        
        # Update user registration
        rows_affected = ads_register_db.update_user_registration(
            user_id=request.user_id,
            ad_ids=ad_ids,
            titles=titles
        )
        await send_slack_webhook(
            message=f"User {request.user_id} updated registration for {len(ad_ids)} ads for Smart Assistant feature: {', '.join(titles)}",
        )
        if rows_affected == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user registration"
            )
        
        return ApiResponse(
            success=True,
            message=f"Successfully updated registration for user {request.user_id}",
            data={
                "user_id": request.user_id,
                "updated_ads": len(ad_ids),
                "ad_ids": ad_ids,
                "titles": titles
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during update: {str(e)}"
        )


@router.post("/add-ad", response_model=ApiResponse)
async def add_ad_to_user(request: SingleAdRequest):
    """
    Add a single ad to an existing user registration.
    
    Args:
        request: Single ad request containing user_id, ad_id, and title
        
    Returns:
        API response with operation status
        
    Raises:
        HTTPException: If operation fails or validation errors
    """
    try:
        if not request.title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required when adding an ad"
            )
        
        ads_register_db = AdsRegisterDatabase()
        
        success = ads_register_db.add_ad_to_user(
            user_id=request.user_id,
            ad_id=request.ad_id,
            title=request.title
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add ad to user registration"
            )
        
        await send_slack_webhook(
            message=f"User {request.user_id} added ad {request.ad_id} to Smart Assistant feature: {request.title}",
        )

        return ApiResponse(
            success=True,
            message=f"Successfully added ad {request.ad_id} to user {request.user_id}",
            data={
                "user_id": request.user_id,
                "ad_id": request.ad_id,
                "title": request.title
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while adding ad: {str(e)}"
        )


@router.delete("/remove-ad", response_model=ApiResponse)
async def remove_ad_from_user(request: SingleAdRequest):
    """
    Remove a single ad from a user registration.
    
    Args:
        request: Single ad request containing user_id and ad_id
        
    Returns:
        API response with operation status
        
    Raises:
        HTTPException: If operation fails or ad not found
    """
    try:
        ads_register_db = AdsRegisterDatabase()
        
        success = ads_register_db.remove_ad_from_user(
            user_id=request.user_id,
            ad_id=request.ad_id
        )
        await send_slack_webhook(
            message=f"User {request.user_id} removed ad {request.ad_id} from Smart Assistant feature",
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ad {request.ad_id} not found in user {request.user_id} registration"
            )
        
        return ApiResponse(
            success=True,
            message=f"Successfully removed ad {request.ad_id} from user {request.user_id}",
            data={
                "user_id": request.user_id,
                "ad_id": request.ad_id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while removing ad: {str(e)}"
        )


@router.delete("/user/{user_id}", response_model=ApiResponse)
async def delete_user_registration(user_id: int):
    """
    Delete a complete user registration.
    
    Args:
        user_id: The user ID whose registration should be deleted
        
    Returns:
        API response with deletion status
        
    Raises:
        HTTPException: If deletion fails or user not found
    """
    try:
        ads_register_db = AdsRegisterDatabase()
        
        rows_affected = ads_register_db.delete_user_registration(user_id)
        
        if rows_affected == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No registration found for user {user_id}"
            )
        await send_slack_webhook(
            message=f"User {user_id} registration has been deleted from Smart Assistant feature",
        )
        return ApiResponse(
            success=True,
            message=f"Successfully deleted registration for user {user_id}",
            data={"user_id": user_id, "deleted": True}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting registration: {str(e)}"
        )


@router.get("/all", response_model=List[UserRegistrationResponse])
async def get_all_registrations():
    """
    Get all user registrations.
    
    Returns:
        List of all user registrations
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        ads_register_db = AdsRegisterDatabase()
        registrations = ads_register_db.get_all_registrations()
        
        return [
            UserRegistrationResponse(
                user_id=reg['user_id'],
                list_ad_ids=reg['list_ad_ids'],
                list_titles=reg['list_titles'],
                total_ads=len(reg['list_ad_ids'])
            )
            for reg in registrations
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving registrations: {str(e)}"
        )


@router.get("/ad/{ad_id}/users", response_model=List[int])
async def get_users_by_ad_id(ad_id: int):
    """
    Get all user IDs that have registered for a specific ad.
    
    Args:
        ad_id: The ad ID to search for
        
    Returns:
        List of user IDs that have registered for the specified ad
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        ads_register_db = AdsRegisterDatabase()
        user_ids = ads_register_db.get_users_by_ad_id(ad_id)
        
        return user_ids
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving users for ad {ad_id}: {str(e)}"
        )


@router.delete("/flush", response_model=ApiResponse)
async def flush_all_registrations():
    """
    Remove all data from the ads_register table.
    ⚠️ WARNING: This will delete all registration data permanently!
    
    Returns:
        API response confirming the flush operation
        
    Raises:
        HTTPException: If flush operation fails
    """
    try:
        ads_register_db = AdsRegisterDatabase()
        ads_register_db.flush()
        
        return ApiResponse(
            success=True,
            message="All registration data has been permanently deleted",
            data={"flushed": True}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while flushing data: {str(e)}"
        )


# Bump-related endpoints

@router.get("/unbumped-ads", response_model=ApiResponse)
async def get_unbumped_ads():
    """
    Get all ads that haven't been bumped yet.
    
    Returns:
        List of unbumped ads with user_id, ad_id, and title
    """
    try:
        ads_register_db = AdsRegisterDatabase()
        unbumped_ads = ads_register_db.get_unbumped_ads()
        
        return ApiResponse(
            success=True,
            message=f"Found {len(unbumped_ads)} unbumped ads",
            data={
                "unbumped_ads": unbumped_ads,
                "count": len(unbumped_ads)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching unbumped ads: {str(e)}"
        )


@router.post("/bump-ad", response_model=ApiResponse)
async def manual_bump_ad(user_id: int, ad_id: int):
    """
    Manually mark a specific ad as bumped.
    
    Args:
        user_id: The user ID
        ad_id: The ad ID to mark as bumped
        
    Returns:
        API response confirming the bump operation
    """
    try:
        ads_register_db = AdsRegisterDatabase()
        
        # Check if user registration exists
        user_data = ads_register_db.read_user_registration(user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        # Check if ad exists for this user
        if ad_id not in user_data['list_ad_ids']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ad {ad_id} is not registered for user {user_id}"
            )
        
        # Mark as bumped
        success = ads_register_db.mark_ad_as_bumped(user_id, ad_id)
        
        if success:
            return ApiResponse(
                success=True,
                message=f"Ad {ad_id} successfully marked as bumped for user {user_id}",
                data={"user_id": user_id, "ad_id": ad_id, "bumped": True}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to mark ad as bumped"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while bumping ad: {str(e)}"
        )


@router.post("/reset-bumped", response_model=ApiResponse)
async def reset_all_bumped_ads():
    """
    Reset all bumped ad statuses (start a new bump cycle).
    This will clear all bumped_ad_ids so all ads can be bumped again.
    
    Returns:
        API response confirming the reset operation
    """
    try:
        ads_register_db = AdsRegisterDatabase()
        success = ads_register_db.reset_bumped_ads()
        
        if success:
            return ApiResponse(
                success=True,
                message="All bumped ad statuses have been reset. New bump cycle started.",
                data={"reset": True}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset bumped ad statuses"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while resetting bumped ads: {str(e)}"
        )


@router.get("/bump-status", response_model=ApiResponse)
async def get_bump_status():
    """
    Get the current bump status including total ads, bumped ads, and progress.
    
    Returns:
        Current bump cycle status and statistics
    """
    try:
        ads_register_db = AdsRegisterDatabase()
        
        all_registrations = ads_register_db.get_all_registrations()
        unbumped_ads = ads_register_db.get_unbumped_ads()
        total_bumped = ads_register_db.get_bumped_ads_count()
        
        # Calculate total ads across all users
        total_ads = sum(len(reg['list_ad_ids']) for reg in all_registrations)
        
        return ApiResponse(
            success=True,
            message="Bump status retrieved successfully",
            data={
                "total_ads": total_ads,
                "bumped_ads": total_bumped,
                "unbumped_ads": len(unbumped_ads),
                "progress_percentage": round((total_bumped / total_ads * 100) if total_ads > 0 else 0, 2),
                "users_count": len(all_registrations),
                "cycle_complete": len(unbumped_ads) == 0
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while getting bump status: {str(e)}"
        )


@router.post("/trigger-bump", response_model=ApiResponse)
async def trigger_manual_bump():
    """
    Manually trigger the ad bump process (same as scheduler).
    This will randomly select up to 2 unbumped ads and send bump messages.
    
    Returns:
        API response with details of the bumped ads
    """
    try:
        ads_register_db = AdsRegisterDatabase()
        
        # Get unbumped ads
        unbumped_ads = ads_register_db.get_unbumped_ads()
        
        if len(unbumped_ads) == 0:
            ads_register_db.reset_bumped_ads()
            unbumped_ads = ads_register_db.get_unbumped_ads()
        
        if len(unbumped_ads) == 0:
            return ApiResponse(
                success=True,
                message="No ads available for bumping",
                data={"bumped_ads": [], "count": 0}
            )
        
        # Randomly select up to 2 ads
        import random
        from datetime import datetime, timezone, timedelta
        
        selected_count = min(2, len(unbumped_ads))
        selected_ads = random.sample(unbumped_ads, selected_count)
        
        current_time = datetime.now(timezone(timedelta(hours=7))).strftime('%d-%m-%Y %H:%M')
        bumped_ads = []
        
        for ad in selected_ads:
            # Create bump message
            message = f"🔥 Ad BUMPED! Tin đăng '{ad['title']}' (ID: {ad['ad_id']}) đã được bump lúc {current_time}. Check hiệu quả <http://localhost:8080|tại đây>!"
            
            # Send Slack message
            await send_slack_webhook(message)
            
            # Mark ad as bumped
            ads_register_db.mark_ad_as_bumped(ad['user_id'], ad['ad_id'])
            
            bumped_ads.append({
                "user_id": ad['user_id'],
                "ad_id": ad['ad_id'],
                "title": ad['title'],
                "bumped_at": current_time
            })
        
        return ApiResponse(
            success=True,
            message=f"Successfully bumped {selected_count} ads and sent Slack notifications",
            data={
                "bumped_ads": bumped_ads,
                "count": selected_count,
                "timestamp": current_time
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while triggering manual bump: {str(e)}"
        )
