import pendulum
import pydantic
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class AuthData(models.Model):
    created = fields.DatetimeField(auto_now_add=True)
    expires = fields.DatetimeField()
    token = fields.CharField(max_length=256)

    def is_expired(self):
        return (self.expires - pendulum.now("UTC")).seconds < 0


class Artist(models.Model):
    name = fields.CharField(max_length=100)
    spotify_id = fields.CharField(max_length=32, index=True)
    followers = fields.IntField(default=0)
    popularity = fields.IntField(default=0)
    genres = fields.CharField(max_length=256, default="")
    image_url = fields.CharField(max_length=256, default="")
    locked = fields.BooleanField(default=False)


ArtistP = pydantic_model_creator(Artist)


class ArtistFetch(pydantic.BaseModel):
    spotify_id: str


class ArtistResponseItem(pydantic.BaseModel):
    external_urls: dict
    followers: dict
    genres: list[str]
    href: str
    id: str
    images: list[dict]
    name: str
    popularity: int
    type: str
    uri: str


class ArtistResponse(pydantic.BaseModel):
    href: str
    items: list[ArtistResponseItem]
    limit: int
    offset: int
    next: str | None
    previous: str | None
    total: int
