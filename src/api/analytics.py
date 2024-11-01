from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix = "/analytics",
    tags = ["analytics"],
)


class search_sort_options(str, Enum):
    movie_name = "movie_name"
    budget = "budget"
    box_office = "box_office"
    demographic = "demographic"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/")
def search_orders(
    movie_name : str = "",
    budget : int = 0,
    box_office : int = 0,
    demographic : list[str]= [],
):
    return NotImplemented

@router.get("/movies/{movie_id}")
def get_movie_analytics():
    with db.engine.begin() as connection:
        print()
    return NotImplemented

@router.post("/genre/{genre_id}")
def get_genre_analytics():
    return NotImplemented

@router.post("/popular")
def get_most_popular():
    return NotImplemented




