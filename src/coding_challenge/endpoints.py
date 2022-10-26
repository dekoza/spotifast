import base64

import httpx
import pendulum
from dotenv import load_dotenv
from fastapi import APIRouter

from . import settings
from .models import AuthData

load_dotenv()
router = APIRouter()


def get_spotify_headers():
    credentials = base64.b64encode(
        f"{settings.SPOTIFY_ID}:{settings.SPOTIFY_SECRET}".encode("ascii")
    )
    return {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {credentials.decode()}",
    }


async def get_auth_token():
    auth_data = await AuthData.first()
    if not auth_data or auth_data.is_expired():
        client = httpx.AsyncClient()
        data = {"grant_type": "client_credentials"}
        headers = get_spotify_headers()
        response = await client.post(url=settings.TOKEN_URL, data=data, headers=headers)
        token_data = response.json()
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
    return await get_auth_token()
