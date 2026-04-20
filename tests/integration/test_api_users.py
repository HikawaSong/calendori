from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.models import User
import uuid

client = TestClient(app)
EXISTING_OPENID = "kasumi"
EXISTING_PLATFORM = "wx"


@patch("app.services.user_service.get_user_openid", new_callable=AsyncMock)
def test_login_existing_user(mock_get_openid, client):
    """
    测试：老用户登录（数据库里已存在）
    """
    mock_get_openid.return_value = EXISTING_OPENID

    response = client.post(
        "/api/v1/users/login", json={"code": "any_code", "platform": EXISTING_PLATFORM}
    )

    assert response.status_code == 200


@patch("app.services.user_service.get_user_openid", new_callable=AsyncMock)
def test_login_new_user(mock_get_openid, client):
    """
    测试：新用户登录（数据库里不存在）
    """
    new_openid = str(f"new_{uuid.uuid4()}")
    mock_get_openid.return_value = new_openid

    response = client.post(
        "/api/v1/users/login", json={"code": "new_code", "platform": "qq"}
    )

    assert response.status_code == 200
