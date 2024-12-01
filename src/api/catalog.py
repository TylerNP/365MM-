from fastapi import APIRouter, HTTPException
#from pydantic import BaseModel
#from src.api import auth
import sqlalchemy
from src import database as db
from enum import Enum

router = APIRouter(
    prefix="/catalog",
    tags=["catalog"],
)

class SearchSortOptions(str, Enum):
    movie_name = "movie_name"
    genre = "genre"
    director = "director"
    actor = "actor"
    year = "year"
    rating = "rating"

class SearchSortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("/search")
async def search_movies(
    movie_name: str = "",
    genre: str = "",
    director: str = "",
    actor: str = "",
    year: int = None,
    rating: int = None,
    search_page: int = 1,
    limit: int = 10,
    sort_col: SearchSortOptions = SearchSortOptions.movie_name,
    sort_order: SearchSortOrder = SearchSortOrder.asc,
):
    if limit < 1:
        raise HTTPException(status_code=422, detail="limit must be a positive number greater than zero")
    elif search_page < 1:
        raise HTTPException(status_code=422, detail="search_page must be a positive number greater than zero")
    offset = (search_page - 1) * limit
    
    # Define ordering based on sort_col
    if sort_col == SearchSortOptions.movie_name:
        order_by = db.movies.c.name
    elif sort_col == SearchSortOptions.genre:
        order_by = db.genres.c.name
    elif sort_col == SearchSortOptions.director:
        order_by = db.cast_and_crew.c.lastname  # assuming directors are in the cast_and_crew table
    elif sort_col == SearchSortOptions.actor:
        order_by = db.cast_and_crew.c.lastname
    elif sort_col == SearchSortOptions.year:
        order_by = db.movies.c.release_date
    elif sort_col == SearchSortOptions.rating:
        order_by = db.movies.c.average_rating
    else:
        assert False

    # Apply ascending or descending order
    if sort_order == SearchSortOrder.desc:
        order_by = sqlalchemy.desc(order_by)

    # Base query selecting from movies table and related columns
    stmt = (
        sqlalchemy.select(
            db.movies.c.id.label("movie_id"),
            db.movies.c.name.label("movie_name"),
            db.movies.c.release_date.label("movie_release_year"),
            sqlalchemy.func.coalesce(db.movies.c.average_rating,0).label("movie_average_rating"),
            sqlalchemy.func.array_agg(db.genres.c.name).label("movie_genre")
        )
        .select_from(db.movies)
        .join(db.movie_genres, db.movies.c.id == db.movie_genres.c.movie_id)
        .join(db.genres, db.movie_genres.c.genre_id == db.genres.c.id)
        .group_by(db.movies.c.id)
        .limit(limit)
        .offset(offset)
        .order_by(order_by, db.movies.c.id)
    )

    # Filtering conditions
    if movie_name:
        stmt = stmt.where(db.movies.c.name.ilike(f"%{movie_name}%"))
    if genre:
        stmt = stmt.where(db.genres.c.name.ilike(f"%{genre}%"))
    if director:
        stmt = stmt.join(db.roles, db.movies.c.id == db.roles.c.movie_id) \
                   .join(db.cast_and_crew, db.roles.c.cast_id == db.cast_and_crew.c.id) \
                   .where(db.roles.c.role == "director") \
                   .where(db.cast_and_crew.c.lastname.ilike(f"%{director}%"))
    if actor:
        stmt = stmt.join(db.roles, db.movies.c.id == db.roles.c.movie_id) \
                   .join(db.cast_and_crew, db.roles.c.cast_id == db.cast_and_crew.c.id) \
                   .where(db.roles.c.role == "actor") \
                   .where(db.cast_and_crew.c.lastname.ilike(f"%{actor}%"))
    if year:
        stmt = stmt.where(sqlalchemy.extract('year', db.movies.c.release_date) == year)
    if rating:
        stmt = stmt.where(db.movies.c.average_rating >= rating)

    # Executing the query
    movies = []
    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        for row in result:
            movies.append(
                {
                    "movie_id": row.movie_id,
                    "movie_name": row.movie_name,
                    "movie_release_year": row.movie_release_year,
                    "movie_genre": row.movie_genre,
                    "movie_average_rating": row.movie_average_rating,
                }
            )

    # Creating pagination links
    previous = f"/catalog/search?search_page={search_page - 1}" if search_page > 1 else ""
    next = f"/catalog/search?search_page={search_page + 1}" if len(movies) == limit else ""

    return {
        "previous": previous,
        "next": next,
        "results": movies
    }
