from fastapi import APIRouter, HTTPException

from app.models import ReviewRequest


router = APIRouter()


@router.post("/review")
async def review_code(request: ReviewRequest):
    pass
