# routers/analytics.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/linkedin/analytics")
def get_mock_analytics():
    return {
        "post_id": "123456",
        "likes": 87,
        "comments": 14,
        "shares": 9,
        "impressions": 1200,
        "engagement_rate": "9.25%"
    }
