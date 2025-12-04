from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Text


class Character(SQLModel, table=True):
    """角色数据模型"""

    __tablename__ = "characters"

    id: Optional[int] = Field(default=None, primary_key=True)
    name_full: Optional[str] = Field(default=None, max_length=100)
    name_native: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[str] = Field(default=None, max_length=20)
    age: Optional[str] = Field(default=None, max_length=20)
    favourites: Optional[int] = Field(default=0)
    image_url: Optional[str] = Field(default=None, max_length=300)
    description: Optional[str] = Field(default=None, sa_column=Field(default=None, sa_column=Text()))
    site_url: Optional[str] = Field(default=None, max_length=300)
