import base64

import httpx
import pendulum

from spotifast import const, settings
from spotifast.models import AuthData


def get_login_headers():
    credentials = base64.b64encode(
        f"{settings.SPOTIFY_ID}:{settings.SPOTIFY_SECRET}".encode("ascii")
    )
    return {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {credentials.decode()}",
    }


async def get_auth_headers():
    token = await get_auth_token()
    return {"Authorization": f"Bearer {token}"}


async def fetch_token():
    client = httpx.AsyncClient()
    data = {"grant_type": "client_credentials"}
    headers = get_login_headers()
    response = await client.post(url=const.TOKEN_URL, data=data, headers=headers)
    assert response.status_code == 200, f"Bad ID {settings.SPOTIFY_ID}"
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


def prep_artist_defaults(data) -> dict:
    results = {
        "name": data["name"],
        "popularity": data["popularity"],
        "followers": data["followers"]["total"],
        "genres": ", ".join(data["genres"]),
    }
    return results
