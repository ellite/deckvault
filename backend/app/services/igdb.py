import asyncio
import httpx
from sqlalchemy.orm import Session

_token_cache: dict = {}


def clear_token_cache():
    _token_cache.clear()


def _get_credentials(db: Session) -> tuple[str, str] | None:
    from ..routers.settings import get_setting
    client_id = get_setting(db, "igdb_client_id")
    client_secret = get_setting(db, "igdb_client_secret")
    if not client_id or not client_secret:
        return None
    return client_id, client_secret


async def _get_token(client_id: str, client_secret: str) -> str | None:
    cache_key = client_id
    if _token_cache.get(cache_key):
        return _token_cache[cache_key]
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
            },
        )
        r.raise_for_status()
        token = r.json()["access_token"]
        _token_cache[cache_key] = token
        return token


async def search_games(query: str, db: Session) -> list[dict]:
    if not query or len(query) > 200:
        return []
    creds = _get_credentials(db)
    if not creds:
        return []
    client_id, client_secret = creds

    escaped = query.replace("\\", "\\\\").replace('"', '\\"')
    fields = 'fields id,name,summary,first_release_date,rating,genres.name,cover.image_id;'
    body_search = f'search "{escaped}"; {fields} limit 20;'
    body_name   = f'{fields} where name ~ *"{escaped}"*; limit 20;'

    for attempt in range(2):
        token = await _get_token(client_id, client_secret)
        if not token:
            return []
        async with httpx.AsyncClient() as client:
            r_search, r_name = await asyncio.gather(
                client.post("https://api.igdb.com/v4/games",
                            headers={"Client-ID": client_id, "Authorization": f"Bearer {token}"},
                            content=body_search),
                client.post("https://api.igdb.com/v4/games",
                            headers={"Client-ID": client_id, "Authorization": f"Bearer {token}"},
                            content=body_name),
            )
        if r_search.status_code == 401 or r_name.status_code == 401:
            clear_token_cache()
            continue
        r_search.raise_for_status()
        r_name.raise_for_status()

        seen: dict[int, dict] = {}
        for g in r_search.json() + r_name.json():
            if g["id"] not in seen:
                seen[g["id"]] = g
        return [_format_game(g) for g in seen.values()]

    return []


def _format_game(g: dict) -> dict:
    cover_url = None
    if g.get("cover"):
        cover_url = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{g['cover']['image_id']}.jpg"
    genres = ", ".join(gen["name"] for gen in g.get("genres", []))
    release_year = None
    if g.get("first_release_date"):
        from datetime import datetime, timezone
        release_year = datetime.fromtimestamp(g["first_release_date"], tz=timezone.utc).year
    return {
        "igdb_id": g["id"],
        "title": g["name"],
        "cover_url": cover_url,
        "genres": genres or None,
        "release_year": release_year,
        "summary": g.get("summary"),
        "rating": round(g["rating"], 1) if g.get("rating") else None,
    }
