from fastapi.testclient import TestClient

from app.core.security import get_current_user
from app.main import app
from app.models import User


def test_current_user_requires_authentication() -> None:
    response = TestClient(app).get("/api/v1/auth/me")

    assert response.status_code == 401


def test_current_user_returns_complete_user_read_contract() -> None:
    current_user = User(
        id=17,
        username="operator",
        full_name="Olena Koval",
        password_hash="unused",
        role="OPERATOR",
        department=None,
        is_active=True,
    )
    app.dependency_overrides[get_current_user] = lambda: current_user
    try:
        response = TestClient(app).get("/api/v1/auth/me")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    assert response.json() == {
        "id": 17,
        "username": "operator",
        "full_name": "Olena Koval",
        "role": "OPERATOR",
        "department": None,
        "is_active": True,
    }
