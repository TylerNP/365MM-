from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
#from src.api import auth
import sqlalchemy
from src import database as db

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

@router.get("/login")
def user_login(username : str):
    user_id = 0
    with db.engine.begin() as connection:
        set = 'SELECT users.id FROM users WHERE users.username = :username'
        try:
            user_id = connection.execute(sqlalchemy.text(set), {"username":username}).scalar_one()
        except sqlalchemy.exc.NoResultFound:
            raise HTTPException(status_code=404, detail="No User Found")
    return {
        "user_id":user_id
    }

# Takes CursorResult Object And Creates A List of Dictionaries For JSON 
def format_movie(movie_result : object, output : list[dict[str,any]]) -> None:
    for info in movie_result:
        movie = {}
        movie["movie_id"] = info.id
        movie["name"] = info.name
        movie["release_date"] = info.release_date
        movie["description"] = info.description
        movie["average_rating"] = info.average_rating
        movie["budget"] = info.budget
        movie["box_office"] = info.box_office
        # movie["demographic"] = info.demographic
        output.append(movie)

@router.post("/{user_id}/add/{movie_id}")
def user_add_movie(user_id : int, movie_id : int):
    """
    Record a movie a user has saved
    """
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
        except sqlalchemy.exc.DataError:
            raise HTTPException(status_code=400, detail="Malformed request")
    return {
        "success":True
    }

@router.get("/{user_id}/list")
def user_list(user_id : int):
    """
    List all the movies a user has saved
    """
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
        
    return list_movies

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

@router.post("/{user_id}/like/{movie_id}")
def user_like_movie(user_id : int, movie_id : int, like : bool):
    """
    Like a movie for a specific user
    """
    # Add Check For Movie and User IDs To Ensure They Exists
    with db.engine.begin() as connection:
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
    return {
        "success":True
    }
