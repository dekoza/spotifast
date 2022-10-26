import pendulum
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
    spotify_uri = fields.CharField(max_length=100, index=True)
    followers = fields.SmallIntField(default=0)
    popularity = fields.SmallIntField(default=0)
    genres = fields.CharField(max_length=256)
    image_url = fields.CharField(max_length=256)
    locked = fields.BooleanField(default=False)


ArtistP = pydantic_model_creator(Artist)
