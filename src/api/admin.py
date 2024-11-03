from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
#from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix = "/admin",
    tags = ["admin"],
    #dependencies=[Depends(auth.get_api_key)],
)

@router.post("{user_id}/movies/delete/{movie_id}")
def delete_movie(user_id : int, movie_id : int):
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT 1 FROM users WHERE users.id = :user_id AND users.is_admin = TRUE"
        try:
            connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id}).scalar_one()
        except sqlalchemy.exc.NoResultFound:
            raise HTTPException(status_code=401, detail="Forbidden")
        sql_to_execute = "DELETE FROM movies WHERE id = :movie_id"
        connection.execute(sqlalchemy.text(sql_to_execute), {"movie_id":movie_id})
    return {"success": True}