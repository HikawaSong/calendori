import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.models import Artist, Event, User
import os
from app.database import get_db

user = os.getenv("DB_USER", "root")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST", "127.0.0.1")
port = os.getenv("DB_PORT", "3306")
db_name = os.getenv("DB_NAME", "calendori")
test_db_name = os.getenv("TEST_DB_NAME", "calendori_test")

TEST_DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{test_db_name}"
TEST_DB_URL = os.getenv("DATABASE_URL", TEST_DATABASE_URL)
test_engine = create_engine(TEST_DB_URL, echo=True, connect_args={"charset": "utf8mb4"})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def create_test_data() -> list:
    test_artist_1 = Artist(
        name="Poppin'Party", description="A popular band in BanG Dream!"
    )
    test_artist_2 = Artist(
        name="Roselia", description="Another popular band in BanG Dream!"
    )

    test_Event_1 = Event(
        title="Poppin'Party 5th Live -Smile-",
        dates=["2026-04-10", "2026-04-11"],
        event_start_date="2026-04-10",
        place="Saitama Super Arena",
        category="Live",
        thumbnail_url="https://example.com/thumbnail2.jpg",
        event_url="https://example.com/event2",
        artists=[test_artist_1],
    )
    test_Event_2 = Event(
        title="Roselia 1st Live -Rausch-",
        dates=["2026-03-20", "2026-03-21"],
        event_start_date="2026-03-20",
        place="Tokyo Dome",
        category="Live",
        thumbnail_url="https://example.com/thumbnail.jpg",
        event_url="https://example.com/event",
        artists=[test_artist_2],
    )

    test_user_1 = User(
        openid="kasumi",
        platform="wechat",
        nickname="Test User 1",
        avatar_url="https://example.com/avatar.jpg",
    )

    return [test_Event_1, test_Event_2, test_user_1]


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """
    清空并重新建表，注入元数据
    """

    with test_engine.connect() as conn:
        # 1. 强制连接层使用 utf8mb4
        conn.execute(text("SET NAMES utf8mb4;"))
        conn.execute(
            text(
                "ALTER DATABASE calendori_test CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;"
            )
        )
        conn.commit()

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    # 注入基础元数据
    session = TestSessionLocal(bind=test_engine)
    try:
        data = create_test_data()
        session.add_all(data)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    yield test_engine


@pytest.fixture(scope="function")
def db_session(setup_db):
    """
    每个测试函数使用独立的数据库事务，测试结束后回滚，保持数据库状态一致
    """
    connection = setup_db.connect()
    # 开启事务
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    提供测试客户端：它负责发起 HTTP 请求
    """

    def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    # 创建客户端
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
