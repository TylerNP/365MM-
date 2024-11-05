###### Get Movie To Watch And Save
Rupinder Singh logs in by making a POST request to `/users/login`. Rupinder then gets recommended movies where he likes "Toy Story" and decides to watch it. He decideds to rate the movie a 10 out of 10 with a POST request to `/users/{id}/list/{movie_id}/rate` and then makes a POST request to `/movies/{id}/list/{movie_id}/` with that movie's id in the request URL. 

Rupinder starts by calling POST `/users/login` to log in.
Then Rupinder calls GET `/recommendations/{user_id}` to get his recommended movies
Rupinder calls POST `/users/{id}/list/{movie_id}/rate`  with the movie he has already seen.
Finally, he then makes call to POST `/users/{id}/list/{movie_id}/watched`, where the movie_id is the id of the movie he has seen"

# Testing Results

1. `/users/login`
**Request**
curl -X 'GET' \
  'https://three65mm.onrender.com/users/login?username=Rupinder' \
  -H 'accept: application/json' 

**Response**
{
  "user_id": 24
} 
2. `/recommendations/24`
**Request**
curl -X 'GET' \
  'http://127.0.0.1:3000/recommendations/24' \
  -H 'accept: application/json'

**Response**
[
    {
        "movie_id":1,
        "name":"Toy Story",
        "release_date": "1995-10-30 00:00:00+00",
        "average_rating":null,
        "budget": 30000000,
        "box_office":373554033,
        "genre": [
            "Animation",
            "Comedy",
            "Family"
        ]
        "language": [
            "English"
        ]
    },
    {
        "movie_id":4,
        "name":"Waiting to Exhale",
        "release_date": "1995-12-22 00:00:00+00",
        "average_rating":null,
        "budget": 16000000,
        "box_office":81452156,
        "genre": [
            "Comedy",
            "Romance",
            "Drama"
        ]
        "language": [
            "English"
        ]
    }
]
3. `/users/24/rate/1`
**Request**
curl -X 'POST' \
  'http://127.0.0.1:3000/users/4/rate/1?rating=10' \
  -H 'accept: application/json' \
  -d ''

**Response**
{
  "success": true
}

4. `/users/24/watch/1`
**Request**
curl -X 'POST' \
  'http://127.0.0.1:3000/users/24/watch/1' \
  -H 'accept: application/json' \
  -d ''

**Response**
{
  "success": true
}

#### GET A MOVIE TO WATCH TODAY
Rakesh had a long day and wants to watch a movie. He is too tired to think of a movie. Rakesh first logs in by making a POST request to `/users/login`. He then makes a GET request to `/movies/user/{user_id}/` which returns a movie that he has not already watched, but has shown intrest in from past recomendations. Rakesh then deciedes to watch that movie. 

Rakesh starts by calling POST `/users/login` to log in.
He then makes a GET request to `/movies/user/{user_id}/` where he is given a movie to watch
Rakesh then enjoys the rest of his day by watching the new movie

# Testing Results

1. `/users/login`
**Request**
curl -X 'GET' \
  'https://three65mm.onrender.com/users/login?username=Rakesh' \
  -H 'accept: application/json' 

**Response**
{
  "user_id": 23
} 
2. `/movies/user/23/`
**Request**
curl -X 'GET' \
  'https://three65mm.onrender.com/movies/user/23' \
  -H 'accept: application/json' 

**Response**
{
  "movie_id": 3,
  "name": "Grumpier Old Men",
  "release_date": "1995-12-22T00:00:00+00:00",
  "description": "",
  "average_rating": 0,
  "budget": 0,
  "box_office": 0,
}

##### Already watched from watching a movie
###### Taran (movie not found if not there) (search by title and genre or or them)
John Smith just watched a new movie in the theatres. He really enjoyed this movie and would like to see similar movies. He goes on (our project) and searches for the movie he just watched. He adds it to his list of liked movies and rates it from 1-10. John then requests to see movies like the one he just likes and rated.

John starts by logging into or signing up for an account 
He calls SEARCH and inputs the movie he just watched.
If he liked the movie, He calls ADD to his liked movie list with his rating.
He decides he would like to see which movies are similar to the movie he just watched so he calls RECOMMEND

#### Advanced search feature
Jane, a user who wants to see a movie but doesn’t know the movie title, wants to search for the movie using the director(which she knows).

She first signs up with a POST request to `/users/signup`. She then searches for the director’s movies with a GET request to `/catalog/search?director=thebestdirector`. She then looks at one she likes with a GET request to `/movies/:id`.
She now has all the info she needs to watch the movie.


#### RATE MOVIES THAT ARE NEW TO YOU
Jake is very bored and wants to try something differnt from his usual movie taste. First, Jake requests a catalog of movies that are differnt from the movies he likes with a GET request to `/recommend/{id}/random`. If Jake is a new user and doesn't have any liked films, he will get random films from the same endpoint. Jake can then rate specfic movies from the recieved catalog with a POST request to `/users/{id}/list{movie_id}/rate` with a number for how willing he is to watch the movie. If Jake really wants to watch a movie, he can add that movie to his watch list with a POST request to `/users/{id}/watch/{movie_id}`/


#### RECOMMENDATION FEATURE
Kade Cabrera visits our website because she wants to find other movies based off of her likes and dislikes. 
First, Kade requests the catalog of movies to find what she has watched with `/catalog/movies`. 
Kade rates movie, A, on her account with a POST request to `/users/{id}/list/{movie_id}/rate/` with a like and movie, B, with disklike. 
Kade then receives recommendations with a GET `/recommend/{id}`