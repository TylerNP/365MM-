import os
import dotenv 

from sqlalchemy import create_engine


def database_connecgtion_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connecgtion_url(), pool_pre_ping=True)