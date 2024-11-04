from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
#from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix = "/groups",
    tags = ["groups"],
    #dependencies=[Depends(auth.get_api_key)],
)

class new_group(BaseModel):
    group_name = "string"
    group_description = "string"
    group_inerests = ["string"]
    group_scores = ["integer"]

@router.get("/{group_id}")
def get_group_info(group_id : int):
    sql_to_execute = "SELECT 1 FROM groups WHERE groups.id = :group_id"
    values = {"group_id":group_id}
    with db.engine.begin() as connection:
        try:
            connection.execute(sqlalchemy.text(sql_to_execute), values).scalar_one()
        except sqlalchemy.exc.NoResultFound:
            raise HTTPException(status_code=404, detail="No such group exists")
        sql_to_execute = """
            SELECT 
                groups.name, 
                groups.description, 
                ARRAY_AGG(genres.id) AS interests
            FROM 
                groups 
            JOIN
                liked_genres_groups ON groups.id = liked_genres_groups.group_id
            JOIN
                genres ON liked_genres_groups.genre_id = genres.id
            WHERE 
                groups.id = :group_id
            GROUP BY
                groups.name,
                groups.description
        """
        result = connection.execute(sqlalchemy.text(sql_to_execute), values)

    group = {}
    for row in result:
        group["name"] = row.name
        group["description"] = row.description
        group["interests"] = row.interests
    
    return group

@router.post("/new/{user_id}")
def create_group(group : new_group, user_id : int):
    if len(group.group_scores) != len(group.group_inerests):
        raise HTTPException(status_code=400, detail="Invalid Format")
    with db.engine.begin() as connection:
        try:
            sql_to_execute = "SELECT 1 FROM users WHERE users.id = :user_id"
            connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id}).scalar_one()
            sql_to_execute = "INSERT INTO groups (name, description) VALUES (:name, :description) RETURNING groups.id"
            group_id = connection.execute(sqlalchemy.text(sql_to_execute), {"name":group.group_name, "description":group.group_description}).scalar_one()
        except sqlalchemy.exc.NoResultFound:
            print("No user to create group from")
            return {}
        except sqlalchemy.exc.IntegrityError:
            print("Group name already exists")
            return {}
        sql_to_execute = """
            INSERT INTO 
                liked_genres_groups (group_id, genre_id, score) 
            SELECT 
                :group_id,
                genres.id,
                match.score
            FROM 
                genres 
            JOIN (SELECT UNNEST(:genres) AS name, UNNEST(:scores)::int AS score) AS match ON genres.name = match.name
        """
        connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id, "genres":group.group_inerests, "scores":group.group_scores})
        sql_to_execute = "INSERT INTO groups_joined (user_id, group_id, role) VALUES (:user_id, :group_id, 'Owner')"
        connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id, "user_id":user_id})
    return {"group_id":group_id}

@router.post("/{group_id}/join/{user_id}")
def join_group(group_id : int, user_id : int):
    return "OK"

@router.post("/{group_id}/remove/{user_id}")
def remove_from_group(group_id : int, user_id : int):
    return "OK"

@router.post("/{group_id}/delete/{user_id}")
def delete_group(gro):
    return "OK"

@router.get("/list/")
def list_groups():
    return "OK"