### Example Flows

#### ALREADY WATCHED A MOVIE
##### Already watched from recommended movies

###### Taran
Rupinder Singh logs in by making a POST request to `/users/login`. Rupinder then gets recommended movies where he likes "Toy Story" and decides to watch it. He decideds to rate the movie a 10 out of 10 with a POST request to `/users/{id}/list/{movie_id}/rate` and then makes a POST request to `/movies/{id}/list/{movie_id}/` with that movie's id in the request URL. 

Rupinder starts by calling POST `/users/login` to log in.
Then Rupinder calls GET `/recommendations/{user_id}` to get his recommended movies
Rupinder calls POST `/users/{id}/list/{movie_id}/rate`  with the movie he has already seen.
Finally, he then makes call to POST `/users/{id}/list/{movie_id}/watched`, where the movie_id is the id of the movie he has seen"


#### GET A MOVIE TO WATCH TODAY
Rakesh had a long day and wants to watch a movie. He is too tired to think of a movie. Rakesh first logs in by making a POST request to `/users/login`. He then makes a GET request to `/movies/user/{user_id}/` which returns a new movie that he has not already watched. He wants to know more about the movie so he calls `/analytcs/movies/{movie-id}`

Rakesh starts by calling POST `/users/login` to log in.
He then makes a GET request to `/movies/user/{user_id}/` where he is given a movie to watch
Rakesh then enjoys the rest of his day by watching the new movie and wants to see how it performed `/analytics/movies/{movie_id}`ven a movie to watch
Rakesh then enjoys the rest of his day by watching the new movie

##### Already watched from watching a movie
John Smith just watched Toy Story in the theatres. He goes on 365MM and searches for the movie he just watched. He adds it to his list of liked movies and wants to see how it will perform. 

He calls SEARCH and inputs the movie he just watched by calling `/catalog/search`
If he liked the movie, He calls ADD to his movie list with `/users/{user_id}/add/{movie_id}/`
Afterwards he checks the predictions on the movie with `/predictions/{movie_id}`


# Additional Flows
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
