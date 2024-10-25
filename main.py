'''
    Get a movie to watch today.
    - Signup / Login (passoword table that we hash)
    - Get movies that are not on the watched table for the user (fixed amount)    (just a simple random query from movies not watched)
'''


# If username is already in the table, tell them to pick a new username
# If username is not in the table when logging, tell user to sign up 

# Join not exsist in watched table for that user

import uvicorn

if __name__ == "__main__":
    config = uvicorn.Config(
        "src.api.server:app", port=3000, log_level="info", reload=True, env_file=".env"
    )
    server = uvicorn.Server(config)
    server.run()



# from fastapi import FastAPI

# app = FastAPI()
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

