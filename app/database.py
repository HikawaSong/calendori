import pymysql
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

pymysql.install_as_MySQLdb()

user = os.getenv("DB_USER", "root")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST", "127.0.0.1")
port = os.getenv("DB_PORT", "3306")
db_name = os.getenv("DB_NAME", "calendori")

# 1. 定义连接字符串
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"

# 2. 创建引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# 3. 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 定义基类 (供 models.py 继承)
Base = declarative_base()


# 5. 依赖注入函数 (供 routers 里的 API 调用)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    print("🚀 开始连接数据库并同步表结构...")
    from . import models

    try:
        Base.metadata.create_all(bind=engine)
        print("✅ 表结构初始化成功！")
        print("📊 当前已创建/验证的表: ", Base.metadata.tables.keys())
    except Exception as e:
        print(f"❌ 初始化失败，请检查数据库连接或权限。")
        print(f"错误详情: {e}")
