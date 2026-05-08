from fastapi import Request
import jwt
import os
from app.database import get_db

SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


def get_current_user_optional(request: Request) -> str | None:
    """
    非强制的鉴权依赖：解析 Token 并返回 user_id，如果没有 Token 则返回 None
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None  # 游客访问

    token = auth_header.split(" ")[1]
    try:
        # 解密 Token，拿到里面隐藏的数据（Payload）
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")  # 行业惯例，sub 字段存放 user_id
        if user_id is None:
            return None
        return user_id
    except jwt.PyJWTError:
        # 如果 Token 伪造或过期，你可以选择静默按游客处理，或者抛错
        return None
