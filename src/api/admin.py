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

@router.post("/{user_id}/movies/delete/{movie_id}")
def delete_movie(user_id : int, movie_id : int):
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT 1 FROM users WHERE users.id = :user_id AND users.is_admin = TRUE"
        try:
            connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id}).scalar_one()
        except sqlalchemy.exc.NoResultFound:
            raise HTTPException(status_code=403, detail="Invalid Authorization")
        sql_to_execute = "DELETE FROM movies WHERE id = :movie_id"
        connection.execute(sqlalchemy.text(sql_to_execute), {"movie_id":movie_id})
    return {"success": True}

@router.post("/{user_id}/group/delete/{group_id}")
def delete_group(user_id : int, group_id : int):
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT 1 FROM users WHERE users.id = :user_id AND users.is_admin = TRUE"
        try:
            connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id}).scalar_one()
        except sqlalchemy.exc.NoResultFound:
            raise HTTPException(status_code=403, detail="Invalid Authorization")
        sql_to_execute = "DELETE FROM groups WHERE id = :group_id"
        connection.execute(sqlalchemy.text(sql_to_execute), {"group_id": group_id})
    return {"success": True}