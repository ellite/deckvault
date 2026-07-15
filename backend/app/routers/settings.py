from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, SystemSetting
from ..schemas import SystemSettingsOut, UserOut, UserAdminUpdate
from ..dependencies import get_current_user, get_admin_user

router = APIRouter(prefix="/settings", tags=["settings"])


def get_setting(db: Session, key: str, default: str = "") -> str:
    s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    return s.value if s else default


def set_setting(db: Session, key: str, value: str):
    s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if s:
        s.value = value
    else:
        db.add(SystemSetting(key=key, value=value))
    db.commit()


@router.get("", response_model=SystemSettingsOut)
def get_settings(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SystemSettingsOut(
        registration_enabled=get_setting(db, "registration_enabled", "true") == "true",
    )


@router.put("/registration")
def toggle_registration(
    enabled: bool,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    set_setting(db, "registration_enabled", "true" if enabled else "false")
    return {"registration_enabled": enabled}


# IGDB credentials

class IGDBCredentials(BaseModel):
    client_id: str
    client_secret: str


class IGDBStatus(BaseModel):
    client_id: str
    has_secret: bool


@router.get("/igdb", response_model=IGDBStatus)
def get_igdb(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return IGDBStatus(
        client_id=get_setting(db, "igdb_client_id"),
        has_secret=bool(get_setting(db, "igdb_client_secret")),
    )


@router.put("/igdb")
def save_igdb(
    data: IGDBCredentials,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    from ..services.igdb import clear_token_cache
    set_setting(db, "igdb_client_id", data.client_id.strip())
    set_setting(db, "igdb_client_secret", data.client_secret.strip())
    clear_token_cache()
    return {"ok": True}


# Users

@router.get("/users", response_model=list[UserOut])
def list_users(
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    return db.query(User).all()


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserAdminUpdate,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.is_admin is not None:
        if user.id == current_admin.id and not data.is_admin:
            raise HTTPException(status_code=400, detail="Cannot remove your own admin status")
        user.is_admin = data.is_admin
    db.commit()
    db.refresh(user)
    return user
