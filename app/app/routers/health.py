from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """ตรวจสอบว่า backend service พร้อมรับ request"""

    return {"status": "ok"}
