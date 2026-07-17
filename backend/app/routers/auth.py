from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, status
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import User, UserSession, SystemSetting
from ..schemas import UserRegister, UserLogin, UserOut, ChangePassword
from ..auth import hash_password, verify_password, create_access_token, decode_token
from ..dependencies import get_current_user
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_NAME = "deckVault_token"
COOKIE_MAX_AGE = settings.access_token_expire_minutes * 60


def _set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        max_age=COOKIE_MAX_AGE,
        samesite="lax",
    )


def _create_session(db: Session, user: User) -> str:
    token, jti, expires_at = create_access_token(user.id)
    # prune expired sessions for this user opportunistically
    db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.expires_at <= datetime.now(timezone.utc),
    ).delete()
    db.add(UserSession(jti=jti, user_id=user.id, expires_at=expires_at))
    db.commit()
    return token


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, response: Response, db: Session = Depends(get_db)):
    reg_setting = db.query(SystemSetting).filter(SystemSetting.key == "registration_enabled").first()
    if reg_setting and reg_setting.value == "false":
        raise HTTPException(status_code=403, detail="Registration is disabled")

    username_taken = db.query(User).filter(User.username == data.username).first()
    email_taken = db.query(User).filter(User.email == data.email).first()
    if username_taken or email_taken:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    is_first_user = db.query(User).count() == 0
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        is_admin=is_first_user,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if is_first_user:
        db.add(SystemSetting(key="registration_enabled", value="true"))
        db.commit()

    token = _create_session(db, user)
    _set_auth_cookie(response, token)
    return user


@router.post("/login", response_model=UserOut)
def login(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = _create_session(db, user)
    _set_auth_cookie(response, token)
    return user


@router.post("/logout")
def logout(
    response: Response,
    deckVault_token: Optional[str] = Cookie(default=None),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if deckVault_token:
        decoded = decode_token(deckVault_token)
        if decoded:
            _, jti = decoded
            db.query(UserSession).filter(UserSession.jti == jti).delete()
            db.commit()
    response.delete_cookie(key=COOKIE_NAME)
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/change-password")
def change_password(
    data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"ok": True}
