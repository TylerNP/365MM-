from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix = "/predictions",
    tags = ["predictions"],
)

@router.get("/{movie_id}")
def get_prediction(movie_id : int):
    prediction = {}
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT predicted_ratings, predicted_views, box_office FROM predictions WHERE movie_id = :movie_id"
        try:
            results = connection.execute(sqlalchemy.text(sql_to_execute), {"movie_id":movie_id})
        except sqlalchemy.exc.NoResultFound:
            print("No prediction yet")
        for result in results:
            prediction["predicted_ratings"] = result.predicted_ratings
            prediction["predicted_views"] = result.predicted_views
            prediction["box_office"] = result.box_office
    return prediction

@router.post("/generate/")
def create_prediction(movie_id : int):
    return "OK"