from enum import StrEnum
from datetime import datetime

from sqlalchemy import ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

from database.settings import engine

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_user_id: Mapped[str]

class ReelService(StrEnum):  
    YOUTUBE = "youtube"  
    VK = "vk"  
    INSTAGRAM = "instagram"  
    TIKTOK = "tiktok"

class AdvertStat(Base):  
    __tablename__ = "advert_stats"  

    id: Mapped[int] = mapped_column(primary_key=True)  
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))  
    article: Mapped[str]  
    service: Mapped[StrEnum] = mapped_column(SQLEnum(ReelService))  
    link: Mapped[str]
    active: Mapped[bool]

class AdvertStatMark(Base):  
    __tablename__ = "advert_stat_marks"  

    id: Mapped[int] = mapped_column(primary_key=True)  
    advert_stat_id: Mapped[int] = mapped_column(  
        ForeignKey("advert_stats.id", ondelete="CASCADE")  
    )  
    datetime: Mapped[datetime]
    views: Mapped[int]  
    likes: Mapped[int]  
    comments: Mapped[int]

Base.metadata.create_all(engine)
