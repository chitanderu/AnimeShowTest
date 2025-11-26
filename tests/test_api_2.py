# tests/test_api_2.py
from typing import List
from pathlib import Path

import pytest
import yaml
from sqlalchemy.pool import StaticPool  # ✅ 注意这里是 from sqlalchemy.pool import StaticPool

pytest.importorskip("fastapi")
pytest.importorskip("sqlmodel")

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
## 只跑新文件里的测试
#PYTHONPATH=. pytest tests/test_api_2.py --alluredir=allure-results

#allure serve allure-results

import main

# ---- Allure 兼容处理：没有安装 allure 也能运行测试 ----
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


# ---- 测试专用客户端：用 sqlite 内存库 + 覆盖 get_session ----
@pytest.fixture()
def test_client(monkeypatch):
    """Provide a TestClient with an isolated in-memory database."""
    # 使用共享内存 sqlite，这样 create_all 创建的表在后续请求中也可见
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            yield session

    # 覆盖掉 main.get_session，让接口用 sqlite 而不是 MySQL
    main.app.dependency_overrides[main.get_session] = get_session_override

    # 测试时不跑 MySQL 的 startup/shutdown 事件
    main.app.router.on_startup.clear()
    main.app.router.on_shutdown.clear()

    with TestClient(main.app) as client:
        yield client

    main.app.dependency_overrides.clear()


# ========= 下面是你原来的三个测试，用来对比 =========

@allure.feature("character search")
def test_search_character_success(monkeypatch, test_client):
    mock_characters = [
        {
            "id": 1,
            "name": {"full": "Naruto Uzumaki", "native": "うずまき ナルト", "alternative": []},
            "image": {"large": "large.jpg", "medium": "medium.jpg"},
            "description": "Ninja",
            "gender": "Male",
            "age": "17",
            "dateOfBirth": {"year": 1990, "month": 10, "day": 10},
            "bloodType": "O",
            "favourites": 100,
            "siteUrl": "https://example.com",
            "media": {"edges": []},
        }
    ]

    def fake_search(name: str, per_page: int = 5) -> List[dict]:
        return mock_characters

    # 用 monkeypatch 把真实的 AniList 调用替换掉，避免发真实网络请求
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
    assert save_response.status_code == 200
    save_data = save_response.json()
    assert save_data["code"] == 0

    list_response = test_client.get("/api/getallcharacters")
    assert list_response.status_code == 200
    characters = list_response.json()
    assert any(char["id"] == 2 for char in characters)
    assert characters[0]["name_full"] == "Sakura Haruno"


# ========= 下面是「YAML + parametrize」的新增部分 =========

def load_search_cases():
    """
    从 tests/data/search_cases.yaml 读取测试用例
    """
    yaml_path = Path(__file__).parent / "data" / "search_cases.yaml"
    with yaml_path.open("r", encoding="utf-8") as f:
        cases = yaml.safe_load(f)
    return cases


SEARCH_CASES = load_search_cases()
SEARCH_CASE_IDS = [case["name"] for case in SEARCH_CASES]


@allure.feature("character search")
@allure.story("search with yaml cases")
@pytest.mark.parametrize("case", SEARCH_CASES, ids=SEARCH_CASE_IDS)
def test_search_character_with_yaml(monkeypatch, test_client, case):
    """
    使用 YAML 数据驱动测试 /api/character/search

    - 对于非空名字，我们用 fake_search 把外部 AniList API Mock 掉，避免真实网络请求
    - 对于空字符串 / 只空格，接口本身会直接返回 400
    """
    query = case["query"]

    # 如果 query 非空，则 mock 掉 search_characters_from_anilist，返回固定数据
    if query.strip():
        def fake_search(name: str, per_page: int = 5) -> List[dict]:
            return [
                {
                    "id": 1,
                    "name": {
                        "full": "Naruto Uzumaki",
                        "native": "うずまき ナルト",
                        "alternative": [],
                    },
                    "image": {"large": "large.jpg", "medium": "medium.jpg"},
                    "description": "Ninja",
                    "gender": "Male",
                    "age": "17",
                    "dateOfBirth": {"year": 1990, "month": 10, "day": 10},
                    "bloodType": "O",
                    "favourites": 100,
                    "siteUrl": "https://example.com",
                    "media": {"edges": []},
                }
            ]

        monkeypatch.setattr(main, "search_characters_from_anilist", fake_search)

    # 1. 发请求
    resp = test_client.get("/api/character/search", params={"name": query})

    # 2. 断言 HTTP 状态码
    assert resp.status_code == case["expect_status"]

    # 3. 如果预期是 200，再检查业务字段
    if case["expect_status"] == 200:
        data = resp.json()
        # 如果 YAML 里写了 expect_code，就校验它
        if "expect_code" in case:
            assert data.get("code") == case["expect_code"]
        assert "data" in data
        assert "characters" in data["data"]
        assert len(data["data"]["characters"]) > 0
