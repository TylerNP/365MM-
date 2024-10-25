from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix = "/users",
    tags = ["users"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/signup")
def user_signup(username : str):
    # CHECK IF NAME IS UNIQUE
    # USE UNIQUENESS CONSTRAINT
    sql_to_execute = """
                        INSERT INTO users (username)
                        VALUES (:username)
                    """
    with db.engine.begin() as connection:
        try:
            connection.execute(sqlalchemy.text(sql_to_execute), {"username":username})
        except:
            return None

    # IF SO, ADDED TO DB
    return "success"


def user_login():
    with db.engine.begin() as connection:
        'SELECT username FROM users WHERE username = '
        return NotImplemented


def user_list():
    return NotImplemented


def user_rate_movie():
    return NotImplemented


def user_watched_movie():
    return NotImplemented

