from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from pydantic import BaseModel
from app.services.user_service import user_login
from app.utils.auth import create_access_token
from app.routers.base import ResponseModel
import os


router = APIRouter(prefix="/api/v1/users", tags=["users"])

WX_APPID = os.getenv("WX_APPID")
WX_SECRET = os.getenv("WX_SECRET")
WX_URL = "https://api.weixin.qq.com/sns/jscode2session"
QQ_APPID = os.getenv("QQ_APPID")
QQ_SECRET = os.getenv("QQ_SECRET")
QQ_URL = "https://api.q.qq.com/sns/jscode2session"


class LoginRequest(BaseModel):
    code: str
    platform: str = "qq"


@router.post("/login", response_model=ResponseModel[dict])
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    if request.platform not in ["wx", "qq"]:
        raise HTTPException(status_code=400, detail="平台参数错误")

    user = await user_login(db, request.code, request.platform)

    token = create_access_token(data={"sub": str(user.id)})
    return ResponseModel.success_response(data={"token": token, "user_id": user.id})
