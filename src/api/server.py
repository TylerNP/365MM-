from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import users, groups, catalog, analytics, admin, movies, predictions, recommendations
import json
import logging
import sys
from starlette.middleware.cors import CORSMiddleware

description = """
                365MM is the premier movie database for all your movies desires.
            """

app = FastAPI(
    title="365MM",
    description=description,
    version="2.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "N/A",
        "email": "N/A",
    },
)

# ? when deploying put app domain here
#origins = ["https://potion-exchange.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    #allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(users.router)
# app.include_router(catalog.router)
# app.include_router(groups.router)
# app.include_router(catalog.router)
# app.include_router(analytics.router)
app.include_router(movies.router)
# app.include_router(admin.router)
# app.include_router(predictions.router)
app.include_router(recommendations.router)


@app.exception_handler(exceptions.RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response['message'].append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)

@app.get("/")
async def root():
    return {"message": "Welcome to 365MM"}
