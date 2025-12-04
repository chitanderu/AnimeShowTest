"""
AnimeShow API - 入口文件

这是一个兼容入口，实际应用在 app/main.py
使用方式:
    uvicorn main:app --reload
    或者
    uvicorn app.main:app --reload
"""

from app.main import app

# 为了向后兼容，导出常用模块
from app.models import Character
from app.database import get_engine, get_session
from app.config import settings

__all__ = ["app", "Character", "get_engine", "get_session", "settings"]

