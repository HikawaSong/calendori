from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel
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


T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    success: bool = True
    message: str = "success"
    data: Optional[T] = None
    code: int = 200

    @classmethod
    def success_response(cls, data: T, message: str = "success"):
        return cls(success=True, message=message, data=data)
