from sqlmodel import SQLModel, Session, create_engine
from typing import Generator, Optional
from sqlalchemy import Engine

from app.config import settings

# 使用懒加载模式，避免导入时立即连接数据库
_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """获取数据库引擎（懒加载）"""
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.database_url,
            echo=False,
            pool_pre_ping=True
        )
    return _engine


def init_db() -> None:
    """初始化数据库，创建所有表"""
    SQLModel.metadata.create_all(get_engine())


def get_session() -> Generator[Session, None, None]:
    """数据库会话依赖注入"""
    with Session(get_engine()) as session:
        yield session


# 为了向后兼容，提供 engine 属性
@property
def engine() -> Engine:
    return get_engine()
