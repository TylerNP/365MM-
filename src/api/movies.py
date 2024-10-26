from fastapi import APIRouter, Depends, HTTPException
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix = "/movies",
    tags = ["movies"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/{movie_id}")
def get_movie(movie_id : int):
    movie = {}
    result = None
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT name, release_year, genres, average_rating, budget, box_office, demographic FROM movies WHERE id = :movie_id"
        result = connection.execute(sqlalchemy.text(sql_to_execute), {"movie_id":movie_id})
    for info in result:
        movie["movie_id"] = movie_id
        movie["name"] = info.name
        movie["release_year"] = info.release_year
        movie["genres"] = info.genres
        movie["average_rating"] = info.average_rating
        movie["budget"] = info.budget
        movie["box_office"] = info.box_office
        movie["demographic"] = info.demographic
    return movie

@router.post("/new/")
def new_movie():
    return NotImplemented

@router.get("/available")
def get_movie_available():
    return NotImplemented

@router.get("/user/{user_id}")
def get_movie_interested():
    return NotImplemented