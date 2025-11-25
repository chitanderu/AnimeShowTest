from typing import Optional, List, Dict
import os

import pymysql
from django.db.models.expressions import result
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlalchemy import Column, BigInteger, Text
from fastapi.middleware.cors import CORSMiddleware
import logging
import requests
logger = logging.getLogger(__name__)
# ---- SQLModel 定义（映射已有表 users）----

from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional
from pydantic import BaseModel
class Character(SQLModel, table=True):
    __tablename__ = "characters"
    id: Optional[int] = Field(default=None, primary_key=True)
    name_full: Optional[str] = Field(default=None, max_length=100)
    name_native: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[str] = Field(default=None, max_length=20)
    age: Optional[str] = Field(default=None, max_length=20)
    favourites: Optional[int] = Field(default=0)
    image_url: Optional[str] = Field(default=None, max_length=300)
    description: Optional[str] = Field(default=None, sa_column=Field(default=None, sa_column=Text()))  # ← 重点
    site_url: Optional[str] = Field(default=None, max_length=300)
# ---- 数据库引擎 & 会话依赖 ----
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:59591468@127.0.0.1:3306/anime?charset=utf8mb4"
)
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

def get_session():
    with Session(engine) as session:
        yield session


# ---- FastAPI 应用 ----
app = FastAPI()
# 配置CORS,允许Vue前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 保证元数据就绪；若表已存在不会覆盖（相当于 no-op）




@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

ANILIST_API_URL = "https://graphql.anilist.co"
def search_characters_from_anilist(search_name: str, per_page: int = 5):
    """
    从 AniList API 搜索角色（返回多个结果）

    Args:
        search_name: 角色名字
        per_page: 返回结果数量

    Returns:
        list: 角色信息列表
    """
    query = '''
    query ($search: String, $page: Int, $perPage: Int) {
      Page(page: $page, perPage: $perPage) {
        characters(search: $search, sort: FAVOURITES_DESC) {
          id
          name {
            first
            middle
            last
            full
            native
            alternative
          }
          image {
            large
            medium
          }
          description
          gender
          dateOfBirth {
            year
            month
            day
          }
          age
          bloodType
          favourites
          siteUrl
          media(page: 1, perPage: 3, sort: POPULARITY_DESC) {
            edges {
              node {
                id
                title {
                  romaji
                  english
                  native
                }
                type
              }
            }
          }
        }
      }
    }
    '''

    variables = {
        'search': search_name,
        'page': 1,
        'perPage': per_page
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    response = requests.post(
        ANILIST_API_URL,
        json={'query': query, 'variables': variables},
        headers=headers,
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and data['data']['Page']['characters']:
            return data['data']['Page']['characters']
        else:
            return []
    else:
        raise Exception(f"AniList API 请求失败: {response.status_code}")


@app.get("/api/character/search")
async def search_character(name: str):
    """
    搜索角色（返回多个结果）

    Args:
        name: 角色名字（查询参数）

    Returns:
        dict: 标准化的角色列表数据
    """
    try:
        logger.info(f"开始搜索角色: {name}")

        if not name or not name.strip():
            raise HTTPException(status_code=400, detail="角色名字不能为空")

        # 调用 AniList API（返回前5个结果）
        characters = search_characters_from_anilist(name.strip(), per_page=5)

        if not characters:
            raise HTTPException(status_code=404, detail=f"未找到角色: {name}")

        # 数据格式转换 - 转换为前端期望的格式
        formatted_characters = []

        for character in characters:
            formatted_character = {
                'id': character.get('id', 0),
                'name': {
                    'full': character.get('name', {}).get('full', ''),
                    'native': character.get('name', {}).get('native', ''),
                    'alternative': character.get('name', {}).get('alternative', [])
                },
                'image': {
                    'large': character.get('image', {}).get('large', ''),
                    'medium': character.get('image', {}).get('medium', '')
                },
                'description': character.get('description', ''),
                'gender': character.get('gender', ''),
                'age': character.get('age', ''),
                'dateOfBirth': {
                    'year': character.get('dateOfBirth', {}).get('year'),
                    'month': character.get('dateOfBirth', {}).get('month'),
                    'day': character.get('dateOfBirth', {}).get('day')
                },
                'bloodType': character.get('bloodType', ''),
                'favourites': character.get('favourites', 0),
                'siteUrl': character.get('siteUrl', ''),
                'media': []
            }

            # 处理出现的作品
            if character.get('media') and character['media'].get('edges'):
                for edge in character['media']['edges'][:3]:  # 只取前3个作品
                    node = edge.get('node', {})
                    title = node.get('title', {})
                    formatted_character['media'].append({
                        'id': node.get('id', 0),
                        'title': title.get('english') or title.get('romaji') or title.get('native', ''),
                        'type': node.get('type', '')
                    })

            formatted_characters.append(formatted_character)

        logger.info(f"成功找到 {len(formatted_characters)} 个角色")



        # 返回标准化的格式
        return {
            'code': 0,
            'message': 'success',
            'data': {
                'characters': formatted_characters,
                'total': len(formatted_characters)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索角色失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")



@app.get("/api/getallcharacters",response_model=List[Character])
async def get_all_characters(session=Depends(get_session)):

    results = session.exec(select(Character)).all()
    return  results



@app.post("/api/character/save")
def save_character(character: Dict, session: Session = Depends(get_session)):
    """
    保存前端选中的角色到数据库
    """
    try:
        # 将前端传来的 JSON 转为 ORM 对象
        char = Character(
            id=character.get('id'),
            name_full=character.get('name', {}).get('full'),
            name_native=character.get('name', {}).get('native'),
            gender=character.get('gender'),
            age=character.get('age'),
            favourites=character.get('favourites'),
            image_url=character.get('image', {}).get('medium'),
            description=character.get('description'),
            site_url=character.get('siteUrl')
        )

        # merge() = INSERT or UPDATE
        session.merge(char)
        session.commit()

        return {"code": 0, "message": "角色已保存成功", "data": {"id": char.id}}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"保存失败: {e}")

