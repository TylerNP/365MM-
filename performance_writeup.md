# Fake Data Modeling
### populate_data/fake_data.py [Code Block](https://github.com/TylerNP/365MM-/blob/tylerp/populate_data/fake_data.py)

#### Cast Members
First we created 1000 fake cast members. We approximated 1000 cast members specifically, since on average actors typically act in about 50 movies in their career, this would approximately map out to the approximately 45,000 movies we had. From this, we also generated about 50,000 role entries to map actors to their respecitve movies. 

### Streaming Services
We used 15 fake streaming services, to roughly map out the popular streaming services and a few of the more obscure ones. We assumed an average of about 2,000 movies in each service based off the fact the two largest movie collection in streaming services, Netflix and Amazon had 4,000 and 6,000 movies and assumed that besides the top services the collection sizes would drop significantly especially since these services usually drop movies to keep their collection from growing too big for their cost. 

### Users
Finally we assumed that the users would grow the most with their interactions with movies. We assumed that users would interact(like, watch, rate, or save) with movies on average 13 times. However, we assumed that most of this traffic would funnel into users watching or saving movies and a smaller portion towards liking and rating a movie. We assumed that users were equally likely to save or watch a movie, while they were half as likely to like or rate. With this in mind, we assumed users to grow by 50,000.

#### Groups
With about 50,000 users, we assumed a little less than 1 in 10 users would make a group on average. So we set the number to 4,000. With this in mind we assumed that each group would contain an average of 19 users. This number came to mind, since we assume that there would probably be a few large groups with over 100 users of users and a majority of the groups to be around 10 and under. So we used a rough estimate of 90% of groups had 10 users and 10% had 100 to get 19 on average.

### Genre interests
We assumed that groups would be slightly more interested in rating genres to clearly state their interests and users would be slightly less likely to do so. So, we assumed that groups would average around 3 genre ratings. With this in mind, we lowered the users to around 2.35 to be lower than the groups. 

## Total
With this in mind, we get around 50,000 rows from cast, 30,000 from streaming services, 710,000 from users, and 80,000 from groups and 130,000 from genre interests which sums up to 1,000,000.

# Performance of endpoints

## Analytics

### Get_Movie_Analytics
1. 0.0335 s
2. 
### Get_Genre_Analytics
1. 0.0944 s
2. 
### Get_Most_Popular
1. 0.1592 s 0.1559 s 0.1497 s 
2. 

## Users

### User_Signup
1. 0.0053 s

### User_Login
1. 0.0051 s

### User_Add_movie
1. 0.0108 s

### User_list
1. 0.0397 s

### User_Rate_Movie
1. 0.0138 s

### User_Watched_Movie
1. 0.0127 s

### User_Like_Movie
1. 0.0114 s

### Remove_User
1. 0.0317 s

## Catalog

### Search
1. 0.0423 s 

## Groups

### Get_Group_Info
1. 0.0071 s

### Create_Group
1. 0.0186 s

### Join_Group
1. 0.0207 s

### Remove_From_Group
1. 0.0166 s

### Delete_Group
1. 0.0188 s

### List_Groups
1. 0.0445 s 

## Analytics 

### Get_Movie_Analytics
1. 0.0384 s

### Get_Genre_Analytics
1. 0.1098 s

## Movies

### Get_Movie
1. 0.0078 s

### New_movie
1. 0.0126 s

### Get_Movies_Available
1. 0.0313 s

### Get_Random_Movie_Interested
1. 0.0258 s

## Admin

### Delete_Movie
1. 0.0337 s

### Delete_Group
1. 0.0155 s

## Predictions

### Get_Prediction
1. 0.0047 s

### Create_Prediction
1. 0.3141 s

## Recommendations
### Get_Recommended
1. 0.4866 s

# Performance Tuning
Top 3 Slowest Endpoints:
    - Get_recommended (0.4866s)
    - Create_Prediction (0.3141s)
    - Get_Genre_Analytics (0.1098s)

## Get_Recommended

### 1st Query
```
EXPLAIN
SELECT 
    user_id, movie_id, rating 
FROM 
    ratings 
ORDER BY 
    user_id, rating  
LIMIT
    10000
```

***Explain***
```
Limit  (cost=0.74..888.24 rows=10000 width=24)
  ->  Incremental Sort  (cost=0.74..10788.79 rows=121556 width=24)
    Sort Key: user_id, rating
        Presorted Key: user_id
        Full-sort Groups: 286  Sort Method: quicksort  Average Memory: 28kB  Peak Memory: 28kB
        ->  Index Scan using unique_user_id_movie_id_rating on ratings  (cost=0.42..6048.01 rows=121556 width=24)
Planning Time: 0.599 ms
Execution Time: 3.205 ms
```

### Explanation
The query planner is first keeping in mind the limit (10000) assuming it costs around 888.24 for 10000 rows and scanning the results sequentially over (user_id and rating) sorted by quicksort on the entire table (121556) costing (10788.79) using the index on user_id and movie_id to fetch the results. To improve this result we add an index on the composite user_id and rating

***Results*** (Added composite index on user_id and rating)
```
Limit  (cost=0.42..474.24 rows=10000 width=24)
  ->  Index Scan using user_rating on ratings  (cost=0.42..5760.02 rows=121557 width=24)
Planning Time: 0.168 ms
Execution Time: 1.696 ms
```

### Improvements
With the new index, the query no longer needs to sort the data and needs to scan the entire table, but uses the new index to accomplish this. Results in shorter planning and execution times.

### 2nd Query
```
SELECT
    movies.id,
    movies.name,
    movies.release_date,
    movies.description,
    movies.average_rating,
    movies.budget,
    movies.box_office,
    ARRAY_AGG( DISTINCT COALESCE( genres.name, 'N/A')) as genres,
    ARRAY_AGG( DISTINCT COALESCE(movie_languages.language, 'N/A')) as languages
FROM
    movies
JOIN 
    movie_genres ON movies.id = movie_genres.movie_id 
JOIN 
    genres ON movie_genres.genre_id = genres.id
LEFT JOIN 
    movie_languages on movies.id = movie_languages.movie_id
WHERE 
    movies.id = :movie_id
GROUP BY 
    movies.id,
    movies.name,
    movies.release_date,
    movies.description,
    movies.average_rating,
    movies.budget,
    movies.box_office
```

***Explain*** (Using movie_id = 34000)
```
GroupAggregate  (cost=1.02..33.36 rows=1 width=446)
  Group Key: movies.id
    ->  Nested Loop  (cost=1.02..33.33 rows=2 width=423)
        ->  Nested Loop Left Join  (cost=0.58..12.63 rows=1 width=391)
            Join Filter: (movies.id = movie_languages.movie_id)
            ->  Index Scan using movies_pkey on movies  (cost=0.29..8.31 rows=1 width=382)
                Index Cond: (id = 34000)
            ->  Index Only Scan using unique_movie_language on movie_languages  (cost=0.29..4.31 rows=1 width=17)
                Index Cond: (movie_id = 34000)
    ->  Nested Loop  (cost=0.44..20.68 rows=2 width=40)
        ->  Index Only Scan using unique_movie_genre on movie_genres  (cost=0.29..4.33 rows=2 width=16)
            Index Cond: (movie_id = 34000)
        ->  Index Scan using genres_pkey on genres  (cost=0.15..8.17 rows=1 width=40)
            Index Cond: (id = movie_genres.genre_id)
Planning Time: 0.882 ms
Execution Time: 0.624 ms
```

### Explanation
The query planner first groups the rows resulting in only a single row, with several nested queries that are resolved in about the same time as the grouping or less. After the first nested query, another is nested that filters the results by matching movie_id to the current movie where the id is used to scan the table with matching index which is used in conjunction with a second index to conditional scan on unique movie langauges to retrieve the unique langauges the movie is available in. The next nested query uses a similar index to conditional scan the movie_genres table on movies given by the previous index. Finally, the index on genres id is used to scan the table for matching genre_id froim the previous movie_genres subquery. We decided that the query already uses mostly indices already, so adding more indices would not make any improvements. Also, the time of execution and planning were relatively quick already. 

### 3rd Query
```
SELECT 
    movie_genres.genre_id as genre, COUNT(1) as num_of_movies 
FROM 
    ratings 
JOIN 
    movies ON ratings.movie_id = movies.id
JOIN 
    movie_genres ON movies.id = movie_genres.movie_id
WHERE 
    user_id = :user_id AND ratings.rating >= :good_rating
GROUP BY 
    movie_genres.genre_id
ORDER BY 
    num_of_movies DESC
LIMIT 
    3  
```

***Explain***
```
Limit  (cost=32.89..32.90 rows=3 width=16) (actual time=0.119..0.121 rows=3 loops=1)
  ->  Sort  (cost=32.89..32.91 rows=8 width=16) (actual time=0.118..0.119 rows=3 loops=1)
    Sort Key: (count(1)) DESC
    Sort Method: quicksort  Memory: 25kB
    ->  GroupAggregate  (cost=32.65..32.79 rows=8 width=16) (actual time=0.100..0.102 rows=3 loops=1)
        Group Key: movie_genres.genre_id
        ->  Sort  (cost=32.65..32.67 rows=8 width=8) (actual time=0.094..0.095 rows=3 loops=1)
            Sort Key: movie_genres.genre_id
            Sort Method: quicksort  Memory: 25kB
            ->  Nested Loop  (cost=1.00..32.53 rows=8 width=8) (actual time=0.072..0.086 rows=3 loops=1)
            Join Filter: (ratings.movie_id = movie_genres.movie_id)
                ->  Index Scan using unique_user_id_movie_id_rating on ratings  (cost=0.42..13.75 rows=4 width=8) (actual time=0.041..0.042 rows=2 loops=1)
                Index Cond: (user_id = 130000)
                Filter: (rating >= 5)
                ->  Index Only Scan using movies_pkey on movies  (cost=0.29..4.31 rows=1 width=8) (actual time=0.008..0.008 rows=1 loops=2)
                    Index Cond: (id = ratings.movie_id)
                    Heap Fetches: 0
            ->  Index Only Scan using unique_movie_genre on movie_genres  (cost=0.29..0.36 rows=2 width=16) (actual time=0.011..0.011 rows=2 loops=2)
                Index Cond: (movie_id = movies.id)
                Heap Fetches: 0
Planning Time: 1.123 ms
Execution Time: 0.206 ms
```

### Explanation
First, the query planner keeps in mind the limit (3) and tries to group the result based off the key. However, this is done after the two sorts of which the first one, sorts by the number of entries (aggregate) with a specific genre and the second by the genre_id. Where the sorted results are derived from nested queries that utlizes the index on movie_id to find the matching movies and similarily an index on user_id to find the user related entries. These are used to conditionally scan other indices based off the matching index. To improve this we added a composite index on movie_id and genre_id.

***Results*** (Using User_id 130000 and good_rating = 5)
```
Limit  (cost=32.89..32.90 rows=3 width=16) (actual time=0.143..0.145 rows=3 loops=1)
    ->  Sort  (cost=32.89..32.91 rows=8 width=16) (actual time=0.142..0.143 rows=3 loops=1)
    Sort Method: quicksort  Memory: 25kB
    ->  GroupAggregate  (cost=32.65..32.79 rows=8 width=16) (actual time=0.118..0.121 rows=3 loops=1)
        Group Key: movie_genres.genre_id
        ->  Sort  (cost=32.65..32.67 rows=8 width=8) (actual time=0.113..0.114 rows=3 loops=1)
            Sort Key: movie_genres.genre_id
            Sort Method: quicksort  Memory: 25kB
            ->  Nested Loop  (cost=1.00..32.53 rows=8 width=8) (actual time=0.091..0.105 rows=3 loops=1)
            Join Filter: (ratings.movie_id = movie_genres.movie_id)
                ->  Nested Loop  (cost=0.71..30.98 rows=4 width=16) (actual time=0.051..0.060 rows=2 loops=1)
                Index Cond: (user_id = 130000)
                Filter: (rating >= 5)
                ->  Index Only Scan using movies_pkey on movies  (cost=0.29..4.31 rows=1 width=8) (actual time=0.009..0.009 rows=1 loops=2)
                    Index Cond: (id = ratings.movie_id)
                    Heap Fetches: 0
            ->  Index Only Scan using unique_movie_genre on movie_genres  (cost=0.29..0.36 rows=2 width=16) (actual time=0.021..0.021 rows=2 loops=2)
                Index Cond: (movie_id = movies.id)
                Heap Fetches: 0
Planning Time: 1.105 ms
Execution Time: 0.242 ms
```

### Explanation 
No real improvements, as the query plan used the same plan even with the new index. 

### 4th Query
```
WITH rel_ran AS (
    SELECT
        movies.id,
        movies.name,
        movies.release_date,
        movies.description,
        COALESCE(movies.average_rating, 0) AS average_rating,
        movies.budget,
        movies.box_office,
        genres.id as genre_id,
        ROW_NUMBER() OVER (PARTITION BY genres.id ORDER BY RANDOM()) as ranking,
        ARRAY_AGG( DISTINCT COALESCE( genres.name, 'N/A')) as genres,
        ARRAY_AGG( DISTINCT COALESCE(movie_languages.language, 'N/A')) as languages
    FROM
        movies
    JOIN 
        movie_genres ON movies.id = movie_genres.movie_id 
    JOIN 
        genres ON movie_genres.genre_id = genres.id
    LEFT JOIN
        movie_languages on movies.id = movie_languages.movie_id
    WHERE
        NOT EXISTS (
            SELECT
            1
            FROM
            watched_movies
            WHERE
            user_id = :user_id
            AND movie_id = movies.id
        ) AND movie_genres.genre_id in (:genre_id_1, :genre_id_2, :genre_id_3)
    GROUP BY movies.id,
        movies.name,
        movies.release_date,
        movies.description,
        movies.average_rating,
        movies.budget,
        movies.box_office,
        genres.id
)
SELECT DISTINCT
    id,
    name,
    release_date,
    description,
    average_rating,
    budget,
    box_office,
    genres,
    languages
FROM 
    rel_ran
WHERE
    (genre_id = :genre_id_1 AND  ranking <= :genre_ranking_1)
    OR (genre_id = :genre_id_2 AND  ranking <= :genre_ranking_2)
    OR (genre_id = :genre_id_3 AND  ranking <= :genre_ranking_3)
```

***Explain***
```
Unique  (cost=14494.41..14496.16 rows=68 width=168) (actual time=61.185..61.202 rows=6 loops=1)
  CTE rel_ran
    ->  WindowAgg  (cost=13686.18..14001.60 rows=14019 width=478) (actual time=51.511..56.138 rows=12005 loops=1)
          ->  Sort  (cost=13686.18..13721.22 rows=14019 width=462) (actual time=51.498..52.801 rows=12005 loops=1)
                Sort Key: genres.id, (random())
                Sort Method: external merge  Disk: 5848kB
                ->  GroupAggregate  (cost=2792.62..9794.61 rows=14019 width=462) (actual time=6.607..41.179 rows=12005 loops=1)
                      Group Key: movies.id, genres.id
                      ->  Incremental Sort  (cost=2792.62..9409.09 rows=14019 width=431) (actual time=6.565..28.141 rows=16468 loops=1)
                            Sort Key: movies.id, genres.id
                            Presorted Key: movies.id
                            Full-sort Groups: 502  Sort Method: quicksort  Average Memory: 39kB  Peak Memory: 39kB
                            ->  Merge Left Join  (cost=2792.18..8778.23 rows=14019 width=431) (actual time=6.535..24.958 rows=16468 loops=1)
                                  Merge Cond: (movies.id = movie_languages.movie_id)
                                  ->  Merge Anti Join  (cost=2791.86..6753.86 rows=11941 width=422) (actual time=6.526..18.937 rows=12005 loops=1)
                                        Merge Cond: (movies.id = watched_movies.movie_id)
                                        ->  Merge Join  (cost=2787.14..6719.22 rows=11943 width=422) (actual time=6.468..18.140 rows=12005 loops=1)
                                              Merge Cond: (movies.id = movie_genres.movie_id)
                                              ->  Index Scan using movies_pkey on movies  (cost=0.29..3640.11 rows=45346 width=382) (actual time=0.007..7.794 rows=45347 loops=1)
                                              ->  Sort  (cost=2786.85..2816.71 rows=11943 width=48) (actual time=6.454..6.851 rows=12005 loops=1)
                                                    Sort Key: movie_genres.movie_id
                                                    Sort Method: quicksort  Memory: 1177kB
                                                    ->  Hash Join  (cost=26.88..1978.08 rows=11943 width=48) (actual time=0.028..5.469 rows=12005 loops=1)
                                                          Hash Cond: (movie_genres.genre_id = genres.id)
                                                          ->  Seq Scan on movie_genres  (cost=0.00..1919.67 rows=11943 width=16) (actual time=0.006..4.344 rows=12005 loops=1)
                                                                Filter: (genre_id = ANY ('{21,22,23}'::bigint[]))
                                                                Rows Removed by Filter: 78953
                                                          ->  Hash  (cost=17.50..17.50 rows=750 width=40) (actual time=0.013..0.014 rows=20 loops=1)
                                                                Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                                                ->  Seq Scan on genres  (cost=0.00..17.50 rows=750 width=40) (actual time=0.006..0.008 rows=20 loops=1)
                                        ->  Sort  (cost=4.72..4.74 rows=9 width=8) (actual time=0.056..0.058 rows=1 loops=1)
                                              Sort Key: watched_movies.movie_id
                                              Sort Method: quicksort  Memory: 25kB
                                              ->  Index Only Scan using unique_user_id_movie_id on watched_movies  (cost=0.42..4.58 rows=9 width=8) (actual time=0.050..0.051 rows=1 loops=1)
                                                    Index Cond: (user_id = 130000)
                                                    Heap Fetches: 0
                                  ->  Index Only Scan using unique_movie_language on movie_languages  (cost=0.29..1721.22 rows=53241 width=17) (actual time=0.007..3.158 rows=56638 loops=1)
                                        Heap Fetches: 78
  ->  Sort  (cost=492.81..492.99 rows=70 width=168) (actual time=61.184..61.184 rows=6 loops=1)
        Sort Key: rel_ran.id, rel_ran.name, rel_ran.release_date, rel_ran.description, rel_ran.average_rating, rel_ran.budget, rel_ran.box_office, rel_ran.genres, rel_ran.languages
        Sort Method: quicksort  Memory: 27kB
        ->  CTE Scan on rel_ran  (cost=0.00..490.67 rows=70 width=168) (actual time=51.516..61.161 rows=6 loops=1)
              Filter: (((genre_id = 21) AND (ranking <= 1)) OR ((genre_id = 22) AND (ranking <= 2)) OR ((genre_id = 23) AND (ranking <= 3)))
              Rows Removed by Filter: 11999
Planning Time: 1.229 ms
Execution Time: 61.949 ms
```

### Explanation (Using User_id 130000 genres(21-23) with ranks(1-3) in same order)
A quick summary of this would be that the planner uses unique to remove duplciate values with multiple sorts to order the data. With the sorts in the CTE, aggregate function are also called to group data and also aggregate data. Also, multiple joins are called to get all the data available for the movies and an anti join is used to remove already seen movies. With this multiple sequential scans on the entire table are done alongside filters to get the necessary movies and their data. In some caes, a hash is used, and others indexes for unique values. Once the CTE is constructed, one last sort is called on it with a filter to only get the top results for the respective genres. 

# Predictions

## 1st Query (ONLY 1)
```
WITH search_genres AS (
    SELECT movie_genres.genre_id 
    FROM movie_genres 
    WHERE movie_genres.movie_id = :movie_id
),
movie_to_check AS (
    SELECT movies.id, movies.duration, EXTRACT(YEAR FROM movies.release_date) "year", EXTRACT(MONTH FROM movies.release_date) "month"
    FROM movies 
    JOIN movie_genres ON movies.id = movie_genres.movie_id 
    JOIN search_genres ON movie_genres.genre_id = search_genres.genre_id
    WHERE movies.id != :movie_id
),
movie_ratings AS (
    SELECT movie_to_check.id, AVG(ratings.rating) AS avg
    FROM movie_to_check
    JOIN ratings ON movie_to_check.id = ratings.movie_id
    GROUP BY movie_to_check.id
),
movie_views AS (
    SELECT movie_to_check.id, COUNT(watched_movies.movie_id) AS view
    FROM movie_to_check
    JOIN watched_movies ON movie_to_check.id = watched_movies.movie_id
    GROUP BY movie_to_check.id
),
movie_rev AS (
    SELECT movie_to_check.id, movies.box_office 
    FROM movie_to_check
    JOIN movies ON movie_to_check.id = movies.id AND box_office != 0
)

SELECT movie_to_check.id, ARRAY_AGG(DISTINCT genres.name) AS genres, movie_views.view, movie_ratings.avg, 
        movie_rev.box_office, movie_to_check.duration, movie_to_check.year, movie_to_check.month
FROM movie_to_check
JOIN movie_genres ON movie_to_check.id = movie_genres.movie_id 
LEFT JOIN search_genres ON movie_genres.genre_id = search_genres.genre_id
JOIN genres ON movie_genres.genre_id = genres.id
LEFT JOIN movie_views ON movie_to_check.id = movie_views.id 
LEFT JOIN movie_ratings ON movie_to_check.id = movie_ratings.id 
LEFT JOIN movie_rev ON movie_to_check.id = movie_rev.id 
WHERE view IS NOT NULL OR avg IS NOT NULL OR box_office IS NOT NULL
GROUP BY movie_to_check.id, movie_views.view, movie_ratings.avg, movie_rev.box_office, movie_to_check.duration, 
        movie_to_check.year, movie_to_check.month
```

### Explain
```
GroupAggregate  (cost=28290.83..50838.25 rows=162918 width=160) (actual time=16.093..16.102 rows=0 loops=1)
  Group Key: movie_to_check.id, movie_views.view, movie_ratings.avg, movies.box_office, movie_to_check.duration, movie_to_check.year, movie_to_check.month
  CTE search_genres
    ->  Index Only Scan using unique_movie_genre on movie_genres movie_genres_1  (cost=0.29..8.33 rows=2 width=8) (actual time=0.025..0.025 rows=0 loops=1)
        Index Cond: (movie_id = 130000)
        Heap Fetches: 0
  CTE movie_to_check
    ->  Hash Join  (cost=1687.13..5083.80 rows=9096 width=80) (actual time=0.082..0.084 rows=0 loops=1)
        Hash Cond: (movies_1.id = movie_genres_2.movie_id)
        ->  Seq Scan on movies movies_1  (cost=0.00..2976.82 rows=45345 width=24) (actual time=0.008..0.008 rows=1 loops=1)
            Filter: (id <> 130000)
        ->  Hash  (cost=1573.43..1573.43 rows=9096 width=8) (actual time=0.027..0.029 rows=0 loops=1)
        Buckets: 16384  Batches: 1  Memory Usage: 128kB
            ->  Nested Loop  (cost=55.54..1573.43 rows=9096 width=8) (actual time=0.027..0.028 rows=0 loops=1)
                ->  CTE Scan on search_genres search_genres_1  (cost=0.00..0.04 rows=2 width=8) (actual time=0.026..0.026 rows=0 loops=1)
                ->  Bitmap Heap Scan on movie_genres movie_genres_2  (cost=55.54..741.22 rows=4548 width=16) (never executed)
                    Recheck Cond: (genre_id = search_genres_1.genre_id)
                    ->  Bitmap Index Scan on movie_genre_genre_id  (cost=0.00..54.40 rows=4548 width=0) (never executed)
                        Index Cond: (genre_id = search_genres_1.genre_id)
  ->  Incremental Sort  (cost=23198.70..40451.28 rows=162918 width=160) (actual time=16.092..16.098 rows=0 loops=1)
        Sort Key: movie_to_check.id, movie_views.view, movie_ratings.avg, movies.box_office, movie_to_check.duration, movie_to_check.year, movie_to_check.month
        Presorted Key: movie_to_check.id
        Full-sort Groups: 1  Sort Method: quicksort  Average Memory: 25kB  Peak Memory: 25kB
        ->  Merge Left Join  (cost=23123.28..25676.86 rows=162918 width=160) (actual time=16.074..16.080 rows=0 loops=1)
            Merge Cond: (movie_to_check.id = movie_to_check_1.id)
            Filter: ((movie_views.view IS NOT NULL) OR (movie_ratings.avg IS NOT NULL) OR (movies.box_office IS NOT NULL))
            ->  Sort  (cost=19770.13..19825.06 rows=21971 width=152) (actual time=16.073..16.078 rows=0 loops=1)
                Sort Key: movie_to_check.id
                Sort Method: quicksort  Memory: 25kB
                ->  Hash Join  (cost=17367.73..18185.66 rows=21971 width=152) (actual time=16.068..16.072 rows=0 loops=1)
                    Hash Cond: (movie_genres.genre_id = genres.id)
                ->  Hash Left Join  (cost=17366.28..18114.31 rows=21971 width=128) (actual time=16.026..16.030 rows=0 loops=1)
                    Hash Cond: (movie_genres.genre_id = search_genres.genre_id)
                    ->  Hash Join  (cost=17366.21..18009.89 rows=21971 width=128) (actual time=16.025..16.029 rows=0 loops=1)
                        Hash Cond: (movie_to_check.id = movie_genres.movie_id)
                        ->  Hash Left Join  (cost=14650.65..14881.33 rows=9096 width=120) (actual time=0.085..0.088 rows=0 loops=1)
                            Hash Cond: (movie_to_check.id = movie_ratings.id)
                            ->  Hash Left Join  (cost=9957.36..10163.66 rows=9096 width=88) (actual time=0.084..0.086 rows=0 loops=1)
                                Hash Cond: (movie_to_check.id = movie_views.id)
                                ->  CTE Scan on movie_to_check  (cost=0.00..181.92 rows=9096 width=80) (actual time=0.083..0.084 rows=0 loops=1)
                                ->  Hash  (cost=9954.86..9954.86 rows=200 width=16) (never executed)
                                    ->  Subquery Scan on movie_views  (cost=9950.86..9954.86 rows=200 width=16) (never executed)
                                        ->  HashAggregate  (cost=9950.86..9952.86 rows=200 width=16) (never executed)
                                            Group Key: movie_to_check_2.id
                                            ->  Hash Join  (cost=7524.69..9695.24 rows=51124 width=16) (never executed)
                                                Hash Cond: (movie_to_check_2.id = watched_movies.movie_id)
                                                ->  CTE Scan on movie_to_check movie_to_check_2  (cost=0.00..181.92 rows=9096 width=8) (never executed)
                                                ->  Hash  (cost=3867.75..3867.75 rows=222875 width=8) (never executed)
                                                    ->  Seq Scan on watched_movies  (cost=0.00..3867.75 rows=222875 width=8) (never executed)
                            ->  Hash  (cost=4690.80..4690.80 rows=200 width=40) (never executed)
                                ->  Subquery Scan on movie_ratings  (cost=4686.30..4690.80 rows=200 width=40) (never executed)
                                    ->  HashAggregate  (cost=4686.30..4688.80 rows=200 width=40) (never executed)
                                        Group Key: movie_to_check_3.id
                                        ->  Hash Join  (cost=3748.03..4532.72 rows=30715 width=16) (never executed)
                                            Hash Cond: (movie_to_check_3.id = ratings.movie_id)
                                            ->  CTE Scan on movie_to_check movie_to_check_3  (cost=0.00..181.92 rows=9096 width=8) (never executed)
                                            ->  Hash  (cost=2228.57..2228.57 rows=121557 width=16) (never executed)
                                                ->  Seq Scan on ratings  (cost=0.00..2228.57 rows=121557 width=16) (never executed)
                    ->  Hash  (cost=1578.58..1578.58 rows=90958 width=16) (actual time=15.756..15.757 rows=90958 loops=1)
                        Buckets: 131072  Batches: 1  Memory Usage: 5288kB
                        ->  Seq Scan on movie_genres  (cost=0.00..1578.58 rows=90958 width=16) (actual time=0.004..7.064 rows=90958 loops=1)
                ->  Hash  (cost=0.04..0.04 rows=2 width=8) (never executed)
                    ->  CTE Scan on search_genres  (cost=0.00..0.04 rows=2 width=8) (never executed)
            ->  Hash  (cost=1.20..1.20 rows=20 width=40) (actual time=0.012..0.012 rows=20 loops=1)
                Buckets: 1024  Batches: 1  Memory Usage: 9kB
                ->  Seq Scan on genres  (cost=0.00..1.20 rows=20 width=40) (actual time=0.007..0.008 rows=20 loops=1)
        ->  Sort  (cost=3353.15..3356.85 rows=1483 width=16) (never executed)
            Sort Key: movie_to_check_1.id
            ->  Hash Join  (cost=3069.24..3275.03 rows=1483 width=16) (never executed)
                Hash Cond: (movie_to_check_1.id = movies.id)
                ->  CTE Scan on movie_to_check movie_to_check_1  (cost=0.00..181.92 rows=9096 width=8) (never executed)
                ->  Hash  (cost=2976.82..2976.82 rows=7393 width=16) (never executed)
                    ->  Seq Scan on movies  (cost=0.00..2976.82 rows=7393 width=16) (never executed)
                        Filter: (box_office <> 0)
Planning Time: 1.337 ms
Execution Time: 16.393 ms
```

### Explanation
To sum this up, the query plan relies heavily on hash joins on the tables with CTES to join the data together. This is used in tandem with sorts and sequential scans to grab the data.

***Results***