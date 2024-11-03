import os 
import dotenv
import sqlalchemy
from sqlalchemy import create_engine

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)

metadata_obj = sqlalchemy.MetaData()
movies = sqlalchemy.Table("movies", metadata_obj, autoload_with=engine)
roles = sqlalchemy.Table("roles", metadata_obj, autoload_with=engine)
movie_genres = sqlalchemy.Table("movie_genres", metadata_obj, autoload_with=engine)
cast_and_crew = sqlalchemy.Table("cast_and_crew", metadata_obj, autoload_with=engine)
genres = sqlalchemy.Table("genres", metadata_obj, autoload_with=engine)
    