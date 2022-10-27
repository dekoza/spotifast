from pathlib import Path

import anyio
import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from tortoise.contrib.fastapi import HTTPNotFoundError

from . import const
from .models import Artist, ArtistFetch, ArtistP, ArtistResponse
from .utils import fetch_artist_data_from_spotify, fill_db, get_auth_headers

CURRENT_DIR = Path(__file__).parent

load_dotenv()
router = APIRouter()


class Status(BaseModel):
    message: str


@router.get("/")
async def main_page():
    # fill db on first entry
    await fill_db()
    afile = await anyio.open_file(CURRENT_DIR / "templates/base.html")
    output = await afile.read()
    return HTMLResponse(content=output)


@router.get("/artists/", response_model=list[ArtistP])
async def list_artists() -> list[ArtistP]:
    """
    List artists saved in database.
    """
    return await ArtistP.from_queryset(Artist.all())


@router.post("/artists/", response_model=ArtistP)
async def create_artist(artist: ArtistP) -> ArtistP:
    """
    Create new Artist entry in database.
    """
    artist_obj = await Artist.create(**artist.dict(exclude_unset=True))
    return await ArtistP.from_tortoise_orm(artist_obj)


@router.post(
    "/artists/fetch/",
    response_model=ArtistP,
    responses={404: {"model": HTTPNotFoundError}},
)
async def fetch_artist(artist: ArtistFetch):
    """
    Fetch Artist data from Spotify. You can take the spotify_id from Search.
    """
    spotify_id = artist.spotify_id
    defaults = await fetch_artist_data_from_spotify(spotify_id)
    artist, created = await Artist.get_or_create(
        spotify_id=spotify_id, defaults=defaults
    )
    if not created:
        for k, v in defaults.items():
            setattr(artist, k, v)
        await artist.save()
    return await ArtistP.from_queryset_single(Artist.get(spotify_id=spotify_id))


@router.get("/artists/spotisearch/", response_model=ArtistResponse)
async def spotisearch(query: str, offset: int = 0, limit: int = 10):
    """
    Search Artists on Spotify.
    """
    client = httpx.AsyncClient()
    headers = await get_auth_headers()
    params = {"q": query, "type": "artist", "offset": offset, "limit": limit}
    result = await client.get(url=const.SEARCH_URL, params=params, headers=headers)
    return result.json().get("artists")


@router.get(
    "/artists/{artist_id}/",
    response_model=ArtistP,
    responses={404: {"model": HTTPNotFoundError}},
)
async def artist_detail(artist_id: int):
    return await ArtistP.from_queryset_single(Artist.get(id=artist_id))


@router.put(
    "/artists/{artist_id}/",
    response_model=ArtistP,
    responses={404: {"model": HTTPNotFoundError}},
)
async def update_artist(artist_id: int, artist: ArtistP):
    await Artist.filter(id=artist_id).update(**artist.dict(exclude_unset=True))
    return await ArtistP.from_queryset_single(Artist.get(id=artist_id))


@router.delete(
    "/artists/{artist_id}/",
    response_model=Status,
    responses={404: {"model": HTTPNotFoundError}},
)
async def remove_artist(artist_id: int):
    deleted = await Artist.filter(id=artist_id).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Artist {artist_id} not found")
    return Status(message=f"Deleted artist {artist_id}")
