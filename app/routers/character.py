import logging
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Character
from app.services import AniListService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["character"])


@router.get("/character/search")
async def search_character(name: str):
    """
    搜索角色（从AniList API返回多个结果）

    Args:
        name: 角色名字（查询参数）

    Returns:
        标准化的角色列表数据
    """
    try:
        logger.info(f"开始搜索角色: {name}")

        if not name or not name.strip():
            raise HTTPException(status_code=400, detail="角色名字不能为空")

        # 调用 AniList 服务搜索角色
        formatted_characters = AniListService.search_and_format(name.strip())

        if not formatted_characters:
            raise HTTPException(status_code=404, detail=f"未找到角色: {name}")

        logger.info(f"成功找到 {len(formatted_characters)} 个角色")

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


@router.get("/getallcharacters", response_model=List[Character])
async def get_all_characters(session: Session = Depends(get_session)):
    """
    获取数据库中所有已保存的角色

    Returns:
        角色列表
    """
    results = session.exec(select(Character)).all()
    return results


@router.post("/character/save")
def save_character(character: Dict, session: Session = Depends(get_session)):
    """
    保存前端选中的角色到数据库

    Args:
        character: 角色数据
        session: 数据库会话

    Returns:
        保存结果
    """
    try:
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
