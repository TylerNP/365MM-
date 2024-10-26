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

class user(BaseModel):
    username: str

@router.post("/signup")
def user_signup(new_user : user):
    # CHECK IF NAME IS UNIQUE
    # USE UNIQUENESS CONSTRAINT
    sql_to_execute = """
                        INSERT INTO users (username)
                        VALUES (:username)
                    """
    with db.engine.begin() as connection:
        try:
            connection.execute(sqlalchemy.text(sql_to_execute), {"username":new_user.username})
        except:
            return "BAD"

    # IF SO, ADDED TO DB
    return "OK"

def user_login():
    with db.engine.begin() as connection:
        set = 'SELECT username FROM users WHERE username = '
        return "ok"


def user_list():
    return "ok"


def user_rate_movie():
    return "ok"


def user_watched_movie():
    return "ok"

