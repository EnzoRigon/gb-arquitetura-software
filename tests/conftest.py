from collections.abc import Generator
from typing import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models.base import Base


DEFAULT_PASSWORD = "123456"


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def user_factory(client: TestClient) -> Callable[[str, str, str], dict]:
    def _create(name: str, email: str, password: str = DEFAULT_PASSWORD) -> dict:
        response = client.post(
            "/users",
            json={
                "full_name": name,
                "email": email,
                "password": password,
            },
        )
        assert response.status_code == 201
        return response.json()

    return _create


@pytest.fixture()
def token_factory(client: TestClient) -> Callable[[str, str], str]:
    def _login(email: str, password: str = DEFAULT_PASSWORD) -> str:
        response = client.post("/auth/login", json={"email": email, "password": password})
        assert response.status_code == 200
        return response.json()["access_token"]

    return _login


@pytest.fixture()
def auth_header() -> Callable[[str], dict[str, str]]:
    def _headers(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    return _headers
