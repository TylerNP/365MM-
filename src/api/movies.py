from fastapi import APIRouter, Depends
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix = "/movies",
    tags = ["movies"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/{movie_id}")
def get_movie():
    return NotImplemented

@router.post("/new/")
def new_movie():
    return NotImplemented

@router.get("/available")
def get_movie_available():
    return NotImplemented

@router.get("/user/{user_id}")
def get_movie_interested():
    return NotImplemented