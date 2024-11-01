import csv 
import ast
import parameter
from datetime import datetime
import os 
import dotenv
import sqlalchemy
from sqlalchemy import create_engine

"""
# Data Obtained From Kaggle Movie Dataset
# https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset?resource=download
"""
def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)

def format_date(string_date : str) -> datetime:
    format_date = "%Y-%m-%d %H:%M:%S"
    date = None
    try:
        date = datetime.strptime(string_date, format_date)
    except :
        string_date_timestamp = string_date +  " 00:00:00"
        date = datetime.strptime(string_date_timestamp, format_date)
    return date

#Generate CSVs For DB
def cleaned_csvs(max_read : int):
    movies = []
    genres_joined = []
    missing = 0
    genre_ids = {}
    with engine.begin() as connection:
        results = connection.execute(sqlalchemy.text("SELECT id, name FROM genres"))
        for result in results:
            genre_ids[result.name] = result.id

    with open(parameter.path, "r", encoding='utf-8') as file:
        csv_reader = csv.reader(file) 
        headers = next(csv_reader)
        header_indices = {header: index for index, header in enumerate(headers)}
        seen = set()
        movie_id = 1
        for i, row in enumerate(csv_reader):
            if i > max_read:
                break
            movie = {}
            genres = []
            try:
                movie["id"] = movie_id
                movie["name"] = row[header_indices["title"]] 
                movie["description"] = row[header_indices["overview"]]
                movie["release_date"] = format_date(row[header_indices["release_date"]])
                movie["budget"] = row[header_indices["budget"]] 
                movie["box_office"] = row[header_indices["revenue"]] 
                genre_info = ast.literal_eval(row[header_indices["genres"]])
                for info in genre_info:
                    genres.append(info["name"])
            except:
                missing += 1
                print(f"{i}: is missing data or malformed")
                continue
            #Uniqueness check of db table
            if (movie["name"]+str(movie["release_date"])+str(genres)+movie["description"]) in seen:
                missing += 1
                print(f"{i}: is a duplicate")
                continue
            for genre in genres:
                genres_joined.append({"movie_id":movie_id, "genre_id":genre_ids[genre]})

            movie_id += 1
            movies.append(movie)
            seen.add(movie["name"]+str(movie["release_date"])+str(genres)+movie["description"])


    print(f"{missing} rows removed")

    header = ["id", "name", "release_date", "budget", "box_office", "description"]
    with open(parameter.movie_path, "w", newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(movies)

    header = ["movie_id", "genre_id"]
    with open(parameter.genre_path, "w", newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(genres_joined)

if __name__ == "__main__":
    max = float('inf')
    cleaned_csvs(max)
