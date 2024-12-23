from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, root_validator
#from src.api import auth
import time
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
    start_time = time.time()
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
            LEFT JOIN
                liked_genres_groups ON groups.id = liked_genres_groups.group_id
            LEFT JOIN
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
        group["interests"] = row.interests if row.interests[0] != None else ["N/A"]
    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} s")
    return group

@router.post("/new/{user_id}")
def create_group(group : new_group, user_id : int):
    """
    Create a new group with the user as owner 
    """
    start_time = time.time()
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
    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} s")
    return {"group_id":group_id}

@router.post("/{group_id}/join/{user_id}")
def join_group(group_id : int, user_id : int):
    """
    Add a user to a group
    """
    start_time = time.time()
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT 1 FROM groups WHERE id = :group_id"
        try:
            # test if group exists
            if not len(list(connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id}))):
                raise HTTPException(status_code=409, detail="group does not exist")
            sql_to_execute = "SELECT user_id FROM groups_joined WHERE group_id = :group_id"
            users = list(connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id}))
            # check if there is another user and make that person the new owner 
            if len(users):
                role = "Member"
            else:
                role = "Owner"
            sql_to_execute = "INSERT INTO groups_joined (user_id, group_id, role) VALUES (:user_id, :group_id, :role)"
            connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id, "user_id":user_id, "role": role})
        except sqlalchemy.exc.IntegrityError:
            raise HTTPException(status_code=409, detail="user already a member of this group")
    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} s")
    return HTTPException(status_code=201, detail="Joined Group")

@router.delete("/{group_id}/user/{user_id}")
def remove_from_group(group_id : int, user_id : int):
    """
    Remove a user form a group
    """
    start_time = time.time()
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT count(1) FROM groups_joined WHERE group_id = :group_id and user_id = :user_id"
        exists = connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id, "user_id":user_id}).scalar()
        print(exists)
        if not exists:
            raise HTTPException(status_code=409, detail="user is not a member of this group")
        sql_to_execute = "DELETE FROM groups_joined WHERE group_id = :group_id AND user_id = :user_id"
        connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id, "user_id":user_id})
        sql_to_execute = "SELECT user_id FROM groups_joined WHERE group_id = :group_id ORDER BY created_at DESC LIMIT 1"
        try:
            user_id = connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id}).scalar_one()
        # check if there is another user and make that person the new owner 
        except sqlalchemy.exc.NoResultFound:
            sql_to_execute = "UPDATE groups_joined SET role = 'Owner' WHERE groups_joined.user_id = :user_id"
            connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id, "user_id":user_id})

    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} s")
    return HTTPException(status_code=200, detail="Removed user")

@router.delete("/{group_id}/")
def delete_group(group_id : int, user_id : int):
    """
    Delete a group (only owners can)
    """
    start_time = time.time()
    with db.engine.begin() as connection:
        try:
            sql_to_execute = """
                SELECT 1 
                FROM users 
                JOIN groups_joined 
                    ON users.id = groups_joined.user_id AND groups_joined.role = 'Owner'
                WHERE users.id = :user_id AND groups_joined.group_id = :group_id
            """
            connection.execute(sqlalchemy.text(sql_to_execute), {"user_id":user_id, "group_id":group_id } ).scalar_one()
        except sqlalchemy.exc.NoResultFound:
            raise HTTPException(status_code=403, detail="Invalid Authorization")
        sql_to_execute = "DELETE FROM groups WHERE groups.id = :group_id"
        connection.execute(sqlalchemy.text(sql_to_execute), {"group_id":group_id})
    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} s")
    return HTTPException(status_code=200, detail="Removed group")

@router.get("/list/")
def list_groups(search_page: int = 1, limit: int = 10):
    """
    List all groups
    """
    start_time = time.time()
    if limit < 1:
        raise HTTPException(status_code=422, detail="limit must be a positive number greater than zero")
    elif search_page < 1:
        raise HTTPException(status_code=422, detail="search_page must be a positive number greater than zero")
    offset = (search_page - 1) * limit
    #result = None
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
            OFFSET 
                :offset
            LIMIT 
                :limit
        """
        result = connection.execute(sqlalchemy.text(sql_to_execute), {"offset":offset, "limit":limit})

    groups = [
            {
                "group_id":value.id,
                "group_name":value.name,
                "group_description":value.description,
                "members":value.member,
                "group_interests":value.interests if value.interests[0] != None else ["N/A"]
            } for value in result 
        ]
    
    end_time = time.time()
    print(f"Took {round(end_time-start_time,4)} s")
    return groups