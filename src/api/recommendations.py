from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import random
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from src.api.utils import format_movie_with_agg

router = APIRouter(
    prefix = "/recommendations",
    tags = ["recommendations"],
)

@router.get("/{user_id}")
def get_recommended(user_id: int):
    with db.engine.begin() as connection:
        # get 3-0 collabrative filtered items --> if they are good ones, then add them and get less genre recommended, else stick with genre
        sql_to_execute = '''
                                SELECT user_id, movie_id, rating FROM ratings
                                ORDER BY user_id, rating    
                        '''
        users_ratings = list(connection.execute(sqlalchemy.text(sql_to_execute)))
        df = pd.DataFrame(users_ratings, columns=["user_id", "movie_id", "rating"])
        user_item_matrix = df.pivot(index="user_id", columns="movie_id", values="rating")
        user_item_matrix.fillna(0, inplace=True)
        user_similarity = cosine_similarity(user_item_matrix)
        print(user_similarity)
        user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

        potential_movies = []
        # if the user has rated something before
        if user_id in user_item_matrix.index:
            users_rating = user_item_matrix.loc[user_id]
            similar_users = user_similarity_df[user_id] # for our user 
            weighted_ratings = user_item_matrix.T.dot(similar_users) / similar_users.sum()
            weighted_ratings = user_item_matrix.T.dot(similar_users) / similar_users.sum()
            recomendations = weighted_ratings[users_rating == 0].sort_values(ascending=False).head(5)
            recomendations = recomendations[weighted_ratings >= 2.5].index.to_numpy()
            potential_movies = (recomendations)

        to_append = []
        for movie in potential_movies:
            sql_to_execute = '''
                SELECT
                movies.id,
                movies.name,
                movies.release_date,
                movies.description,
                movies.average_rating,
                movies.budget,
                movies.box_office,
                ARRAY_AGG( DISTINCT COALESCE( genres.name, 'N/A')) as genres,
                ARRAY_AGG( DISTINCT COALESCE(movie_languages.language, 'N/A')) as languages
                FROM
                movies
                JOIN movie_genres ON movies.id = movie_genres.movie_id 
                JOIN genres ON movie_genres.genre_id = genres.id
                LEFT JOIN movie_languages on movies.id = movie_languages.movie_id
                WHERE movies.id = :movie_id
                GROUP BY movies.id,
                movies.name,
                movies.release_date,
                movies.description,
                movies.average_rating,
                movies.budget,
                movies.box_office
            '''
            result = list(connection.execute(sqlalchemy.text(sql_to_execute), {"movie_id":int(movie)}))
            to_append.append(format_movie_with_agg(result[0]))

        # genre recommended
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
        # Make a with table for not watched movies, and then filter off of that in later version
        sql_to_execute = """
                                SELECT
                                movies.id,
                                movies.name,
                                movies.release_date,
                                movies.description,
                                movies.average_rating,
                                movies.budget,
                                movies.box_office,
                                ARRAY_AGG( DISTINCT COALESCE( genres.name, 'N/A')) as genres,
                                ARRAY_AGG( DISTINCT COALESCE(movie_languages.language, 'N/A')) as languages
                                FROM
                                movies
                                JOIN movie_genres ON movies.id = movie_genres.movie_id 
                                JOIN genres ON movie_genres.genre_id = genres.id
                                LEFT JOIN movie_languages on movies.id = movie_languages.movie_id
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
                                GROUP BY movies.id,
                                movies.name,
                                movies.release_date,
                                movies.description,
                                movies.average_rating,
                                movies.budget,
                                movies.box_office
                                ORDER BY
                                RANDOM()
                                LIMIT :limit
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
        return (list(map(format_movie_with_agg, recommended_movies)) + to_append)

            

# @router.post("/{user_id}/reset/")
# def reset_recommended():
#     return NotImplemented

# @router.post("/{user_id}/delete/{movie_id}")
# def delete_recommendation():
#     return NotImplemented

# @router.post("/{user_id}/generate/")
# def generate_recommendation():
#     return NotImplemented

# @router.post("/{user_id}/collab/")
# def generate_recommendation_collab():
#     return NotImplemented

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