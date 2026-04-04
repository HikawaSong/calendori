from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["System"])
async def root():
    """
    系统根路径
    """
    return {
        "status": "online",
        "project": "Calendori",
        "version": "0.1.0",
        "message": "Welcome to the Bandori Live Calendar API",
    }
