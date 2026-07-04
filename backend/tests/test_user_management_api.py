from fastapi.testclient import TestClient

from app.core.security import get_current_user
from app.main import app
from app.models import User


def override_current_user() -> User:
    return User(
        id=1,
        username="admin",
        full_name="Test Admin",
        password_hash="not-used",
        role="test",
        is_active=True,
    )


def test_user_management_api_routes_are_registered() -> None:
    route_paths = {route.path for route in app.routes}

    assert "/api/v1/user-management/health" in route_paths
    assert "/api/v1/user-management/users" in route_paths
    assert "/api/v1/user-management/users/{user_id}" in route_paths
    assert "/api/v1/user-management/profiles" in route_paths
    assert "/api/v1/user-management/profiles/{profile_id}" in route_paths
    assert "/api/v1/user-management/role-assignments" in route_paths
    assert "/api/v1/user-management/role-assignments/{assignment_id}" in route_paths
    assert "/api/v1/user-management/audit-events" in route_paths
    assert "/api/v1/user-management/audit-events/{event_id}" in route_paths


def test_user_management_health_endpoint_is_reachable() -> None:
    app.dependency_overrides[get_current_user] = override_current_user
    client = TestClient(app)

    try:
        response = client.get("/api/v1/user-management/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
