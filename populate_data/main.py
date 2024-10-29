import csv 
import ast
from datetime import datetime

"""
# Data Obtained From Kaggle Movie Dataset
# https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset?resource=download
"""
def format_date(string_date : str) -> datetime:
    format_date = "%Y-%m-%d %H:%M:%S"
    date = None
    try:
        date = datetime.strptime(string_date, format_date)
    except :
        string_date_timestamp = string_date +  " 00:00:00"
        date = datetime.strptime(string_date_timestamp, format_date)
    return date

path = r"C:\Users\123Ra\OneDrive\Documents\GitHub\365MM-\populate_data\archive\movies_metadata.csv"

max_read = float('inf')
movies = []
missing = 0

with open(path, "r", encoding='utf-8') as file:
    csv_reader = csv.reader(file) 
    headers = next(csv_reader)
    header_indices = {header: index for index, header in enumerate(headers)}
    for i, row in enumerate(csv_reader):
        if i > max_read:
            break
        movie = {}
        try:
            movie["name"] = row[header_indices["title"]] 
            movie["release_date"] = format_date(row[header_indices["release_date"]])
            genres = []
            genre_info = ast.literal_eval(row[header_indices["genres"]])
            for genre in genre_info:
                genres.append(genre["name"])
            movie["genres"] = genres
            movie["average_rating"] = 0 #Default Value
            movie["budget"] = row[header_indices["budget"]] 
            movie["box_office"] = row[header_indices["revenue"]] 
            movie["demographic"] = [] # Default
        except:
            missing = missing + 1
            print(f"{i} is missing data or malformed")
        movies.append(movie)

write_path = r"C:\Users\123Ra\OneDrive\Documents\GitHub\365MM-\populate_data\data.csv"
print(f"{missing} rows removed")

header = ["name", "release_date", "genres", "average_rating", "budget", "box_office", "demographic"]
with open(write_path, "w", newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=header)
    writer.writeheader()
    writer.writerows(movies)
