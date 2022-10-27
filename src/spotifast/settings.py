import os

SPOTIFY_ID = os.getenv("SPOTIFY_ID")
SPOTIFY_SECRET = os.getenv("SPOTIFY_SECRET")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite://:memory:")
