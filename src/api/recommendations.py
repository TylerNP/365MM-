from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix = "/recommendations",
    tags = ["recommendations"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/{user_id}")
def get_recommended():
    return NotImplemented

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