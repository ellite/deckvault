import asyncio
import time
import httpx
from sqlalchemy.orm import Session

_token_cache: dict = {}
_genres_cache: list[dict] = []


def clear_token_cache():
    _token_cache.clear()
    _genres_cache.clear()


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
    fields = 'fields id,name,summary,first_release_date,rating,genres.name,cover.image_id,platforms.name;'
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


async def get_genres(db: Session) -> list[dict]:
    global _genres_cache
    if _genres_cache:
        return _genres_cache
    creds = _get_credentials(db)
    if not creds:
        return []
    client_id, client_secret = creds

    for attempt in range(2):
        token = await _get_token(client_id, client_secret)
        if not token:
            return []
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.igdb.com/v4/genres",
                headers={"Client-ID": client_id, "Authorization": f"Bearer {token}"},
                content="fields id,name; limit 50; sort name asc;",
            )
        if r.status_code == 401:
            clear_token_cache()
            continue
        if r.status_code == 200:
            _genres_cache = r.json()
            return _genres_cache
        break

    return []


async def browse_games(
    query: str | None,
    sort: str,
    genre_id: int | None,
    limit: int,
    offset: int,
    db: Session,
) -> list[dict]:
    creds = _get_credentials(db)
    if not creds:
        return []
    client_id, client_secret = creds

    fields = "fields id,name,summary,first_release_date,rating,total_rating_count,genres.id,genres.name,cover.image_id,platforms.name;"
    where_parts = ["cover != null"]
    if genre_id:
        where_parts.append(f"genres = ({genre_id})")

    now_ts = int(time.time())

    if query and query.strip():
        escaped = query.strip().replace("\\", "\\\\").replace('"', '\\"')
        if sort == "relevance" or not sort:
            where_str = " & ".join(where_parts)
            body = f'search "{escaped}"; {fields} where {where_str}; limit {limit}; offset {offset};'
        else:
            where_parts.append(f'name ~ *"{escaped}"*')
            if sort == "rating":
                where_parts.append("rating != null")
                sort_clause = "sort rating desc;"
            elif sort == "newest":
                where_parts.append(f"first_release_date != null & first_release_date <= {now_ts}")
                sort_clause = "sort first_release_date desc;"
            elif sort == "name_asc":
                sort_clause = "sort name asc;"
            else:
                sort_clause = "sort total_rating_count desc;"
            where_str = " & ".join(where_parts)
            body = f"{fields} where {where_str}; {sort_clause} limit {limit}; offset {offset};"
    else:
        if sort == "rating":
            where_parts.append("rating != null & total_rating_count > 20")
            sort_clause = "sort rating desc;"
        elif sort == "newest":
            where_parts.append(f"first_release_date != null & first_release_date <= {now_ts}")
            sort_clause = "sort first_release_date desc;"
        elif sort == "name_asc":
            sort_clause = "sort name asc;"
        else:
            where_parts.append("total_rating_count != null")
            sort_clause = "sort total_rating_count desc;"
        where_str = " & ".join(where_parts)
        body = f"{fields} where {where_str}; {sort_clause} limit {limit}; offset {offset};"

    for attempt in range(2):
        token = await _get_token(client_id, client_secret)
        if not token:
            return []
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.igdb.com/v4/games",
                headers={"Client-ID": client_id, "Authorization": f"Bearer {token}"},
                content=body,
            )
        if r.status_code == 401:
            clear_token_cache()
            continue
        if r.status_code != 200:
            return []
        return [_format_game(g) for g in r.json()]

    return []


def _format_game(g: dict) -> dict:
    cover_url = None
    if g.get("cover"):
        cover_url = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{g['cover']['image_id']}.jpg"
    genres = ", ".join(gen["name"] for gen in g.get("genres", []))
    platforms = ", ".join(p["name"] for p in g.get("platforms", []))
    release_year = None
    if g.get("first_release_date"):
        from datetime import datetime, timezone
        release_year = datetime.fromtimestamp(g["first_release_date"], tz=timezone.utc).year
    return {
        "igdb_id": g["id"],
        "title": g["name"],
        "cover_url": cover_url,
        "genres": genres or None,
        "platforms": platforms or None,
        "release_year": release_year,
        "summary": g.get("summary"),
        "rating": round(g["rating"], 1) if g.get("rating") else None,
    }
