import base64

import httpx
import pendulum
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from tortoise.contrib.fastapi import HTTPNotFoundError

from . import settings
from .models import Artist, ArtistP, AuthData

load_dotenv()
router = APIRouter()


class Status(BaseModel):
    message: str


def get_spotify_headers():
    credentials = base64.b64encode(
        f"{settings.SPOTIFY_ID}:{settings.SPOTIFY_SECRET}".encode("ascii")
    )
    return {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {credentials.decode()}",
    }


async def fetch_token():
    client = httpx.AsyncClient()
    data = {"grant_type": "client_credentials"}
    headers = get_spotify_headers()
    response = await client.post(url=settings.TOKEN_URL, data=data, headers=headers)
    return response.json()


async def get_auth_token():
    auth_data = await AuthData.first()
    if not auth_data or auth_data.is_expired():
        token_data = await fetch_token()
        expires = pendulum.now("UTC").add(seconds=token_data["expires_in"])
        if auth_data:
            auth_data.token = token_data["access_token"]
            auth_data.expires = expires
            await auth_data.save()
        else:
            auth_data = await AuthData.create(
                token=token_data["access_token"], expires=expires
            )
    return auth_data.token


@router.get("/")
async def main_page():
    artists = await Artist.all()
    return await get_auth_token()


@router.get("/artists/", response_model=list[ArtistP])
async def list_artists() -> list[ArtistP]:
    return await ArtistP.from_queryset(Artist.all())


@router.post("/artists/", response_model=ArtistP)
async def create_artist(artist: ArtistP) -> ArtistP:
    artist_obj = await Artist.create(**artist.dict(exclude_unset=True))
    return await ArtistP.from_tortoise_orm(artist_obj)


@router.get(
    "/artists/{artist_id}/",
    response_model=ArtistP,
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_artist(artist_id: int):
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
