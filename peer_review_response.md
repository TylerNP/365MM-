## Code Review Edits



## Adam Ta's Suggestions 

### Code Review Comments (Adam Ta) https://github.com/TylerNP/365MM-/issues/29
1. We intentionally took our SQL queries out of our sql alchemy statements under the thought process that our code would become more readable; however, we also see the validity in your point. 
2. I agree. This is now edited.
3. We have changed this block of code where a ternary is no longer appropriate.
`       
     if not movie:
            raise HTTPException(status_code=404, detail="No movie found")
    print(movie)
    return movie[-1]
`
4. I agree. This is also now edited. 
5. Custom typing is now implemented.
6.  The potential concurrency issue we see is reading from ratings twice, which might cause 2 different answers. This is technically not a big problem, as both reads are for 2 different recommendation algorithms. However, it is still a concurrency issue, so we have added a write lock on to the ratings table.
7. Snake case is now standard.
8. Spelling error has been fixed.
9. I have optimized this block of code. Now there is a single query called that handles the recommended movies (not using collaborative filtering) rather than 3 different queries called. 
10. Status codes have been added. 
11. "m = not" has been removed (because python is function scoped). The else has been replaced by the third condition, as, logically, there are only 3 options. 
12. We have pivoted to triple quotes rather than using `\`


### Schema/API Design comments (Adam Ta) https://github.com/TylerNP/365MM-/issues/28
1.  I like your idea. When we were deciding on picking names over ids, we thought it would introduce more complexity. An example would be a user trying to join a group called "group" but there are three groups named "group". Another example would be trying to find the movie "The Best Movie" but there are two other movies with that name. So we decided to stick with ids due to that reason. 
2. We pivoted this endpoint a bit. It would make sense to rename it from list to movies if the endpoint returned movies generally associated with a user (like liked and highly rated), but we decided to stick with list as it is more true to our vision: a list of saved movies. 
3. I agree with this and it has been changed. 
4. I agree with this as well and it has been changed. 
5. This is a table that is used to map users to groups and attribute a level of authority in that group (eg. Owner vs Member of the group)
6. We have decided to keep the current naming convention. However, I believe if we were starting from fresh, your proposed convention makes sense. 
7. "box-office" has been changed to "box_office".
8. We talked with Professor Pierce and he recommended not to do auth. However, I agree with changing the login endpoint to a post and that has been changed. 
9. I agree and we have made appropriate edits.
10. This is a valid concern. We have added a helper function that verifies the user_id and movie_id are valid on users endpoints. 
11. This is how our database is designed, we handle (i.e. send and receive) genres as arrays and then store many genres to one movie. 
12. I see. We are using demographic as language here. It is called demographic as we are open to making it multifaceted in the future. Currently there is no need to split it into another table; however we see how this makes sense if demographics encompassed more data. 


### Test results (Adam Ta) https://github.com/TylerNP/365MM-/issues/25
Failing:

1. When getting predictions on a movie that doesn't have predictions generated yet, an empty dictionary is returned. The /predictions/generate/{movie_id} endpoint must be called first to create predictions on said movie.
2. This endpoint might have been a little unclear. It is meant for administrators. We chose to manually make a user an administrator rather than having an endpoint to do so. Group_id is now returned as well.
New Test Cases:

1. There were less than 5 movies returned in the most popular movies (for likes) endpoint because there were less than 5 movies liked at the time. There is now more user data so that endpoint returns the appropriate amount. Movie names are now included.
2. For a user that has not rated any movies, we chose to recommend random movies rather than popular movies on purpose. Our thought process was that recommending random movies would be an opportunity for a new user to explore movies they might not have ever considered.
3. Recommendations are based on ratings rather than likes. We decided to use the more specific metric (ratings) to determine recommendations. A user's ratings are useful when we perform collaborative filtering.


### Product ideas (Adam Ta) #30 https://github.com/TylerNP/365MM-/issues/30
We have now implemented something similar to your second suggestion. We are using collaborative filtering when recommending movies. We think the first suggestion is neat; however it is not the scope we were going for with our application. 


## Alan Castillo
### Product ideas (Alan Castillo) https://github.com/TylerNP/365MM-/issues/35
We currently have something similar to your first suggestion. We are using collaborative filtering when recommending movies. I like your second idea. A trending page would make our application more unique and sensitive to time rather than something that's based on a single, growing snowball of data. However, this adds extra complexity to our application. 


## Edson Munoz's Suggestions 

## Code Review Comments (Edson Munoz) https://github.com/TylerNP/365MM-/issues/31
1. Done, this suggestion has been implemented
2. Writing simple queries in one unbroken line and longer queries in the traditional sense is fine. We will stick with this for consistency’s sake.
3. Thank you, but our queries only have a few parameters so, defining a separate dictionary might feel unnecessary and add extra lines of code.
4. We learned to use the query builder syntax for the search function for our potion search function, so this syntax is fine. 
5. Done, this suggestion has been implemented
6. Done, this suggestion has been implemented
7. The endpoint creates a prediction based on the user’s previous actions so we believe the name is fitting and shouldn’t cause confusion.
8. Done, this suggestion has been implemented
9. In this case, helper functions would hurt readability. We think relegating all of our search and filtering features to one function is efficient. 
10. The query builder automatically does parameter binding, so we are able to use a f string.
11. Done, this suggestion has been implemented
12. We think creating queries as needed is better for readability even if it's in the SQLalchemy call. 

## Product Ideas (Edson Munoz) https://github.com/TylerNP/365MM-/issues/34
These are good ideas, but our main focus is not groups. We do not plan on implementing them. 

## Test Results (Edson Munoz)  
**Existing:**
- Some endpoints are now under different names. So for your test of Example Flow 2, /analytics/{movie_id} would be used rather than /analytics/movies/{movie_id}.

**New:**
Example Flow 2:
- We have fixed adding a group and getting the list of groups, so these errors are no longer there.
Example Flow 3:
- We have pivoted to showing what movies we know are available on a said streaming service. So a user would now enter "Netflix" and our endpoint would return the movies that we know are on Netflix. The list might not be 100% complete, but, nevertheless, our endpoint returns movies on that platform. 


## David Weaver's Suggestions 

## Schema/API Design comments (David-Weaver) https://github.com/TylerNP/365MM-/issues/41
Schema 
1. Setting the name to "null" explicitly allows us to identify rows where no name has been entered.
2. No, this is not possible
3. Foreign key names like movie_genres_movie_id_fkey1 are automatically generated and are standard.
4. It’s better to leave it NULL to signify “unspecified” and require users to explicitly set the language.
5. Joined or combined tables are typically created dynamically in queries and are not stored in the schema. Including them would be redundant.

API spec
1. The {movie_id} in the path already identifies it. Asking again in the request payload is unnecessary.
2. We prefer our method of returning the ID back as confirmation.
3. User verification /authentication is too complicated for the scope of this course
4. The {movie_id} in the path already identifies it. Asking again in the request payload is unnecessary.
5. The {genre} in the URL already specifies the genre.
6. The {movie_id} in the path already identifies it. Asking again is unnecessary.
7. The group is already identified in the URL. Requesting it again in the body or query parameters duplicates information and goes against RESTful design.


### Test Results (David Weaver) https://github.com/TylerNP/365MM-/issues/42
1. Movie ID 2: Similar to how login work (where a user inputs their username and then receive an id) we intended for movies to work the same way. So a user would either search for a movie and get an ID or our system would give them an ID to look up. The main idea being that they are given an ID rather than expected to come up with one.
2. I see your point with liking and rating. We thought of liking a movie as something similar to pinning a post on Instagram. So rather than using liked as a metric of calculating other endpoints, we have a separate rating which is more in line with a user giving their honest opinion on a movie. So "liked" is a way to broadcast movies you liked (think all time favorites).
3. The signup endpoint not being sanitized has now been fixed. So an empty string or a string of just spaces is not valid.
4. Negative ratings and ratings above 10 are now no longer allowed.


### Product ideas (David-Weaver) https://github.com/TylerNP/365MM-/issues/40
We did not implement auth because Professor Pierce advised us not to. I think a "pick up where you left off" feature is cool, but that would be very cumbersome for the user to interact with every time they leave a movie. As well, I think most streaming services automatically keep track of where a user last left a movie. Thank you.

### Code Review Comments (David-Weaver) https://github.com/TylerNP/365MM-/issues/39
1. We implemented an exception when a user tries to use a duplicate username. Thank you for your input
2. Although we agree, we will stick with the existing variable conventions for consistency
3. Good point. For loop is moved out of the connection
4. --
5. Recommended only does the for loop for 6 movies so that it wont reach runtime errors

6. We have changed the issue with format_movie()
7. Not sure what you are suggesting because we are using WITH statements instead of one big query
8. --
9. See 2
10. For loop moved out of the connection.
