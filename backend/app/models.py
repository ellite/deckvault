import enum
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class StorageType(str, enum.Enum):
    local = "local"
    sdcard = "sdcard"
    hdd = "hdd"
    ssd = "ssd"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    storage_mediums = relationship("StorageMedium", back_populates="owner", cascade="all, delete-orphan")


class StorageMedium(Base):
    __tablename__ = "storage_mediums"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(StorageType), nullable=False)
    label = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    size_gb = Column(Float, nullable=True)
    free_gb = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    color = Column(String, default="#6366f1")
    color_primary = Column(String, default="#dc2626")
    color_secondary = Column(String, default="#1c1c2e")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="storage_mediums")
    games = relationship("Game", back_populates="storage_medium", cascade="all, delete-orphan")


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    storage_medium_id = Column(Integer, ForeignKey("storage_mediums.id"), nullable=False)
    igdb_id = Column(Integer, nullable=True)
    title = Column(String, nullable=False)
    cover_url = Column(String, nullable=True)
    genres = Column(String, nullable=True)
    release_year = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    storage_medium = relationship("StorageMedium", back_populates="games")


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
