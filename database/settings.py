import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, URL
from sqlalchemy.orm import Session

load_dotenv(override=True)

DEVELOPMENT_MODE = bool(int(os.getenv("DEVELOPMENT_MODE")))

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")

POSTGRES_PORT = 5432
POSTGRES_HOST = "postgres"

if DEVELOPMENT_MODE:
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
    POSTGRES_HOST = "localhost"

POSTGRES_DB = os.getenv("POSTGRES_DB")

engine = create_engine(
    URL.create(
        drivername="postgresql+psycopg2",
        username=POSTGRES_USER,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB
    ),
    echo=True
)

session = Session(engine)
