from datetime import datetime
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User


def find_user_by_openid(db: Session, openid: str, platform: str):
    return (
        db.query(User).filter(User.openid == openid, User.platform == platform).first()
    )


def create_user(db: Session, openid: str, platform: str):
    user = User(openid=openid, platform=platform, last_login=datetime.now())
    db.add(user)
    db.flush()
    return user
