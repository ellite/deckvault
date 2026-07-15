from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, StorageMedium, Game
from ..schemas import GameCreate, GameOut, GameDetailOut, InstallInfo, LibraryEntry
from ..dependencies import get_current_user
from ..services.igdb import search_games

router = APIRouter(tags=["games"])


def _owned_medium(medium_id: int, user: User, db: Session) -> StorageMedium:
    medium = db.query(StorageMedium).filter(
        StorageMedium.id == medium_id,
        StorageMedium.user_id == user.id,
    ).first()
    if not medium:
        raise HTTPException(status_code=404, detail="Storage medium not found")
    return medium


@router.get("/storage/{medium_id}/games", response_model=list[GameOut])
def list_games(
    medium_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _owned_medium(medium_id, current_user, db)
    return db.query(Game).filter(Game.storage_medium_id == medium_id).all()


@router.post("/storage/{medium_id}/games", response_model=GameOut, status_code=status.HTTP_201_CREATED)
def add_game(
    medium_id: int,
    data: GameCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _owned_medium(medium_id, current_user, db)
    game = Game(**data.model_dump(), storage_medium_id=medium_id)
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


@router.put("/games/{game_id}", response_model=GameOut)
def update_game(
    game_id: int,
    data: GameCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    _owned_medium(game.storage_medium_id, current_user, db)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(game, field, value)
    db.commit()
    db.refresh(game)
    return game


@router.get("/games/library", response_model=list[LibraryEntry])
def get_library(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Game, StorageMedium)
        .join(StorageMedium, Game.storage_medium_id == StorageMedium.id)
        .filter(StorageMedium.user_id == current_user.id)
        .order_by(Game.title)
        .all()
    )

    groups: dict[str, dict] = {}
    for game, medium in rows:
        key = f"igdb-{game.igdb_id}" if game.igdb_id else f"game-{game.id}"
        if key not in groups:
            groups[key] = {
                "igdb_id": game.igdb_id,
                "title": game.title,
                "cover_url": game.cover_url,
                "genres": game.genres,
                "release_year": game.release_year,
                "rating": game.rating,
                "summary": game.summary,
                "installations": [],
            }
        groups[key]["installations"].append(InstallInfo(
            game_id=game.id,
            storage_id=medium.id,
            storage_label=medium.label,
            storage_type=medium.type.value,
            storage_color=medium.color,
        ))

    entries = [
        LibraryEntry(**{**data, "is_duplicate": len(data["installations"]) > 1})
        for data in groups.values()
    ]
    entries.sort(key=lambda e: e.title.lower())
    return entries


@router.get("/games/{game_id}", response_model=GameDetailOut)
def get_game(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    _owned_medium(game.storage_medium_id, current_user, db)

    other_installations = []
    if game.igdb_id:
        others = (
            db.query(Game, StorageMedium)
            .join(StorageMedium, Game.storage_medium_id == StorageMedium.id)
            .filter(
                Game.igdb_id == game.igdb_id,
                Game.id != game.id,
                StorageMedium.user_id == current_user.id,
            )
            .all()
        )
        other_installations = [
            InstallInfo(
                game_id=g.id,
                storage_id=m.id,
                storage_label=m.label,
                storage_type=m.type.value,
                storage_color=m.color,
            )
            for g, m in others
        ]

    return {**GameOut.model_validate(game).model_dump(), "other_installations": other_installations}


@router.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    _owned_medium(game.storage_medium_id, current_user, db)
    db.delete(game)
    db.commit()


@router.get("/igdb/search")
async def igdb_search(
    q: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await search_games(q, db)
