import pendulum
from tortoise import fields, models


class AuthData(models.Model):
    created = fields.DatetimeField(auto_now_add=True)
    expires = fields.DatetimeField()
    token = fields.CharField(max_length=256)

    def is_expired(self):
        return (self.expires - pendulum.now("UTC")).seconds < 0


class Artist:
    name: str
