# USER Stories

1) As an admin I want to be able to remove movies and log potential duplicates, so that their is no repetitive information (remove duplicates)
2) As an admin, I want to verify the user's email, so that someone is not spamming our systems. (verify email)
3) As a user I want to rate movies as I like them or don’t like them, so that i can get recommendations of what other movies I might like   (rate movies)
4) As a user, I would like to follow a friend, so i can see what movies we might enjoy watching together (or input someone’s email and get the same result) (follow a friend)
5) “As a user of (name of our project), I want to determine which upcoming movies will do well based on the movies I’ve liked. I’m a college student so time and money are limited and I’d want to pick the best possible choice.” (give rec. based on liked and not liked movies)
6) “As a user of (name of our project), I love watching and following actor-director collaborations. (name of our project) allows me to find movies that certain actor-directors have worked together on. For example, a list of Leonardo DiCaprio and Martin Scorsese movies while also recommending other collaborations.” (like directors and actors to get more movie rec. from them)
7) “I am a film producer, and (name of our project) allows me to see which movie genres are doing well. They provide the metrics by user rating, critic reception, and budget to box-office earnings. This helps me to see which projects to invest in next.” (get movie data (analytics))
8) As a new movie person, I want to search based on other metrics that aren't the title. (e.g. genre, actor, director, etc.) (advanced search)
9) As a movie enjoyer on a budget, I want to filter by free to watch movies (return movies that have sources that are free) (or if I have netflix, I want it to show me movies that are on netflix)
10) As Frances, I want to organize movies, so I can find what I have already watched and plan on what I movies I want to watch next (add watch history) 
11) As a person trying to learn a new language, I want to find movies that are in that said langauge (search by goal)
12) As a fan of __ (movie series/direcor/actor) I want updates when there new movies that meet these criterias (notifications)
13) I want people to know what my all time favorite films are so I want to set my all time favorite films are.

# Exceptions

1) If a user rates a movie with a metric that was not intended (ex. 11/10), the user will be prompted to re-enter the rating and explain the parameters (b/c it is an api endpoint.) (error handling for rating)
2) If a user wants to input a movie that looks similar to another movie title, they will be prompted to select from the following an make sure they are not just duplicating a movie. (if a movie to submit looks similar, first ask if they meant that)
3) When a user is verifying their email, if their otp is incorrect, they will be prompted to resend an otp or try again. (otp validation)
4) if a user adds more than 5 movies in the past hour, they will be told to wait an hour till they can add more movies. (spam prevention)
5) Exception: User writes fills out the entry incorrectly 
If a user attempts to fill in the wrong information in a field, then the entry will give back an error to the user and ask them to try again with the correct field. e.g. filling out the year of release instead of movie genre  (error handling for all)
6) A user wants to remove a movie from their watchlist that they don't have (tell them that movie was not on the watchlist to begin with)
7) The movie title doesn’t exist / the movie title has the wrong spelling. (could not find resource)
8) The recommendation algorithm fails to generate personalized suggestions (due to lack of data or algorithm failure). (default to popular if not enough user data)
9) The system fails to recommend interest groups due to lack of matching users or an internal error. (Prompt user to join an exsiting group from a list of groups) (to think of later more)
10) The system is unable to predict the performance of upcoming films due to insufficient data or algorithm failure. (if the cast is not definite for example, budget, genre, etc then say not enough info, try again later)
11) User tries to rate a movie but the submission fails due to network or server issues (Tell them to try rating again after _ mins).
12) If use tries to add a group that doesn't exsit (prompt them to create that group)



# Later Ideas
8) “I love using (name of our project) because it helps me as a film writer with my work. I want my current projects to do well and (name of our project) predicts if a movie will do well in certain demographics. If I'm writing for the action-comedy genre, it provides which subject matter do well and which ones don’t and gives me the average screen time of movies that do well. 
12) As Charmaine, I want to invite my friends, so we can find new movies to watch together


# Duplciate
9) As, Max, I want to find other people who shares the same interest so we can enjoy movies together
11) As Celeste, I want to know the production behind a movie, so that I can find their other works
6) Exception: User tries to release a duplicate entry
If a user attempts to upload a duplicate entry, the entry will return back an error signaling them that the entry already exists and they should try another