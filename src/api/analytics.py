from fastapi import APIRouter, Depends, HTTPException
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
def get_movie_analytics(movie_id : int):
    views = 0
    rated = 0
    liked = 0
    disliked = 0
    rating = 0
    with db.engine.begin() as connection:
        try:
            sql_to_execute = "SELECT 1 FROM movies WHERE id = :movie_id"
            connection.execute(sqlalchemy.text(sql_to_execute), {"movie_id":movie_id}).scalar_one()
        except sqlalchemy.exc.NoResultFound:
            print("Movie Does Not Exists")
            raise HTTPException(status_code=404, detail="No Movie Found")
        sql_to_execute = """
            with perception (likes, count) AS (
                SELECT liked, COUNT(liked) 
                FROM liked_movies 
                WHERE movie_id = :movie_id 
                GROUP BY liked
            )

            SELECT 
                (SELECT COUNT(user_id) FROM watched_movies WHERE movie_id = :movie_id) AS views, 
                (SELECT COUNT(user_id) FROM ratings WHERE movie_id = :movie_id) AS rated, 
                (SELECT AVG(rating) FROM ratings WHERE movie_id = :movie_id) AS rating,
                (SELECT count FROM perception WHERE likes = True) AS liked, 
                (SELECT count FROM perception WHERE likes = False) AS disliked
            """
        results = connection.execute(sqlalchemy.text(sql_to_execute), {"movie_id":movie_id})
        for result in results:
            views = result.views
            rated = result.rated
            rating = result.rating
            liked = result.liked
            disliked = result.disliked
    return {
        "views": views,
        "rated": rated,
        "average_rating": rating,
        "liked": liked,
        "disliked": disliked
    }

@router.get("/genre/{genre}")
def get_genre_analytics(genre : str):
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT genres.id FROM genres WHERE genres.name = :genre"
        genre_id = 0
        try:
            genre_id = connection.execute(sqlalchemy.text(sql_to_execute), {"genre":genre}).scalar_one()
        except sqlalchemy.exc.NoResultError:
            print("Genre Does Not Exists")
            raise HTTPException(status_code=404, detail="No Genre Found")
        sql_to_execute = """
                        """
    genre = {
        "average_views": "integer",
        "average_rating": "integer",
        "average_likes": "integer",
        "average_dislikes": "integer",
        "most_views": "integer",
        "highest_rating": "integer",
        "least_views": "integer",
        "lowest_rating": "integer",
        "movie_ids": ["integer"] 
        }
    return NotImplemented

@router.get("/popular")
def get_most_popular():
    movies = []
    analytic = {
        "movie_id": "integer",
        "viewed": "integer",
        "rated": "integer",
        "liked": "integer",
    }
    return NotImplemented




