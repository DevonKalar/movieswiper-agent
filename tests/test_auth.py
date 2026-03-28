import jwt
import pytest
from flask import g
from app.common.auth import require_auth, TokenPayload

SECRET = "test-secret"
ALGORITHM = "HS256"


def make_token(payload: dict) -> str:
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


@pytest.fixture
def auth_app(app):
    app.config["JWT_SECRET"] = SECRET

    @app.get("/protected")
    @require_auth
    def protected_route():
        return {"sub": g.user.sub, "email": g.user.email}

    return app


@pytest.fixture
def auth_client(auth_app):
    return auth_app.test_client()


class TestRequireAuth:
    def test_valid_token_sets_g_user(self, auth_client):
        token = make_token({"sub": "user-123", "email": "test@example.com"})
        response = auth_client.get("/protected", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["sub"] == "user-123"
        assert data["email"] == "test@example.com"

    def test_token_without_email(self, auth_client):
        token = make_token({"sub": "user-123"})
        response = auth_client.get("/protected", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.get_json()["email"] is None

    def test_missing_authorization_header_returns_401(self, auth_client):
        response = auth_client.get("/protected")
        assert response.status_code == 401

    def test_non_bearer_scheme_returns_401(self, auth_client):
        token = make_token({"sub": "user-123"})
        response = auth_client.get("/protected", headers={"Authorization": f"Basic {token}"})
        assert response.status_code == 401

    def test_expired_token_returns_401(self, auth_client):
        from datetime import datetime, timezone
        token = make_token({"sub": "user-123", "exp": datetime(2000, 1, 1, tzinfo=timezone.utc)})
        response = auth_client.get("/protected", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 401
        assert response.get_json()["error_code"] == "UNAUTHORIZED_ERROR"

    def test_tampered_token_returns_401(self, auth_client):
        token = make_token({"sub": "user-123"})
        tampered = token[:-4] + "xxxx"
        response = auth_client.get("/protected", headers={"Authorization": f"Bearer {tampered}"})
        assert response.status_code == 401

    def test_token_missing_sub_returns_401(self, auth_client):
        token = make_token({"email": "test@example.com"})
        response = auth_client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401

    def test_unconfigured_secret_returns_401(self, app):
        app.config["JWT_SECRET"] = ""

        @app.get("/protected-no-secret")
        @require_auth
        def protected_no_secret():
            return {}

        client = app.test_client()
        token = make_token({"sub": "user-123"})
        response = client.get("/protected-no-secret", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
