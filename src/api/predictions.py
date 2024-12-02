from fastapi import APIRouter, HTTPException
#from pydantic import BaseModel
#from src.api import auth
#from enum import Enum
import math
import time
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix = "/predictions",
    tags = ["predictions"],
)

@router.get("/{movie_id}")
def get_prediction(movie_id : int):
    start_time = time.time()
    prediction = {}
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT predicted_ratings, predicted_views, box_office FROM predictions WHERE movie_id = :movie_id"
        results = connection.execute(sqlalchemy.text(sql_to_execute), {"movie_id":movie_id})
        for result in results:
            prediction["predicted_ratings"] = result.predicted_ratings
            prediction["predicted_views"] = result.predicted_views
            prediction["box_office"] = result.box_office
        if not prediction:
            raise HTTPException(status_code=404, detail="No prediction found, prediction must first be generated")
    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} ms")
    return prediction

@router.post("/generate/{movie_id}")
def create_prediction(movie_id : int):
    """
    Attempt to predict the performance of a movie (with respect to 365MM)
    """
    start_time = time.time()

    sql_to_execute = """
        WITH search_genres AS (
            SELECT movie_genres.genre_id 
            FROM movie_genres 
            WHERE movie_genres.movie_id = :movie_id
        ),
        movie_to_check AS (
            SELECT movies.id, movies.duration, EXTRACT(YEAR FROM movies.release_date) "year", EXTRACT(MONTH FROM movies.release_date) "month"
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

        SELECT movie_to_check.id, ARRAY_AGG(DISTINCT genres.name) AS genres, movie_views.view, movie_ratings.avg, 
                movie_rev.box_office, movie_to_check.duration, movie_to_check.year, movie_to_check.month
        FROM movie_to_check
        JOIN movie_genres ON movie_to_check.id = movie_genres.movie_id 
        LEFT JOIN search_genres ON movie_genres.genre_id = search_genres.genre_id
        JOIN genres ON movie_genres.genre_id = genres.id
        LEFT JOIN movie_views ON movie_to_check.id = movie_views.id 
        LEFT JOIN movie_ratings ON movie_to_check.id = movie_ratings.id 
        LEFT JOIN movie_rev ON movie_to_check.id = movie_rev.id 
        WHERE view IS NOT NULL OR avg IS NOT NULL OR box_office IS NOT NULL
        GROUP BY movie_to_check.id, movie_views.view, movie_ratings.avg, movie_rev.box_office, movie_to_check.duration, 
                movie_to_check.year, movie_to_check.month
    """

    genres = None
    duration = 0
    year = 0
    month = 0
    rating_count = 0
    num_view_count = 0
    num_box_office_count = 0
    ratings_total = 0
    views_total = 0
    box_office_total = 0
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT 1 FROM predictions WHERE predictions.movie_id = :movie_id"), {"movie_id":movie_id})
        for _ in result:
            print("Movie Prediction Already Generated")
            raise HTTPException(status_code=409, detail="Movie prediction already generated")
        result = connection.execute(sqlalchemy.text("""
            SELECT movies.duration, EXTRACT(YEAR FROM movies.release_date) "year", 
                EXTRACT(MONTH FROM movies.release_date) "month", 
                ARRAY_AGG(genres.name) OVER (PARTITION BY movies.id) AS genres 
            FROM movies
            JOIN movie_genres ON movies.id = movie_genres.movie_id 
            JOIN genres ON movie_genres.genre_id = genres.id
            WHERE movies.id = :movie_id
            LIMIT 1
        """), {"movie_id":movie_id})

        for value in result:
            genres = value.genres
            year = value.year
            month = value.month
            duration = value.duration
        
        if not genres: # Could be year, month, or duration also
            raise HTTPException(status_code=404, detail="Not enough movie info")
        
        result = connection.execute(sqlalchemy.text(sql_to_execute), {"movie_id":movie_id})
        movie_vector = [3*len(genres), float(duration/15), float(year/1000), float(year%100/10), float(month/3)]
        movie_vector = normalize_vector(movie_vector)

        for values in result:
            # Improve Similarity Calculation
            score_vector = [0]*len(movie_vector)
            genre_value = 0
            for genre in genres:
                try:
                    list(values.genres).index(genre)
                except ValueError:
                    genre_value -= 0.25
                    continue
                genre_value += 3

            score_vector[0] = genre_value
            score_vector[1] = float(values.duration/15)
            score_vector[2] = float(values.year/1000)
            score_vector[3] = float(values.year%100/10)
            score_vector[4] = float(values.month/3)
            score_vector = normalize_vector(score_vector)

            similarity = sum(score_vector[i]*movie_vector[i] for i in range(len(movie_vector)))
            #print(similarity)

            if values.view:
                num_view_count += similarity
                views_total += similarity * float(values.view)
            if values.avg:
                rating_count += similarity
                ratings_total += similarity * float(values.avg)
            if values.box_office:
                num_box_office_count += similarity
                box_office_total += similarity * float(values.box_office)

        prediction = {
            "movie_id":movie_id,
            "predicted_ratings": ratings_total/rating_count if rating_count>0 else None,
            "predicted_views": views_total/num_view_count  if num_view_count>0 else None,
            "box_office": box_office_total/num_box_office_count  if num_box_office_count>0 else None
        }
        sql_insert = """
                    INSERT INTO predictions
                    (movie_id, predicted_ratings, predicted_views, box_office)
                    VALUES (:movie_id, :predicted_ratings, :predicted_views, :box_office)
                    """
        connection.execute(sqlalchemy.text(sql_insert), prediction)

    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} ms")
    return HTTPException(status_code=201, detail="Prediction Created")

def normalize_vector(vector : list[int]) -> list[int]:
    length = math.sqrt(sum(value*value for value in vector))
    return [value/length for value in vector]
    

'''
FOR LATER INSPECTION
        current_movie_genre = connection.execute(sqlalchemy.text(""
            SELECT movies.name, genres.name
            FROM movies
            JOIN movie_genres ON movies.id = movie_genres.movie_id
            JOIN genres ON genres.id = movie_genres.genre_id
            WHERE movies.id = :movie_id
        ""), {'movie_id':movie_id}).mappings()
        
        result = connection.execute(sqlalchemy.text(sql_to_execute), {'movie_id': movie_id}).mappings() #movies to compare 


    movie_count = 0 # number of movies
    current_movie_genre = []
    total_weighted_rating = 0
    total_weighted_views = 0
    total_weighted_box_office = 0 

    for row in current_movie_genre:
        current_movie_genre.append(row.name)
    print(current_movie_genre)

    
    for movie in result:
        #if any of the comparisons are null dont add to calculation
        if movie.view == "NULL" or movie.avg == "NULL" or movie.box_office == "NULL":
            continue

        #uses the set().intersection() \we get its count by using len which is the weight
        weight = len(set(movie.genres).intersection(current_movie_genre)) 

        if weight == 0:
            continue

        total_weighted_views += movie.view * weight
        total_weighted_rating += movie.avg * weight
        total_weighted_box_office += movie.box_office * weight

        movie_count += weight
    

    if movie_count > 0:
        prediction = {
            "movie_id":movie_id,
            "predicted_ratings": total_weighted_rating / movie_count,
            "predicted_views": total_weighted_views / movie_count,
            "box_office": total_weighted_box_office / movie_count,
        }
    else:
        # if no movies match, set the prediction to 0 for all fields
        prediction = {
            "movie_id":movie_id,
            "predicted_ratings": 0,
            "predicted_views": 0,
            "box_office": 0
        }

'''