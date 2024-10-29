# Example Workflow
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
  "genres": "['Romance', 'Comedy']",
  "average_rating": 0,
  "budget": 0,
  "box_office": 0,
  "demographic": "[]"
}

