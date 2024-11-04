from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix = "/predictions",
    tags = ["predictions"],
)

@router.get("/{movie_id}")
def get_prediction(movie_id : int):
    prediction = {}
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT predicted_ratings, predicted_views, box_office FROM predictions WHERE movie_id = :movie_id"
        try:
            results = connection.execute(sqlalchemy.text(sql_to_execute), {"movie_id":movie_id})
        except sqlalchemy.exc.NoResultFound:
            print("No prediction yet")
        for result in results:
            prediction["predicted_ratings"] = result.predicted_ratings
            prediction["predicted_views"] = result.predicted_views
            prediction["box_office"] = result.box_office
    return prediction

@router.post("/generate/")
def create_prediction(movie_id : int):
    # Get data on movies similary -> BY GENRES (USE SELECT)
    # COMPARE SIMILARITY (e.g. count how many of the same genres, compare movie length, etc)
    # Use some formula (e.g. movies with blank genres get an avg rating of 7, longer movies get lower reviews, etc)
    # Predict box_office, ratings, and views based off similarity
    sql_to_execute = """
        WITH search_genres AS (
            SELECT movie_genres.genre_id 
            FROM movie_genres 
            WHERE movie_genres.movie_id = :movie_id
        ),
        movie_to_check AS (
            SELECT movies.id 
            FROM movies 
            JOIN movie_genres ON movies.id = movie_genres.movie_id 
            JOIN search_genres ON movie_genres.genre_id = search_genres.genre_id
            WHERE movies.id != :movie_id
        ),
            movie_ratings AS (
            SELECT movie_to_check.id, AVG(ratings.rating) AS avg
            FROM movie_to_check
            JOIN ratings ON movie_to_check.id = ratings.movie_id
            GROUP BY movie_to_check.id
        ),
            movie_views AS (
            SELECT movie_to_check.id, COUNT(watched_movies.movie_id) AS view
            FROM movie_to_check
            JOIN watched_movies ON movie_to_check.id = watched_movies.movie_id
            GROUP BY movie_to_check.id
        ),
            movie_rev AS (
            SELECT movie_to_check.id, movies.box_office 
            FROM movie_to_check
            JOIN movies ON movie_to_check.id = movies.id AND box_office != 0
        )

        SELECT movie_to_check.id, ARRAY_AGG(genres.name) AS genres, movie_views.view, movie_ratings.avg, movie_rev.box_office
        FROM movie_to_check
        JOIN movie_genres ON movie_to_check.id = movie_genres.movie_id 
        JOIN search_genres ON movie_genres.genre_id = search_genres.genre_id
        JOIN genres ON movie_genres.genre_id = genres.id
        LEFT JOIN movie_views ON movie_to_check.id = movie_views.id 
        LEFT JOIN movie_ratings ON movie_to_check.id = movie_ratings.id 
        LEFT JOIN movie_rev ON movie_to_check.id = movie_rev.id 
        WHERE view IS NOT NULL OR avg IS NOT NULL OR box_office IS NOT NULL
        GROUP BY movie_to_check.id, movie_views.view, movie_ratings.avg, movie_rev.box_office
    """

    #LOOK AT ROWS
    # LOOK AT MATCHING GENRES (COUNT HOW MANY THE SAME)
    # SUM EACH RESULT * SIMILARITY 
    # KEEP TRACK OF NUMBER OF EACH RESULT 
    # AVERAGE EACH RESULT
    # INSERT INTO PREDICTION TABLE (predicted_ratings, predicted_views, box_office)
    # EX: 2 With Movies 
    #   1st Movie With Rating 7 And Similarity Score 2
    #   2nd Movie With Rating 5 And Similarity Score 3
    #   
    #  Rating_Total = 7*2 + 5*3
    #  Rating_Count = 2 + 3
    #  Rating_Avg = (14+15) / 5 -> 5.8

    return "OK"