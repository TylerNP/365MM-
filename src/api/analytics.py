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
    """
    Obtain information about the number of users that rated, watched, or liked/disliked a movie
    """
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
    """
    Obtain information about the avg statistics of movies in a specific genre 
    given they have some form of user interaction (rate, watched, liked)
    """
    result = None
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT genres.id FROM genres WHERE genres.name = :genre"
        try:
            genre_id = connection.execute(sqlalchemy.text(sql_to_execute), {"genre":genre}).scalar_one()
            sql_to_execute = """
                WITH movie_in_genre AS (
                    SELECT
                        movies.id AS movie_id, movies.name
                    FROM
                        movies
                    JOIN 
                        movie_genres ON movie_genres.movie_id = movies.id 
                        AND movie_genres.genre_id = :genre_id
                    GROUP BY
                        movies.id
                ),
                movie_views AS (
                    SELECT
                        movie_in_genre.movie_id,
                        COUNT(watched_movies.movie_id) AS views
                    FROM
                        movie_in_genre
                    JOIN
                        watched_movies
                    ON movie_in_genre.movie_id = watched_movies.movie_id
                    GROUP BY
                        movie_in_genre.movie_id
                ),
                movie_ratings AS (
                    SELECT
                        movie_in_genre.movie_id,
                        ROUND(AVG(ratings.rating), 1) AS movie_avg 
                    FROM
                        movie_in_genre
                    JOIN
                        ratings
                    ON movie_in_genre.movie_id = ratings.movie_id
                    GROUP BY
                        movie_in_genre.movie_id
                ),
                movie_likeness AS (
                    SELECT
                        movie_in_genre.movie_id,
                        SUM(CASE WHEN liked_movies.liked = True THEN 1 ELSE 0 END) AS total_likes,
                        SUM(CASE WHEN liked_movies.liked = False THEN 1 ELSE 0 END) AS total_dislikes
                    FROM
                        movie_in_genre
                    JOIN
                        liked_movies
                    ON movie_in_genre.movie_id = liked_movies.movie_id
                    GROUP BY
                        movie_in_genre.movie_id
                ),
                most_viewed_movies AS (
                    SELECT 
                        m.movie_id, 
                        m.rank 
                    FROM (
                        SELECT 
                        movie_views.movie_id, 
                        ROW_NUMBER() OVER (ORDER BY movie_views.views DESC) AS rank 
                        FROM movie_views
                    ) AS m LIMIT 1
                ),
                filtered_ratings AS (
                    SELECT 
                        high_ratings, 
                        low_ratings 
                    FROM (
                        (SELECT FIRST_VALUE(movie_id) OVER (ORDER BY rank) AS high_ratings, FIRST_VALUE(movie_id) OVER (ORDER BY rank DESC) AS low_ratings
                        FROM (
                            SELECT 
                            m.movie_id, 
                            m.rank 
                            FROM (
                            SELECT 
                                movie_ratings.movie_id, 
                                ROW_NUMBER() OVER (ORDER BY movie_ratings.movie_avg DESC) AS rank 
                            FROM movie_ratings ) AS m
                            ) AS temp
                        LIMIT 1)
                    ) AS done
                ),
                filtered_views AS (
                    SELECT high, low FROM (
                    (SELECT FIRST_VALUE(movie_id) OVER (ORDER BY rank) AS high, FIRST_VALUE(movie_id) OVER (ORDER BY rank DESC) AS low
                    FROM (
                        SELECT 
                        m.movie_id, 
                        m.rank 
                        FROM (
                        SELECT 
                            movie_views.movie_id, 
                            ROW_NUMBER() OVER (ORDER BY movie_views.views DESC) AS rank 
                        FROM movie_views) AS m
                        ) AS temp 
                    LIMIT 1)
                    ) AS done
                )

                SELECT
                    ROUND(AVG(movie_views.views), 1)::real  AS avg_views,
                    ROUND(AVG(movie_ratings.movie_avg), 1)::real  AS avg_ratings,
                    ROUND(AVG(movie_likeness.total_likes), 1)::real AS avg_likes,
                    ROUND(AVG(movie_likeness.total_dislikes), 1)::real AS avg_dislikes,
                    MAX(movie_views.views) AS most_views,
                    MAX(movie_ratings.movie_avg)::real AS highest_rating,
                    MIN(movie_views.views) AS least_views,
                    MIN(movie_ratings.movie_avg)::real AS lowest_rating,
                    (SELECT high_ratings FROM filtered_ratings) AS highest_rated_movie,
                    (SELECT low_ratings FROM filtered_ratings) AS lowest_rated_movie,
                    (SELECT high FROM filtered_views) AS highest_viewed_movie,
                    (SELECT low FROM filtered_views) AS lowest_viewed_movie
                FROM 
                    movie_in_genre
                LEFT JOIN
                    movie_views ON movie_in_genre.movie_id = movie_views.movie_id
                LEFT JOIN
                    movie_ratings ON movie_in_genre.movie_id = movie_ratings.movie_id
                LEFT JOIN
                    movie_likeness ON movie_in_genre.movie_id = movie_likeness.movie_id
            """
            result = connection.execute(sqlalchemy.text(sql_to_execute), {"genre_id":genre_id})
        except sqlalchemy.exc.NoResultFound:
            print("Genre Does Not Exists")
            raise HTTPException(status_code=404, detail="No Genre Found")
        
    genre = {}
    for values in result:
        if all(value == None for value in values):
            return genre
        genre = {
            "average_views": values.avg_views,
            "average_rating": values.avg_ratings,
            "average_likes": values.avg_likes,
            "average_dislikes": values.avg_dislikes,
            "most_views": values.most_views,
            "highest_rating": values.highest_rating,
            "least_views": values.least_views,
            "lowest_rating": values.lowest_rating,
            "movie_ids": [
                values.highest_rated_movie,
                values.lowest_rated_movie,
                values.highest_viewed_movie,
                values.lowest_viewed_movie
            ] 
        }
    return genre

class SearchOptions(str, Enum):
    views = "views"
    rated = "rated"
    liked = "liked"


@router.get("/popular")
def get_most_popular(sort_option: SearchOptions = SearchOptions.views):
    """
    Get the top 5 movies by ratings, views, or likes
    """
    movie_views = (
        sqlalchemy.select(
            db.movies.c.id.label("movie_id"),
            db.movies.c.name.label("name"),
            sqlalchemy.func.count(db.watched_movies.c.movie_id).label("views")
        )
        .select_from(db.movies)
        .join(db.watched_movies, db.movies.c.id == db.watched_movies.c.movie_id)
        .group_by(db.movies.c.id)
    ).cte("movie_views")

    movie_ratings = (
        sqlalchemy.select(
            db.movies.c.id.label("movie_id"),
            db.movies.c.name.label("name"),
            sqlalchemy.func.round(sqlalchemy.func.avg(db.ratings.c.rating), 1).label("movie_avg")
        )
        .select_from(db.movies)
        .join(db.ratings, db.movies.c.id == db.ratings.c.movie_id)
        .group_by(db.movies.c.id)
    ).cte("movie_ratings")

    movie_likes = (
        sqlalchemy.select(
            db.movies.c.id.label("movie_id"),
            db.movies.c.name.label("name"),
            sqlalchemy.func.sum(sqlalchemy.case((db.liked_movies.c.liked == True, 1), else_=0)).label("total_likes")
        )
        .select_from(db.movies)
        .join(db.liked_movies, db.movies.c.id == db.liked_movies.c.movie_id)
        .group_by(db.movies.c.id)
    ).cte("movie_likes")

    m = None
    if sort_option == SearchOptions.views:
        m = (
            sqlalchemy.select(
                movie_views.c.movie_id.label("movie_id"),
                movie_views.c.name.label("name"),
                sqlalchemy.func.row_number().over(order_by=sqlalchemy.desc(movie_views.c.views)).label("rank")
            )
            .select_from(movie_views)
        ).cte("m")
    elif sort_option == SearchOptions.rated:
        m = (
            sqlalchemy.select(
                movie_ratings.c.movie_id.label("movie_id"),
                movie_ratings.c.name.label("name"),
                sqlalchemy.func.row_number().over(order_by=sqlalchemy.desc(movie_ratings.c.movie_avg)).label("rank")
            )
            .select_from(movie_ratings)
        ).cte("m")
    elif sort_option == SearchOptions.liked:
        m = (
            sqlalchemy.select(
                movie_likes.c.movie_id.label("movie_id"),
                movie_likes.c.name.label("name"),
                sqlalchemy.func.row_number().over(order_by=sqlalchemy.desc(movie_likes.c.total_likes)).label("rank")
            )
            .select_from(movie_likes)
        ).cte("m")
    else:
        assert False
    stmt = (
        sqlalchemy.select(
            m.c.movie_id.label("movie_id"),
            m.c.name.label("name"),
            m.c.rank.label("rank"),
            movie_views.c.views.label("views"),
            movie_ratings.c.movie_avg.label("movie_avg"),
            movie_likes.c.total_likes.label("likes")
        )
        .select_from(m)
        .join(movie_views, m.c.movie_id == movie_views.c.movie_id, isouter=True)
        .join(movie_ratings, m.c.movie_id == movie_ratings.c.movie_id, isouter=True)
        .join(movie_likes, m.c.movie_id == movie_likes.c.movie_id, isouter=True)
        .where(m.c.rank <= 5)
        .order_by(m.c.rank)
    )

    movies = []
    with db.engine.connect() as connection:
        result = connection.execute(stmt)
        for row in result:
            if all(value == None for value in row): # no data to analyze
                return movies
            movies.append(
                {
                    "movie_id": row.movie_id,
                    "movie_name": row.name,
                    "rank": row.rank,
                    "viewed": row.views,
                    "rated": row.movie_avg,
                    "liked": row.likes,
                }
            )
    return movies




