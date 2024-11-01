from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix = "/recommendations",
    tags = ["recommendations"],
)

@router.get("/{user_id}")
def get_recommended(user_id: int):
    pass

@router.post("/{user_id}/reset/")
def reset_recommended():
    return NotImplemented

@router.post("/{user_id}/delete/{movie_id}")
def delete_recommendation():
    return NotImplemented

@router.post("/{user_id}/generate/")
def generate_recommendation():
    return NotImplemented

@router.post("/{user_id}/collab/")
def generate_recommendation_collab():
    return NotImplemented

"""
    https://pyimagesearch.com/2023/06/19/fundamentals-of-recommendation-systems/
    Try To Create Simple Recommendation Engine 

    Content (CONS -> No Info On New Users/ Very  Specialized Results)
        -> Use User's Likes/Dislikes of Specific Features To Get A Vector of User Likes/Dislikes
        -> Create a Vector of Same Features For Movies
        -> Take Dotproduct/ (Normal of User * Normal of Movie) FOr Score
    Collaborative (CONS -> No Ratings On Movies = Bad Recommendation, Hard To Identify Most Similar Users)
        -> Find Similar Users that Already Rated a Movie
        -> Use this to Score Movies to Reocmmend 
"""