from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, StorageMedium
from ..schemas import StorageMediumCreate, StorageMediumUpdate, StorageMediumOut
from ..dependencies import get_current_user

router = APIRouter(prefix="/storage", tags=["storage"])


@router.get("", response_model=list[StorageMediumOut])
def list_storage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(StorageMedium).filter(StorageMedium.user_id == current_user.id).all()


@router.post("", response_model=StorageMediumOut, status_code=status.HTTP_201_CREATED)
def create_storage(
    data: StorageMediumCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    medium = StorageMedium(**data.model_dump(), user_id=current_user.id)
    db.add(medium)
    db.commit()
    db.refresh(medium)
    return medium


@router.get("/{medium_id}", response_model=StorageMediumOut)
def get_storage(
    medium_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    medium = db.query(StorageMedium).filter(
        StorageMedium.id == medium_id,
        StorageMedium.user_id == current_user.id,
    ).first()
    if not medium:
        raise HTTPException(status_code=404, detail="Not found")
    return medium


@router.put("/{medium_id}", response_model=StorageMediumOut)
def update_storage(
    medium_id: int,
    data: StorageMediumUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    medium = db.query(StorageMedium).filter(
        StorageMedium.id == medium_id,
        StorageMedium.user_id == current_user.id,
    ).first()
    if not medium:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(medium, field, value)
    db.commit()
    db.refresh(medium)
    return medium


@router.delete("/{medium_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_storage(
    medium_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    medium = db.query(StorageMedium).filter(
        StorageMedium.id == medium_id,
        StorageMedium.user_id == current_user.id,
    ).first()
    if not medium:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(medium)
    db.commit()
