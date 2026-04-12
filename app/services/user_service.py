import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.daos.user_dao import find_user_by_openid, create_user
from app.models import User
from datetime import datetime

import os


WX_APPID = os.getenv("WX_APPID")
WX_SECRET = os.getenv("WX_SECRET")
WX_URL = "https://api.weixin.qq.com/sns/jscode2session"
QQ_APPID = os.getenv("QQ_APPID")
QQ_SECRET = os.getenv("QQ_SECRET")
QQ_URL = "https://api.q.qq.com/sns/jscode2session"


async def get_user_openid(code: str, platform: str) -> str:
    if platform == "qq":
        auth_url = QQ_URL
        appid = QQ_APPID
        secret = QQ_SECRET
    else:
        auth_url = WX_URL
        appid = WX_APPID
        secret = WX_SECRET

    params = {
        "appid": appid,
        "secret": secret,
        "js_code": code,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(auth_url, params=params)
        data = response.json()

    if "openid" not in data:
        raise HTTPException(
            status_code=400, detail=f"{platform.upper()}登录失败: {data.get('errmsg')}"
        )
    return data["openid"]


async def user_login(db: Session, code: str, platform: str) -> User:

    openid = await get_user_openid(code, platform)

    # 查找或创建用户
    user = find_user_by_openid(db, openid, platform)
    if not user:
        user = create_user(db, openid, platform)
    else:
        user.last_login = datetime.now()

    db.commit()
    db.refresh(user)
    return user
