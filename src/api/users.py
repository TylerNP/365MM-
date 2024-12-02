from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
#from src.api import auth
import sqlalchemy
import time
from src import database as db
from typing import Literal

router = APIRouter(
    prefix = "/users",
    tags = ["users"],
    #dependencies=[Depends(auth.get_api_key)],
)

class user(BaseModel):
    username: str

@router.post("/signup")
def user_signup(new_user : user):
    """
    Create a new user with a given username
    Rejects duplicate usernames
    """
    start_time = time.time()
    # USE UNIQUENESS CONSTRAINT With Try Block TO Detect Bad Inputs
    new_user.username = new_user.username.replace(" ", "")
    if not new_user.username or new_user.username == "":
        raise HTTPException(status_code=400, detail="Invalid Username") 
    sql_to_execute = """
                        INSERT INTO users (username)
                        VALUES (:username)
                    """
    with db.engine.begin() as connection:
        try:
            connection.execute(sqlalchemy.text(sql_to_execute), {"username":new_user.username})
        except sqlalchemy.exc.IntegrityError:
            print("Username Already Exists")
            raise HTTPException(status_code=409, detail="Username already in use")
    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} ms")
    return HTTPException(status_code=201, detail="New user added")

@router.post("/login")
def user_login(username : str):
    start_time = time.time()
    user_id = 0
    with db.engine.begin() as connection:
        set = 'SELECT users.id FROM users WHERE users.username = :username'
        try:
            user_id = connection.execute(sqlalchemy.text(set), {"username":username}).scalar_one()
        except sqlalchemy.exc.NoResultFound:
            raise HTTPException(status_code=404, detail="No User Found")
        
    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} ms")
    return {
        "user_id":user_id
    }


@router.post("/{user_id}/add/{movie_id}")
def user_add_movie(user_id : int, movie_id : int):
    """
    Record a movie a user has saved
    """
    start_time = time.time()
    # Add Check For Movie and User IDs To Ensure They Exists
    with db.engine.begin() as connection:
        sql_to_execute = """
                            INSERT INTO 
                                saved_movies (user_id, movie_id)
                            VALUES 
                                 (:user_id, :movie_id)
                        """
        try:
            connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id, "movie_id":movie_id})
        except sqlalchemy.exc.IntegrityError:
            print("Already Saved Movie")
            raise HTTPException(status_code=409, detail="Movie Already in list")
        except sqlalchemy.exc.DataError:
            raise HTTPException(status_code=400, detail="Malformed request")
        
    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} ms")
    return HTTPException(status_code=201, detail="Movie added to user list")

@router.get("/{user_id}/list")
def user_list(user_id : int):
    """
    List all the movies a user has saved
    """
    start_time = time.time()
    with db.engine.begin() as connection:
        try:
            sql_to_execute = "SELECT 1 FROM users WHERE users.id = :user_id"
            connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id}).scalar_one()
            sql_to_execute =  """
                SELECT 
                    movies.id, 
                    movies.name, 
                    movies.release_date,
                    movies.description,
                    movies.average_rating,
                    movies.budget,
                    movies.box_office, 
                    movies.duration 
                FROM 
                    movies
                JOIN  
                    saved_movies ON movies.id = saved_movies.movie_id 
                    AND saved_movies.user_id = :user_id 
            """
            results = list(connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id}))
        except sqlalchemy.exc.NoResultFound:
            raise HTTPException(status_code=404, detail="No User Found")
        results = connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id})
        
    list_movies = []
    for info in results:
        movie = {}
        movie["movie_id"] = info.id
        movie["name"] = info.name
        movie["release_date"] = info.release_date
        movie["description"] = info.description
        movie["average_rating"] = info.average_rating
        movie["budget"] = info.budget
        movie["box_office"] = info.box_office
        list_movies.append(movie)
        
    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} ms")
    return list_movies

@router.post("/{user_id}/rate/{movie_id}")
def user_rate_movie(user_id : int, movie_id : int, rating : Literal["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]):
    """
    Rate a movie for a specific user
    """
    start_time = time.time()
    rating = int(rating)
    # Add Check For Movie and User IDs To Ensure They Exists
    if rating < 1 or rating > 10:
        raise HTTPException(status_code=400, detail="Rating must be between 1 to 10")
    with db.engine.begin() as connection:
        validate_user_movie_ids(user_id, movie_id, connection)
        sql_to_execute = """
                            INSERT INTO 
                                ratings (user_id, movie_id, rating)
                            VALUES 
                                 (:user_id, :movie_id, :rating)
                        """
        try:
            connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id, "movie_id":movie_id, "rating":rating})
        except sqlalchemy.exc.IntegrityError:
            # ? To-Do Update query instead
            print("Already Rated Movie")
            raise HTTPException(status_code=409, detail="Movie Already Rated")
    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} ms")
    return HTTPException(status_code=201, detail="Movie rated")

@router.post("/{user_id}/watch/{movie_id}")
def user_watched_movie(user_id : int, movie_id : int):
    """
    Record a movie a user has watched
    """
    # Add Check For Movie and User IDs To Ensure They Exists
    start_time = time.time()
    with db.engine.begin() as connection:
        validate_user_movie_ids(user_id, movie_id, connection)
        sql_to_execute = """
                            INSERT INTO 
                                watched_movies (user_id, movie_id)
                            VALUES 
                                 (:user_id, :movie_id)
                        """
        try:
            connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id, "movie_id":movie_id})
        except sqlalchemy.exc.IntegrityError:
            print("Already Watched Movie")
            raise HTTPException(status_code=409, detail="Movie Already Watched")
    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} ms")
    return HTTPException(status_code=201, detail="Movie watched")

@router.post("/{user_id}/like/{movie_id}")
def user_like_movie(user_id : int, movie_id : int, like : bool):
    """
    Like a movie for a specific user
    """
    start_time = time.time()
    # Add Check For Movie and User IDs To Ensure They Exists
    with db.engine.begin() as connection:
        validate_user_movie_ids(user_id, movie_id, connection)
        sql_to_execute = """
                            INSERT INTO 
                                liked_movies (user_id, movie_id, liked)
                            VALUES 
                                 (:user_id, :movie_id, :like)
                        """
        try:
            connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id, "movie_id":movie_id, "like":like})
        except sqlalchemy.exc.IntegrityError:
            # ? To-Do Update query instead
            print("Already Rated Movie")
            raise HTTPException(status_code=409, detail="Movie Already liked/disliked")
        
    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} ms")
    return HTTPException(status_code=201, detail="Movie liked/disliked")

@router.delete("/{user_id}", status_code = 204)
def remove_user(user_id : int):
    start_time = time.time()
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("DELETE FROM users WHERE users.id = :user_id"), {"user_id":user_id})
    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} ms")
    return HTTPException(status_code=200, detail="User removed")

def validate_user_movie_ids(user_id : int, movie_id : int, connection) -> None:
    try:
        connection.execute(sqlalchemy.text("SELECT 1 FROM users WHERE users.id = :user_id"), {"user_id":user_id}).scalar_one()
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=404, detail="No user found")
    try:
        connection.execute(sqlalchemy.text("SELECT 1 FROM movies WHERE movies.id = :movie_id"), {"movie_id":movie_id}).scalar_one()
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=404, detail="No movie found")