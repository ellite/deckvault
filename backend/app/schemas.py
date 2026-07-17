from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from .models import StorageType


# Auth
class UserRegister(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class TokenData(BaseModel):
    user_id: int


# Storage
class StorageMediumCreate(BaseModel):
    type: StorageType
    label: str
    brand: Optional[str] = None
    model: Optional[str] = None
    size_gb: Optional[float] = None
    free_gb: Optional[float] = None
    notes: Optional[str] = None
    color: Optional[str] = "#6366f1"
    color_primary: Optional[str] = "#dc2626"
    color_secondary: Optional[str] = "#1c1c2e"


class StorageMediumUpdate(BaseModel):
    label: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    size_gb: Optional[float] = None
    free_gb: Optional[float] = None
    notes: Optional[str] = None
    color: Optional[str] = None
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None


class GameOut(BaseModel):
    id: int
    storage_medium_id: int
    igdb_id: Optional[int]
    title: str
    cover_url: Optional[str]
    genres: Optional[str]
    release_year: Optional[int]
    summary: Optional[str]
    rating: Optional[float]
    added_at: datetime

    model_config = {"from_attributes": True}


class StorageMediumOut(BaseModel):
    id: int
    user_id: int
    type: StorageType
    label: str
    brand: Optional[str]
    model: Optional[str]
    size_gb: Optional[float]
    free_gb: Optional[float]
    notes: Optional[str]
    color: str
    color_primary: Optional[str]
    color_secondary: Optional[str]
    created_at: datetime
    games: list[GameOut] = []

    model_config = {"from_attributes": True}


# Games
class GameCreate(BaseModel):
    igdb_id: Optional[int] = None
    title: str
    cover_url: Optional[str] = None
    genres: Optional[str] = None
    release_year: Optional[int] = None
    summary: Optional[str] = None
    rating: Optional[float] = None


class GameDetailOut(GameOut):
    other_installations: list["InstallInfo"] = []


# Library
class InstallInfo(BaseModel):
    game_id: int
    storage_id: int
    storage_label: str
    storage_type: str
    storage_color: str


class LibraryEntry(BaseModel):
    igdb_id: Optional[int]
    title: str
    cover_url: Optional[str]
    genres: Optional[str]
    release_year: Optional[int]
    rating: Optional[float]
    summary: Optional[str]
    installations: list[InstallInfo]
    is_duplicate: bool


# Settings
class SettingUpdate(BaseModel):
    value: str


class SystemSettingsOut(BaseModel):
    registration_enabled: bool


# Admin
class UserAdminUpdate(BaseModel):
    is_admin: Optional[bool] = None
