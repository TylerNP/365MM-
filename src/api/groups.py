from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, root_validator
#from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix = "/groups",
    tags = ["groups"],
    #dependencies=[Depends(auth.get_api_key)],
)

class new_group(BaseModel):
    group_name : str
    group_description : str
    group_interests : list[str]
    group_scores : list[int]

    @root_validator(pre=True)
    def check_lengths(cls, values):
        interests = values.get('group_interests', [])
        scores = values.get('group_scores', [])
        if len(interests) != len(scores):
            print(len(interests), " | ", len(scores))
            raise HTTPException(status_code=422, detail="Malformed data: group_interests and group_scores must be the same length")
        return values

@router.get("/{group_id}")
def get_group_info(group_id : int):
    """
    Get the info about a group
    """
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
                ARRAY_AGG(genres.name) AS interests
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
    """
    Create a new group with the user as owner 
    """

    with db.engine.begin() as connection:
        try:
            sql_to_execute = "SELECT 1 FROM users WHERE users.id = :user_id"
            connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id}).scalar_one()
            sql_to_execute = "INSERT INTO groups (name, description) VALUES (:name, :description) RETURNING groups.id"
            group_id = connection.execute(sqlalchemy.text(sql_to_execute), {"name":group.group_name, "description":group.group_description}).scalar_one()
        except sqlalchemy.exc.NoResultFound:
            raise HTTPException(status_code=404, detail="User does not exist")
        except sqlalchemy.exc.IntegrityError:
            raise HTTPException(status_code=409, detail="Group name already exists")
        sql_to_execute = """
            INSERT INTO 
                liked_genres_groups (group_id, genre_id, score) 
            SELECT 
                :group_id,
                genres.id,
                match.score
            FROM 
                genres 
            JOIN 
                (SELECT UNNEST(:genres) AS name, UNNEST(:scores) AS score) AS match ON genres.name = match.name
            RETURNING id
        """
        results = connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id, "genres":group.group_interests, "scores":group.group_scores})
        ids = [result.id for result in results]
        if len(ids) < len(group.group_interests):
            raise HTTPException(status_code=422, detail="interests must match genres in database")
        sql_to_execute = "INSERT INTO groups_joined (user_id, group_id, role) VALUES (:user_id, :group_id, 'Owner')"
        connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id, "user_id":user_id})
    return {"group_id":group_id}

@router.post("/{group_id}/join/")
def join_group(group_id : int, user_id : int):
    """
    Add a user to a group
    """
    with db.engine.begin() as connection:
        sql_to_execute = "INSERT INTO groups_joined (user_id, group_id, role) VALUES (:user_id, :group_id, 'Member')"
        try:
            connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id, "user_id":user_id})
        except sqlalchemy.exc.IntegrityError:
            raise HTTPException(status_code=409, detail="user already a member of this group")

@router.delete("/{group_id}/user/{user_id}")
def remove_from_group(group_id : int, user_id : int):
    """
    Remove a user form a group
    """
    with db.engine.begin() as connection:
        sql_to_execute = "DELETE FROM groups_joined WHERE group_id = :group_id AND user_id = :user_id"
        connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id, "user_id":user_id})
    return HTTPException(status_code=200, detail="Removed user")

@router.delete("/{group_id}/")
def delete_group(group_id : int, user_id : int):
    """
    Delete a group (only owners can)
    """
    with db.engine.begin() as connection:
        try:
            sql_to_execute = """
                SELECT 1 
                FROM users 
                JOIN groups_joined 
                    ON users.id = groups_joined.user_id AND groups_joined.role = 'Owner'
                WHERE users.id = :user_id
            """
            connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id}).scalar_one()
        except sqlalchemy.exc.NoResultFound:
            raise HTTPException(status_code=403, detail="Invalid Authorization")
        sql_to_execute = "DELETE FROM groups WHERE groups.id = :group_id"
        connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id})
    return HTTPException(status_code=200, detail="Removed group")

@router.get("/list/")
def list_groups():
    """
    List all groups
    """
    result = None
    with db.engine.begin() as connection:
        sql_to_execute = """
            WITH members AS (
                SELECT 
                    groups.id,
                    COUNT(groups_joined.group_id) AS members
                FROM 
                    groups
                JOIN 
                    groups_joined ON groups.id = groups_joined.group_id
                GROUP BY
                    groups.id
            )
            SELECT 
                groups.id,
                groups.name, 
                groups.description, 
                COALESCE(members.members, 0) AS member,
                ARRAY_AGG(genres.name) AS interests
            FROM 
                groups 
            LEFT JOIN
                liked_genres_groups ON groups.id = liked_genres_groups.group_id
            LEFT JOIN
                genres ON liked_genres_groups.genre_id = genres.id
            LEFT JOIN
                members ON groups.id = members.id
            GROUP BY
                groups.name,
                groups.description,
                members.members,
                groups.id
            ORDER BY 
                groups.name
        """
        result = connection.execute(sqlalchemy.text(sql_to_execute))

    groups = []
    for value in result:
        groups.append(
            {
                "group_id":value.id,
                "group_name":value.name,
                "group_description":value.description,
                "members":value.member,
                "group_interests":value.interests
            }
        )
    return groups