
def format_movie_with_agg(movie_result) -> dict[str, any]:
    movie = {}
    movie["movie_id"] = movie_result[0]
    movie["name"] = movie_result[1]
    movie["release_date"] = movie_result[2]
    movie["description"] = movie_result[3]
    movie["average_rating"] = movie_result[4]
    movie["budget"] = movie_result[5]
    movie["box_office"] = movie_result[6]
    movie["genre"] = movie_result[7]
    movie["language"] = movie_result[8]
    return movie

# Takes CursorResult Object And Converts into a list of Movie Dictionary For Json
def format_movies(movie_result : object) -> list[dict[str, any]]:
    movies = []
    for info in movie_result:
        movie = {}
        movie["movie_id"] = info.id
        movie["name"] = info.name
        movie["release_date"] = info.release_date
        movie["description"] = info.description
        movie["average_rating"] = info.average_rating
        movie["budget"] = info.budget
        movie["box_office"] = info.box_office
        movies.append(movie)
        # movie["demographic"] = info.demographic
    return movies

