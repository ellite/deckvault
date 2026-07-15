from fastapi import FastAPI
from .routers import auth, storage, games, settings

app = FastAPI(title="DeckVault API", docs_url="/docs")

app.include_router(auth.router)
app.include_router(storage.router)
app.include_router(games.router)
app.include_router(settings.router)


@app.get("/health")
def health():
    return {"status": "ok"}
