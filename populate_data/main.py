import csv 
import os
import os.path
import StringIO

path = '/Users/taran/Downloads/archive/movies_metadata.csv'

movies = []
with open(path, "r") as file:
    csv_reader = csv.reader(file) 
    for i, row in enumerate(csv_reader):
        movie = []
        if i == 1:
            movie.append(row[20]) # Name was 8
            movie.append(row[14]) # Date
            movie.append(row[3]) # Genres
            movie.append(0) # avg rating
            movie.append(row[2]) # Budget
            movie.append(row[15]) # Box office
            movie.append([])
            # for e in row:
            #     print(e)
            # Movie
            # movies.append()
            break


with open("/Users/taran/CSC365/365MM-/populate_data/main.py", "w") as file:
    writer = csv.writer(file)
    writer.writerows(movies)


class Movie():
    name: str
    release_year: int
    genres: list[str]
    average_rating: int
    budget: int
    box_office: int
    demographic: list[str]



"""

with open(path, "r") as file:
    csv_reader = csv.reader(file) 
    for i, row in enumerate(csv_reader):
        movie = []
        if i == 1:
            print(row[20]) # Name was 8
            print(row[14]) # Date
            print(row[3]) # Genres
            print(0) # avg rating
            print(row[2]) # Budget
            print(row[15]) # Box office
            print([])
            # for e in row:
            #     print(e)
            # Movie
            # movies.append()
            break
            
"""