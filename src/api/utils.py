from typing import TypedDict, Tuple, Union, Protocol

class MovieDict(TypedDict):  
    movie_id: Union[int, str]
    name: str
    release_date: str 
    description: str
    average_rating: float
    budget: float
    box_office: float
    genre: str
    language: str

MovieResultType = Tuple[Union[int, str], str, str, str, float, float, float, str, str]
def format_movie_with_agg(movie_result : MovieResultType) -> MovieDict:
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

class MovieDictNoAgg(TypedDict):  
    movie_id: Union[int, str]
    name: str
    release_date: str 
    description: str
    average_rating: float
    budget: float
    box_office: float

class MovieProtocol(Protocol):
    id: int
    name: str
    release_date: str
    description: str
    average_rating: float
    budget: float
    box_office: float
    
# Takes CursorResult Object And Converts into a list of Movie Dictionary For Json
def format_movies(movie_result : list[MovieProtocol]) -> list[MovieDictNoAgg]:
    return (
        [
            {
                "movie_id": info.id,
                "name": info.name,
                "release_date": info.release_date,
                "description": info.description,
                "average_rating": info.average_rating,
                "budget": info.budget,
                "box_office": info.box_office
                # movie["demographic"] = info.demographic
            } for info in movie_result
        ]
    )


