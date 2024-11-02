# API Specification For CSC365 Movie Database (365mm)

## 1. Movies
### 1.1 Get Movie Info - `/movies/{movie_id}` (GET)
Obtain movie information. <br />

**Response**:

```json
{
  "movie_id": "integer",
  "name": "string",
  "release_year": "integer",
  "description": "str", 
  "average_rating": "integer",
  "budget": "integer",
  "box_office": "integer",
  "languages": ["string"]
}
```

### 1.2 New Entry - `/movies/new/` (POST)
Creates a new movie entry <br />

**Request**:

```json
{
  "movie_id": "integer",
  "name": "string",
  "release_year": "integer",
  "description": "str", 
  "average_rating": "integer",
  "budget": "integer",
  "box_office": "integer",
  "languages": ["string"],
  "genres": ["string"] 
}
```

**Response**:

```json
{
  "movie_id": "integer"
}
```

### 1.3 Get Movie Availabile - `/movies/availabile/` (GET)
Gives a list of movies that are available with a certain subscription services or if free online <br />

**Request**:

```json
{
  "subscription": "string",
}
```

**Response**:

```json
[
  {
    "movie_id": "integer",
    "name": "string",
    "release_year": "integer",
    "description": "str", 
    "average_rating": "integer",
    "budget": "integer",
    "box_office": "integer",
    "languages": ["string"]
  }
]
```

### 1.4 Get Movie You're Interested In `/movies/user/{user_id}/` (GET)
Get movies you haven't watched yet but have shown intrest in <br />

**Response**:

```json
[
  {
    "movie_id": "integer",
    "name": "string",
    "release_year": "integer",
    "description": "str", 
    "average_rating": "integer",
    "budget": "integer",
    "box_office": "integer",
    "languages": ["string"]
  }
]
```

## 2. Users
### 2.1 User Signup - `/users/signup/` (POST)
Create new user. <br />

**Request**:

```json
{
  "username": "string"
}
```
**Response**:

```json
{
  "success": "boolean"
}
```

### 2.2 User Login - `/users/login/` (GET)
Login existing user. <br />

**Request**:

```json
{
  "username": "string"
}
```
**Response**:

```json
{
  "user_id": "integer"
}
```

### 2.3 User List `/users/{user_id}/list/` (GET)
Retrieves user's list of movies <br />

**Response**:

```json
[
  {
    "movie_id": "integer",
    "name": "string",
    "release_year": "integer",
    "genres": ["string"],  /*genres list size is capped at 6*/ 
    "average_rating": "integer",
    "budget": "integer",
    "box_office": "integer",
    "languages": ["string"]
  }
]
```

### 2.4 Rate Movie - `/users/{user_id}/rate/{movie_id}` (POST)
Rate a movie. <br />

**Request**:

```json
{
  "rating": "integer" /*rating from 0 to 10*/
}
```
**Response**:

```json
{
  "success": "boolean"
}
```

### 2.5 Watched Movie - `/users/{user_id}/watch/{movie_id}` (POST)
Log a movie as watched or not. <br />

**Request**:

```json
{
  "watched": "boolean"
}
```
**Response**:

```json
{
  "success": "boolean"
}
```

## 3. Catalog
### 3.1 Get Catalog - `/catalog/` (GET)
Retrieves the catalog of movies. Each movie will only have one unique entry. <br />

**Response**:

```json
[
  {
    "movie_id": "integer",
    "name": "string",
    "release_year": "integer",
    "genres": ["string"],  /*genres list size is capped at 6*/ 
    "average_rating": "integer",
    "budget": "integer",
    "box_office": "integer",
    "languages": ["string"]
  }
]
```

### 3.2 Find Specific Movies - `/catalog/search, tags=["SEARCH"]` (GET)
Searches for movies based off querry parameters <br />

**Querry Parameters**:

- `movie_name`(optional): The name of the movie
- `genre`(optional): The genre of the movie
- `director`(optional): The director of the movie
- `actor`(optional): The actors in the movie
- `year`(optional): The release year of the movie
- `rating`(optional): The average rating of the movie
- `search_page`(optional): The page number of the results
- `sort_col`(optional): The column to sort the movies by. Possible values: `movie_name`, `genre`, `director`, `actor`, `year`, and `rating`
- `sort_order`(optional): The order the result appears. Possible values: `asc`(ascending) or `desc`(descending). Default: `asc`

**Response**:

The API responds with a JSON object with the following:
- `previous`: A string that represents the link to the previous search page if it exists. If no such page exists this string will be empty.
- `next`: A string that represents the link to the search next page if it exists. If no such page exists this string will be empty. 
- `results`: An array of objects, each representing a movie item. Each movie item has the following properties:
  - `movie_id`: An integer that represents the unique identifier of the movie item
  - `movie_name`: A string that holds the movie name
  - `movie_director`: A string that holds the director of the movie
  - `movie_release_year`: An integer holding the year of release of the movie
  - `movie_genres`: An array of strings storing the genres of the movie
  - `movie_average_rating`: An integer holding the average rating of the movie

## 4. Recommendations
### 4.1 Get Recommendations - `/recommend/{user_id}` (GET)
Creates a reocmmendation list based off user prefences (likes/dislikes) <br />

**Response**:

```json
[
  {
    "movie_id": "integer",
    "name": "string",
    "release_year": "integer",
    "genres": ["string"],  /*genres list size is capped at 6*/ 
    "average_rating": "integer",
    "budget": "integer",
    "box_office": "integer",
    "languages": ["string"]
  }
]
```

### 4.2 Reset Recommendations - `/recommend/{user_id}/reset/` (POST)
Reset a given users recommendations defaulting to most popular <br />

**Response**:
```json
{
  "success": "boolean"
}
```

### 4.3 Delete Recommendation - `/recommend/{user_id}/delete/{movie_id}` (POST)
Removes a specific movie from the recommendation list of a user <br />

**Response**:

```json
{
  "success": "boolean"
}
```

### 4.4 Generate Recommendation - `/recommend/{user_id}/generate/` (POST)
Finds more movies to recommend to a user <br />

**Response**:

```json
[
  {
    "movie_id": "integer",
    "name": "string",
    "release_year": "integer",
    "genres": ["string"],  /*genres list size is capped at 6*/ 
    "average_rating": "integer",
    "budget": "integer",
    "box_office": "integer",
    "languages": ["string"]
  }
]
```

### 4.5 Generate Recommendation based on collaborations - `/recommend/{user_id}/collab/` (POST)
Provides a list of movies that both an actor and director have worked on together. The call passes in two strings, the actor name and director name. Returns a list of movies that actor director has worked on together <br />

**Request**:

```json
{
  "actor" : "string",
  "director" : "string"
}
```

**Response**:

```json
[
  {
    "movie_id": "integer",
    "name": "string",
    "release_year": "integer",
    "genres": ["string"],  /*genres list size is capped at 6*/ 
    "average_rating": "integer",
    "budget": "integer",
    "box_office": "integer",
    "languages": ["string"]
  }
]
```

## 5. Analytics
### 5.1 Get Analytics - `/analytics/{movie_id}` (GET)
Get the performance data of a movie <br />

**Response**:

```json
{
  "viewed": "integer",
  "rated": "integer",
  "average_rating": "integer",
  "liked": "integer",
  "disliked": "integer"
}
```

### 5.2 Get Analytics Genre - `/analytics/{genre}` (GET)
Based on genre provide average movie performance<br />

**Response**:

```json
{
  "average_views": "integer",
  "average_rating": "integer",
  "average_likes": "integer",
  "average_dislikes": "integer",
  "most_views": "integer",
  "highest_rating": "integer",
  "least_views": "integer",
  "lowest_rating": "integer",
  "movie_ids": ["integer"] /* movie for most_views, highest_rating, least_views, and lowest_views in this order */
}
```

## 5.3 Get Analytics Popular - `/analytics/popular/` (GET)
Provides a list of the performance of the top 5 of each most rated,most viewed, and most liked movies <br />

**Response**:

```json
[
  {
    "movie_id": "integer",
    "viewed": "integer",
    "rated": "integer",
    "liked": "integer",
  }
]
```

### 5.4 Search Analytics - `/analytics/search, tag=["SEARCH"]`
Searches for movies based off querry parameters <br />

**Querry Parameters**:

- `movie_name`(optional): The name of the movie
- `budget`(optional): The budget of the movie
- `box-office`(optional): The box-office performance of the movie
- `languages`(optional): The viewing languages of the movie
- `sort_col`(optional): The column to sort the movies by. Possible values: `budget`, `box-office`, `languages`, and `movie_name`
- `sort_order`(optional): The order the result appears. Possible values: `asc`(ascending) or `desc`(descending). Default: `asc`

**Response**:

The API responds with a JSON object with the following:
- `previous`: A string that represents the link to the previous search page if it exists. If no such page exists this string will be empty.
- `next`: A string that represents the link to the search next page if it exists. If no such page exists this string will be empty. 
- `results`: An array of objects, each representing an analytics item. Each analytics item has the following properties:
  - `movie_id`: An integer that represents the unique identifier of the movie item
  - `budget`: An integer representing the budget of the movie
  - `box-office`: An integer representing the performance of the movie in the box-office
  - `languages`: A string that represents the languages viewing the movie

## 6. Predictions
### 6.1 Get Prediction - `/predictions/{movie_id}` (GET)
Gets information about a prediction of a movie performance in respect with the box-office and viewing languages. <br />

**Response**:

```json
{
  "predicted_rating": "integer",
  "box-office": "integer",
  "viewing_languages": ["string"]
}
```

### 6.2 Generate Prediction - `/predictions/generate/` (POST)
Attempts to predict the movie performance in the box-office and with specific languages. <br />

**Request**:

```json
{
  "movie_id": "integer"
}
```

**Response**:

```json
{
  "success": "boolean"
}
```

## 7. Groups
### 7.1 Get Group - `/groups/{group_id}` (GET)
Get information about a group. <br />

**Response**:

```json
{
  "group_name": "string",
  "group_desciprtion": "string",
  "group_interests": ["string"]
}
```

### 7.2 Create Group - `/groups/{group_id}` (PUT)
Create a new group for users to join. <br />

**Request**:

```json
{
  "group_name": "string",
  "group_desciprtion": "string",
  "group_interests": ["string"]
}
```

**Response**:

```json
{
  "group_id": "integer" /*Unique number that identifies a group*/
}
```

### 7.3 Join group - `/groups/{group_id}/join/` (POST)
Add an user to a specific group. <br />

**Request**:

```json
{
  "user_id": "integer"
}
```

**Response**:

```json
{
  "success": "boolean"
}
```

### 7.4 Remove User From Group - `/groups/{group_id}/remove/` (POST)
Remove an user from the group. <br />

**Request**:

```json
{
  "user_id": "integer"
}
```

**Response**:

```json
{
  "success": "boolean"
}
```

### 7.5 Delete Group - `/groups/{group_id}` (POST)
Delete a group. <br />

**Response**:

```json

{
    "success": "boolean"
}

```

### 7.6 List Groups - `/groups/list/` (GET)
Shows all groups available. <br />

**Response**:

```json
[
  {
    "group_name": "string",
    "group_desciprtion": "string",
    "group_interests": ["string"]
  }
]
```

## 8. Admin
### 8.1 Delete Movie - `/admin/movies/delete/` (POST)
Delete a movie entry. <br />

**Request**:

```json
{
  "movie_id": "integer"
}
```

**Response**:

```json
{
  "success": "boolean"
}
```



1. Get Random Movie Endpoint 
2. Post Rate Movie (0-10) (weight above a 5 is yes, below is no) # log movie into it 




# Scratch Work 
## Endpoints
1. Movies
1.1 Get Movie Info (generic info)
1.1. Get Random Movie

2. Users
2.1 Rate user

3. Catalog

4. Recommend

5. Predictions

6. Analytics

7. Group

8. Admin