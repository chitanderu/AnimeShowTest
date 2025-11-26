from typing import List

import pytest
from sqlalchemy import StaticPool

pytest.importorskip("fastapi")
pytest.importorskip("sqlmodel")

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

import main

try:  # pragma: no cover - compatibility shim when allure is unavailable
    import allure
except ImportError:  # pragma: no cover - fallback for offline test execution
    class _AllureStub:
        def __getattr__(self, name):
            def decorator(*args, **kwargs):
                def wrapper(func):
                    return func

                return wrapper

            return decorator

    allure = _AllureStub()


@pytest.fixture()
def test_client(monkeypatch):
    """Provide a TestClient with an isolated in-memory database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            yield session

    main.app.dependency_overrides[main.get_session] = get_session_override
    with TestClient(main.app) as client:
        yield client
    main.app.dependency_overrides.clear()


@allure.feature("character search")
def test_search_character_success(monkeypatch, test_client):
    mock_characters = [
        {
            "id": 1,
            "name": {"full": "Naruto Uzumaki", "native": "うずまき ナルト", "alternative": []},
            "image": {"large": "large.jpg", "medium": "medium.jpg"},
            "description": "Ninja", "gender": "Male", "age": "17",
            "dateOfBirth": {"year": 1990, "month": 10, "day": 10},
            "bloodType": "O",
            "favourites": 100,
            "siteUrl": "https://example.com",
            "media": {"edges": []},
        }
    ]

    def fake_search(name: str, per_page: int = 5) -> List[dict]:
        return mock_characters

    monkeypatch.setattr(main, "search_characters_from_anilist", fake_search)

    response = test_client.get("/api/character/search", params={"name": "Naruto"})
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 1
    assert data["data"]["characters"][0]["name"]["full"] == "Naruto Uzumaki"


@allure.feature("character search")
def test_search_character_validation_error(test_client):
    response = test_client.get("/api/character/search", params={"name": "   "})
    assert response.status_code == 400
    assert response.json()["detail"] == "角色名字不能为空"


@allure.feature("database interactions")
@allure.story("save and retrieve characters")
def test_save_and_get_characters(test_client):
    payload = {
        "id": 2,
        "name": {"full": "Sakura Haruno", "native": "春野 サクラ"},
        "gender": "Female",
        "age": "16",
        "favourites": 80,
        "image": {"medium": "sakura.jpg"},
        "description": "Kunoichi",
        "siteUrl": "https://example.com/sakura",
    }

    save_response = test_client.post("/api/character/save", json=payload)
    print("save_response:", save_response.status_code, save_response.text)
    assert save_response.status_code == 200
    save_data = save_response.json()
    assert save_data["code"] == 0

    list_response = test_client.get("/api/getallcharacters")
    assert list_response.status_code == 200
    characters = list_response.json()
    assert any(char["id"] == 2 for char in characters)
    assert characters[0]["name_full"] == "Sakura Haruno"


#PYTHONPATH=. pytest --alluredir=allure-results
