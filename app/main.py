import pymysql

pymysql.install_as_MySQLdb()

from app.database import engine, Base

from app import models

pymysql.install_as_MySQLdb()


def init_db():
    print("🚀 开始连接数据库并同步表结构...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ 表结构初始化成功！")
        print("📊 当前已创建/验证的表: ", Base.metadata.tables.keys())
    except Exception as e:
        print(f"❌ 初始化失败，请检查数据库连接或权限。")
        print(f"错误详情: {e}")


if __name__ == "__main__":
    init_db()
