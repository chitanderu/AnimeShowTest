from typing import Any, Optional, List
from pydantic import BaseModel


class APIResponse(BaseModel):
    """统一API响应格式"""
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None


class CharacterSearchData(BaseModel):
    """角色搜索结果数据"""
    characters: List[dict]
    total: int


class CharacterSearchResponse(APIResponse):
    """角色搜索响应"""
    data: Optional[CharacterSearchData] = None
