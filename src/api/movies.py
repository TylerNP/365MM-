from fastapi import APIRouter, Depends, HTTPException
#from src.api import auth
from pydantic import BaseModel
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix = "/movies",
    tags = ["movies"],
    #dependencies=[Depends(auth.get_api_key)],
)

class Movie(BaseModel):
    name: str
    release_date: int
    genres: list[str]
    average_rating: int
    budget: int
    box_office: int
    demographic: list[str]


@router.get("/{movie_id}")
def get_movie(movie_id : int):
    """
    Return movie information for a given movie_id
    """
    movie = {}
    result = None
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT name, release_date, genres, average_rating, budget, box_office, demographic FROM movies WHERE id = :movie_id"
        result = connection.execute(sqlalchemy.text(sql_to_execute), {"movie_id":movie_id})
        movie = format_movie(result, movie_id)
    print(movie)
    return movie

@router.post("/new/")
def new_movie(new_movie : Movie):
    """
    Create a new entry for a movie
    """
    print(new_movie)
    movie_id = 0
    with db.engine.begin() as connection:
        sql_to_execute = """
                            INSERT INTO movies (name, release_date, genres, average_rating, budget, box_office, demographic)
                            VALUES (:name, :release_date, :genres, :average_rating, :budget, :box_office, :demographic)
                            RETURNING id
                        """
        values = {
            "name":new_movie.name,
            "release_date":new_movie.release_date,
            "genres":new_movie.genres,
            "average_rating":new_movie.average_rating,
            "budget":new_movie.budget,
            "box_office":new_movie.box_office,
            "demographic":new_movie.demographic
        }
        try:
            movie_id = connection.execute(sqlalchemy.text(sql_to_execute), values).scalar()
        except sqlalchemy.exc.IntegrityError:
            print("Movie Already Exists")
            return {}
    return {
        "movie_id":movie_id
    }

@router.get("/available")
def get_movie_available():
    return NotImplemented

@router.get("/user/{user_id}")
def get_movie_interested(user_id : int):
    """
    Gets a random movie that a user has not watched, empty if no movies available
    """
    movie = {}
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT users.id FROM users WHERE users.id = :user_id"
        exsits = list(connection.execute(sqlalchemy.text(sql_to_execute), {"user_id": user_id}))
        if len(exsits) == 0:
            return movie
        sql_to_execute = """
                            SELECT 
                                movies.id, 
                                movies.name, 
                                movies.release_date,
                                movies.genres,
                                movies.average_rating,
                                movies.budget,
                                movies.box_office, 
                                movies.demographic 
                            FROM 
                                movies
                            WHERE NOT EXISTS (
                                SELECT 1 
                                FROM watched_movies 
                                WHERE user_id = :user_id
                                AND movie_id = movies.id
                            ) 
                            ORDER BY 
                                RANDOM() 
                            LIMIT 1
                        """
        results = list(connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id}))
        movie_id = 0
        for result in results:
            movie_id = result.id 
        movie = format_movie(results, movie_id)
        print(movie)
    return movie

# Takes CursorResult Object And Converts into Movie Dictionary For Json
def format_movie(movie_result : object, movie_id : int) -> dict[str, any]:
    movie = {}
    for info in movie_result:
        movie["movie_id"] = movie_id
        movie["name"] = info.name
        movie["release_date"] = info.release_date
        movie["genres"] = info.genres
        movie["average_rating"] = info.average_rating
        movie["budget"] = info.budget
        movie["box_office"] = info.box_office
        movie["demographic"] = info.demographic
    return movie