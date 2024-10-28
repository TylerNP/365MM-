from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix = "/users",
    tags = ["users"],
    dependencies=[Depends(auth.get_api_key)],
)

class user(BaseModel):
    username: str

@router.post("/signup")
def user_signup(new_user : user):
    """
    Create a new user with a given username
    Rejects duplicate usernames
    """
    # USE UNIQUENESS CONSTRAINT With Try Block TO Detect Bad Inputs
    sql_to_execute = """
                        INSERT INTO users (username)
                        VALUES (:username)
                    """
    with db.engine.begin() as connection:
        try:
            connection.execute(sqlalchemy.text(sql_to_execute), {"username":new_user.username})
        except sqlalchemy.exc.IntegrityError:
            print("Username Already Exists")
            return {
                "success":False,
            }
    return {
        "success":True
    }

@router.put("/login/{user_id}")
def user_login(username : str):
    user_id = 0
    with db.engine.begin() as connection:
        set = 'SELECT users.id FROM users WHERE users.username = :username'
        try:
            user_id = connection.execute(sqlalchemy.text(set), {"username":username}).scalar_one()
        except sqlalchemy.exc.IntegrityError:
            print("No User Exists With Given Username")
            return {"user_id": -1}
    return {
        "user_id":user_id
    }

@router.get("/{user_id}/list")
def user_list():
    return "ok"

@router.post("/{user_id}/rate/{movie_id}")
def user_rate_movie(user_id : int, movie_id : int, rating : int):
    """
    Rate a movie for a specific user
    """
    # Add Check For Movie and User IDs To Ensure They Exists
    with db.engine.begin() as connection:
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
    return {
        "success":True
    }

@router.post("/{user_id}/watch/{movie_id}")
def user_watched_movie(user_id : int, movie_id : int):
    """
    Record a movie a user has watched
    """
    # Add Check For Movie and User IDs To Ensure They Exists
    with db.engine.begin() as connection:
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
    return {
        "success":True
    }

