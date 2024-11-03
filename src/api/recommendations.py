from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import random

router = APIRouter(
    prefix = "/recommendations",
    tags = ["recommendations"],
)

@router.get("/{user_id}")
def get_recommended(user_id: int):
    with db.engine.begin() as connection:
        good_rating = 5
        # get top 3 genres for a user if they exist
        sql_to_execute = '''
                            SELECT movie_genres.genre_id as genre, COUNT(1) as num_of_movies 
                            FROM ratings 
                            JOIN movies ON ratings.movie_id = movies.id
                            JOIN movie_genres ON movies.id = movie_genres.movie_id
                            WHERE user_id = :user_id AND ratings.rating >= :good_rating
                            GROUP BY movie_genres.genre_id
                            ORDER BY num_of_movies DESC
                            LIMIT 3      
                        '''
        values = {"user_id": user_id, "good_rating": good_rating}
        users_top_genres = list(connection.execute(sqlalchemy.text(sql_to_execute), values))
        number_of_genres = len(users_top_genres)
        recommended_movies = []
        sql_to_execute = """
                                SELECT
                                movies.id,
                                movies.name,
                                movies.release_date,
                                movies.description,
                                movies.average_rating,
                                movies.budget,
                                movies.box_office
                                FROM
                                movies
                                JOIN movie_genres ON movies.id = movie_genres.movie_id 
                                WHERE
                                NOT EXISTS (
                                    SELECT
                                    1
                                    FROM
                                    watched_movies
                                    WHERE
                                    user_id = :user_id
                                    AND movie_id = movies.id
                                ) AND movie_genres.genre_id = :genre_id
                                ORDER BY
                                RANDOM()
                                LIMIT
                                :limit
                            """
        # based on how many genres a user has indirectly positivly rated, we will return a different proportion of movies related to genres
        if number_of_genres == 3:
            values = {'user_id': user_id, "genre_id": users_top_genres[0][0], "limit": 3}
            recommended_movies += list(connection.execute(sqlalchemy.text(sql_to_execute), values))
            values = {'user_id': user_id, "genre_id": users_top_genres[1][0], "limit": 2}
            recommended_movies += list(connection.execute(sqlalchemy.text(sql_to_execute), values))
            values = {'user_id': user_id, "genre_id": users_top_genres[2][0], "limit": 1}
            recommended_movies += list(connection.execute(sqlalchemy.text(sql_to_execute), values))
        elif number_of_genres == 2:
            values = {'user_id': user_id, "genre_id": users_top_genres[0][0], "limit": 3}
            recommended_movies += list(connection.execute(sqlalchemy.text(sql_to_execute), values))
            values = {'user_id': user_id, "genre_id": users_top_genres[1][0], "limit": 3}
            recommended_movies += list(connection.execute(sqlalchemy.text(sql_to_execute), values))
        elif number_of_genres == 1:
            values = {'user_id': user_id, "genre_id": users_top_genres[0][0], "limit": 6}
            recommended_movies += list(connection.execute(sqlalchemy.text(sql_to_execute), values))
        else: 
            # default to random genre movie
            min_max = connection.execute(sqlalchemy.text("SELECT MIN(id), MAX(id) FROM genres")).one()
            for _ in range(6):
                r = random.randrange(min_max[0], min_max[1])
                values = {'user_id': user_id, "genre_id": r, "limit": 1}
                recommended_movies += list(connection.execute(sqlalchemy.text(sql_to_execute), values))

        # map the recommended movies into proper format
        return list(map(format_movie, recommended_movies))

def format_movie(movie_result) -> dict[str, any]:
    movie = {}
    movie["movie_id"] = movie_result[0]
    movie["name"] = movie_result[1]
    movie["release_date"] = movie_result[2]
    movie["description"] = movie_result[3]
    movie["average_rating"] = movie_result[4]
    movie["budget"] = movie_result[5]
    movie["box_office"] = movie_result[6]
    return movie

            

# @router.post("/{user_id}/reset/")
# def reset_recommended():
#     return NotImplemented

# @router.post("/{user_id}/delete/{movie_id}")
# def delete_recommendation():
#     return NotImplemented

@router.post("/{user_id}/generate/")
def generate_recommendation():
    return NotImplemented

@router.post("/{user_id}/collab/")
def generate_recommendation_collab():
    return NotImplemented

"""
    https://pyimagesearch.com/2023/06/19/fundamentals-of-recommendation-systems/
    Try To Create Simple Recommendation Engine 

    Content (CONS -> No Info On New Users/ Very  Specialized Results)
        -> Use User's Likes/Dislikes of Specific Features To Get A Vector of User Likes/Dislikes
        -> Create a Vector of Same Features For Movies
        -> Take Dotproduct/ (Normal of User * Normal of Movie) FOr Score
    Collaborative (CONS -> No Ratings On Movies = Bad Recommendation, Hard To Identify Most Similar Users)
        -> Find Similar Users that Already Rated a Movie
        -> Use this to Score Movies to Reocmmend 
"""

"""
    Recommendation Engine (Content-Based)
    - Potential Vector Weights
        - Genres
        - Avg Ratings on Movie
        - Avg Likes
        #- Number of Views

"""
    
if __name__ == "__main__":
    print("RAN")