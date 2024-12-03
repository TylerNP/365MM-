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
 
### Get_Genre_Analytics
1. 0.0944 s

### Get_Most_Popular
1. 0.1592 s 
2. 0.1559 s 
3. 0.1497 s 

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
The query planner is first keeping in mind the limit (10000) assuming it costs around 888.24 for 10000 rows and scanning the results sequentially over (user_id and rating) sorted by quicksort on the entire table (121556) costing (10788.79) using the index on user_id and movie_id to fetch the results. 

### Composite Index on user_id and rating for ratings
To improve this result we add an index on the composite user_id and rating to remove the need of sorting the results.

***Results*** 
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
First, the query planner keeps in mind the limit (3) and tries to group the result based off the key. However, this is done after the two sorts of which the first one, sorts by the number of entries (aggregate) with a specific genre and the second by the genre_id. Where the sorted results are derived from nested queries that utlizes the index on movie_id to find the matching movies and similarily an index on user_id to find the user related entries. These are used to conditionally scan other indices based off the matching index. 

### Composite Index On movie_id and genre_id for movie_genres
To improve this we added a composite index on movie_id and genre_id to try to reduce the cost of the group by.

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

### Improvements 
No noticable improvements as the query planner used the same plan. 

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
Unique  (cost=14466.43..14468.18 rows=68 width=168) (actual time=71.241..71.262 rows=6 loops=1)
  CTE rel_ran
    ->  WindowAgg  (cost=13658.19..13973.62 rows=14019 width=478) (actual time=61.797..66.217 rows=12005 loops=1)
          ->  Sort  (cost=13658.19..13693.24 rows=14019 width=462) (actual time=61.789..62.928 rows=12005 loops=1)
                Sort Key: genres.id, (random())
                Sort Method: external merge  Disk: 5848kB
                ->  GroupAggregate  (cost=9.90..9766.62 rows=14019 width=462) (actual time=0.159..51.191 rows=12005 loops=1)
                      Group Key: movies.id, genres.id
                      ->  Merge Left Join  (cost=9.90..9381.10 rows=14019 width=431) (actual time=0.101..34.182 rows=16468 loops=1)
                            Merge Cond: (movies.id = movie_languages.movie_id)
                            ->  Nested Loop  (cost=9.58..7356.73 rows=11941 width=422) (actual time=0.087..25.989 rows=12005 loops=1)
                                  ->  Merge Anti Join  (cost=9.43..7063.05 rows=11941 width=390) (actual time=0.058..22.747 rows=12005 loops=1)
                                        Merge Cond: (movies.id = watched_movies.movie_id)
                                        ->  Merge Join  (cost=0.71..7024.41 rows=11943 width=390) (actual time=0.031..21.719 rows=12005 loops=1)
                                              Merge Cond: (movie_genres.movie_id = movies.id)
                                              ->  Index Only Scan using idx_movie_genres_movie_id_genre_id on movie_genres  (cost=0.42..3121.88 rows=11943 width=16) (actual time=0.015..6.303 rows=12005 loops=1)
                                                    Filter: (genre_id = ANY ('{21,22,23}'::bigint[]))
                                                    Rows Removed by Filter: 78953
                                                    Heap Fetches: 110
                                              ->  Index Scan using movies_pkey on movies  (cost=0.29..3640.12 rows=45347 width=382) (actual time=0.013..11.200 rows=45347 loops=1)
                                        ->  Sort  (cost=8.72..8.74 rows=9 width=8) (actual time=0.026..0.027 rows=1 loops=1)
                                              Sort Key: watched_movies.movie_id
                                              Sort Method: quicksort  Memory: 25kB
                                              ->  Index Only Scan using unique_user_id_movie_id on watched_movies  (cost=0.42..8.58 rows=9 width=8) (actual time=0.018..0.018 rows=1 loops=1)
                                                    Index Cond: (user_id = 130000)
                                                    Heap Fetches: 0
                                  ->  Memoize  (cost=0.15..0.17 rows=1 width=40) (actual time=0.000..0.000 rows=1 loops=12005)
                                        Cache Key: movie_genres.genre_id
                                        Cache Mode: logical
                                        Hits: 12002  Misses: 3  Evictions: 0  Overflows: 0  Memory Usage: 1kB
                                        ->  Index Scan using genre_genre_id on genres  (cost=0.14..0.16 rows=1 width=40) (actual time=0.009..0.009 rows=1 loops=3)
                                              Index Cond: (id = movie_genres.genre_id)
                            ->  Index Only Scan using unique_movie_language on movie_languages  (cost=0.29..1721.22 rows=53241 width=17) (actual time=0.012..4.215 rows=56638 loops=1)
                                  Heap Fetches: 78
  ->  Sort  (cost=492.81..492.99 rows=70 width=168) (actual time=71.240..71.251 rows=6 loops=1)
        Sort Key: rel_ran.id, rel_ran.name, rel_ran.release_date, rel_ran.description, rel_ran.average_rating, rel_ran.budget, rel_ran.box_office, rel_ran.genres, rel_ran.languages
        Sort Method: quicksort  Memory: 27kB
        ->  CTE Scan on rel_ran  (cost=0.00..490.67 rows=70 width=168) (actual time=61.801..71.206 rows=6 loops=1)
              Filter: (((genre_id = 21) AND (ranking <= 1)) OR ((genre_id = 22) AND (ranking <= 2)) OR ((genre_id = 23) AND (ranking <= 3)))
              Rows Removed by Filter: 11999
Planning Time: 2.421 ms
Execution Time: 72.049 ms
```

### Explanation (Using User_id 130000 genres(21-23) with ranks(1-3) in same order)
A quick summary of this would be that the planner uses unique to remove duplciate values with multiple sorts to order the data. With the sorts in the CTE, aggregate function are also called to group data and also aggregate data. Also, multiple joins are called to get all the data available for the movies and an anti join is used to remove already seen movies. With this multiple sequential scans on the entire table are done alongside filters to get the necessary movies and their data. In some caes, a hash is used, and others indexes for unique values. Once the CTE is constructed, one last sort is called on it with a filter to only get the top results for the respective genres. 

### Index on genre_id for movie_genres
Since a sequential scan is called on genre_id for movie_genres an index can improve the performance. 

***Results***
```
Unique  (cost=13534.45..13536.20 rows=68 width=168) (actual time=54.668..54.683 rows=6 loops=1)
  CTE rel_ran
    ->  WindowAgg  (cost=12726.21..13041.64 rows=14019 width=478) (actual time=45.501..49.489 rows=12005 loops=1)
          ->  Sort  (cost=12726.21..12761.26 rows=14019 width=462) (actual time=45.491..46.649 rows=12005 loops=1)
                Sort Key: genres.id, (random())
                Sort Method: external merge  Disk: 5848kB
                ->  GroupAggregate  (cost=1832.64..8834.65 rows=14019 width=462) (actual time=4.381..36.228 rows=12005 loops=1)
                      Group Key: movies.id, genres.id
                      ->  Incremental Sort  (cost=1832.64..8449.12 rows=14019 width=431) (actual time=4.351..23.867 rows=16468 loops=1)
                            Sort Key: movies.id, genres.id
                            Presorted Key: movies.id
                            Full-sort Groups: 502  Sort Method: quicksort  Average Memory: 39kB  Peak Memory: 39kB
                            ->  Merge Left Join  (cost=1832.20..7818.27 rows=14019 width=431) (actual time=4.309..20.921 rows=16468 loops=1)
                                  Merge Cond: (movies.id = movie_languages.movie_id)
                                  ->  Merge Anti Join  (cost=1831.88..5793.90 rows=11941 width=422) (actual time=4.301..15.262 rows=12005 loops=1)
                                        Merge Cond: (movies.id = watched_movies.movie_id)
                                        ->  Merge Join  (cost=1823.16..5755.25 rows=11943 width=422) (actual time=4.274..14.535 rows=12005 loops=1)
                                              Merge Cond: (movies.id = movie_genres.movie_id)
                                              ->  Index Scan using movies_pkey on movies  (cost=0.29..3640.12 rows=45347 width=382) (actual time=0.006..6.817 rows=45347 loops=1)
                                              ->  Sort  (cost=1822.87..1852.72 rows=11943 width=48) (actual time=4.262..4.614 rows=12005 loops=1)
                                                    Sort Key: movie_genres.movie_id
                                                    Sort Method: quicksort  Memory: 1177kB
                                                    ->  Hash Join  (cost=142.89..1014.09 rows=11943 width=48) (actual time=0.443..3.202 rows=12005 loops=1)
                                                          Hash Cond: (movie_genres.genre_id = genres.id)
                                                          ->  Bitmap Heap Scan on movie_genres  (cost=141.44..974.65 rows=11943 width=16) (actual time=0.420..1.930 rows=12005 loops=1)
                                                                Recheck Cond: (genre_id = ANY ('{21,22,23}'::bigint[]))
                                                                Heap Blocks: exact=669
                                                                ->  Bitmap Index Scan on movie_genre_genre_id  (cost=0.00..138.45 rows=11943 width=0) (actual time=0.363..0.363 rows=12005 loops=1)
                                                                      Index Cond: (genre_id = ANY ('{21,22,23}'::bigint[]))
                                                          ->  Hash  (cost=1.20..1.20 rows=20 width=40) (actual time=0.014..0.015 rows=20 loops=1)
                                                                Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                                                ->  Seq Scan on genres  (cost=0.00..1.20 rows=20 width=40) (actual time=0.007..0.008 rows=20 loops=1)
                                        ->  Sort  (cost=8.72..8.74 rows=9 width=8) (actual time=0.026..0.026 rows=1 loops=1)
                                              Sort Key: watched_movies.movie_id
                                              Sort Method: quicksort  Memory: 25kB
                                              ->  Index Only Scan using unique_user_id_movie_id on watched_movies  (cost=0.42..8.58 rows=9 width=8) (actual time=0.019..0.020 rows=1 loops=1)
                                                    Index Cond: (user_id = 130000)
                                                    Heap Fetches: 0
                                  ->  Index Only Scan using unique_movie_language on movie_languages  (cost=0.29..1721.22 rows=53241 width=17) (actual time=0.005..2.910 rows=56638 loops=1)
                                        Heap Fetches: 78
  ->  Sort  (cost=492.81..492.99 rows=70 width=168) (actual time=54.667..54.668 rows=6 loops=1)
        Sort Key: rel_ran.id, rel_ran.name, rel_ran.release_date, rel_ran.description, rel_ran.average_rating, rel_ran.budget, rel_ran.box_office, rel_ran.genres, rel_ran.languages
        Sort Method: quicksort  Memory: 27kB
        ->  CTE Scan on rel_ran  (cost=0.00..490.67 rows=70 width=168) (actual time=45.506..54.644 rows=6 loops=1)
              Filter: (((genre_id = 21) AND (ranking <= 1)) OR ((genre_id = 22) AND (ranking <= 2)) OR ((genre_id = 23) AND (ranking <= 3)))
              Rows Removed by Filter: 11999
Planning Time: 1.113 ms
Execution Time: 55.346 ms
```

### Improvements
With the index on movie_genres, a bitmap heap scan is used rather than a sequential scan improving performance


# Create_Predictions

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
GroupAggregate  (cost=25355.25..47902.66 rows=162918 width=160) (actual time=106.043..127.471 rows=13167 loops=1)
  Group Key: movie_to_check.id, movie_views.view, movie_ratings.avg, movies.box_office, movie_to_check.duration, movie_to_check.year, movie_to_check.month
  CTE search_genres
    ->  Index Scan using movie_genre_movie_id_index on movie_genres movie_genres_1  (cost=0.29..8.33 rows=2 width=8) (actual time=0.062..0.064 rows=1 loops=1)
          Index Cond: (movie_id = 40000)
  CTE movie_to_check
    ->  Hash Join  (cost=1687.13..5083.82 rows=9096 width=80) (actual time=3.336..17.773 rows=13174 loops=1)
          Hash Cond: (movies_1.id = movie_genres_2.movie_id)
          ->  Seq Scan on movies movies_1  (cost=0.00..2976.84 rows=45346 width=24) (actual time=0.006..7.955 rows=45346 loops=1)
                Filter: (id <> 40000)
                Rows Removed by Filter: 1
          ->  Hash  (cost=1573.43..1573.43 rows=9096 width=8) (actual time=3.282..3.283 rows=13175 loops=1)
                Buckets: 16384  Batches: 1  Memory Usage: 643kB
                ->  Nested Loop  (cost=55.54..1573.43 rows=9096 width=8) (actual time=0.387..2.448 rows=13175 loops=1)
                      ->  CTE Scan on search_genres search_genres_1  (cost=0.00..0.04 rows=2 width=8) (actual time=0.064..0.066 rows=1 loops=1)
                      ->  Bitmap Heap Scan on movie_genres movie_genres_2  (cost=55.54..741.22 rows=4548 width=16) (actual time=0.320..1.665 rows=13175 loops=1)
                            Recheck Cond: (genre_id = search_genres_1.genre_id)
                            Heap Blocks: exact=669
                            ->  Bitmap Index Scan on movie_genre_genre_id  (cost=0.00..54.40 rows=4548 width=0) (actual time=0.265..0.265 rows=13175 loops=1)
                                  Index Cond: (genre_id = search_genres_1.genre_id)
  ->  Incremental Sort  (cost=20263.10..37515.68 rows=162918 width=160) (actual time=106.010..116.202 rows=29749 loops=1)
        Sort Key: movie_to_check.id, movie_views.view, movie_ratings.avg, movies.box_office, movie_to_check.duration, movie_to_check.year, movie_to_check.month
        Presorted Key: movie_to_check.id
        Full-sort Groups: 904  Sort Method: quicksort  Average Memory: 28kB  Peak Memory: 28kB
        ->  Merge Left Join  (cost=20187.68..22741.26 rows=162918 width=160) (actual time=105.978..110.044 rows=29749 loops=1)
              Merge Cond: (movie_to_check.id = movie_to_check_1.id)
              Filter: ((movie_views.view IS NOT NULL) OR (movie_ratings.avg IS NOT NULL) OR (movies.box_office IS NOT NULL))
              Rows Removed by Filter: 15
              ->  Sort  (cost=16834.52..16889.45 rows=21971 width=152) (actual time=98.919..99.666 rows=29764 loops=1)
                    Sort Key: movie_to_check.id
                    Sort Method: quicksort  Memory: 3544kB
                    ->  Hash Join  (cost=14432.11..15250.04 rows=21971 width=152) (actual time=84.360..95.337 rows=29764 loops=1)
                          Hash Cond: (movie_genres.genre_id = genres.id)
                          ->  Hash Left Join  (cost=14430.66..15178.69 rows=21971 width=128) (actual time=84.337..93.178 rows=29764 loops=1)
                                Hash Cond: (movie_genres.genre_id = search_genres.genre_id)
                                ->  Hash Join  (cost=14430.59..15074.27 rows=21971 width=128) (actual time=84.330..90.968 rows=29764 loops=1)
                                      Hash Cond: (movie_to_check.id = movie_genres.movie_id)
                                      ->  Hash Left Join  (cost=11715.04..11945.71 rows=9096 width=120) (actual time=69.943..73.352 rows=13174 loops=1)
                                            Hash Cond: (movie_to_check.id = movie_ratings.id)
                                            ->  Hash Left Join  (cost=7021.74..7228.04 rows=9096 width=88) (actual time=45.610..47.561 rows=13174 loops=1)
                                                  Hash Cond: (movie_to_check.id = movie_views.id)
                                                  ->  CTE Scan on movie_to_check  (cost=0.00..181.92 rows=9096 width=80) (actual time=3.338..3.791 rows=13174 loops=1)
                                                  ->  Hash  (cost=7019.24..7019.24 rows=200 width=16) (actual time=42.264..42.266 rows=13069 loops=1)
                                                        Buckets: 16384 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 741kB
                                                        ->  Subquery Scan on movie_views  (cost=780.45..7019.24 rows=200 width=16) (actual time=17.145..41.438 rows=13069 loops=1)
                                                              ->  GroupAggregate  (cost=780.45..7017.24 rows=200 width=16) (actual time=17.144..40.876 rows=13069 loops=1)
                                                                    Group Key: movie_to_check_2.id
                                                                    ->  Merge Join  (cost=780.45..6759.62 rows=51124 width=16) (actual time=17.135..37.181 rows=64705 loops=1)
                                                                          Merge Cond: (watched_movies.movie_id = movie_to_check_2.id)
                                                                          ->  Index Only Scan using idx_watched_movies_movie_id on watched_movies  (cost=0.42..4655.55 rows=222875 width=8) (actual time=0.029..8.710 rows=222820 loops=1)
                                                                                Heap Fetches: 107
                                                                          ->  Sort  (cost=780.03..802.77 rows=9096 width=8) (actual time=17.102..18.665 rows=64810 loops=1)
                                                                                Sort Key: movie_to_check_2.id
                                                                                Sort Method: quicksort  Memory: 385kB
                                                                                ->  CTE Scan on movie_to_check movie_to_check_2  (cost=0.00..181.92 rows=9096 width=8) (actual time=0.000..16.321 rows=13174 loops=1)
                                            ->  Hash  (cost=4690.80..4690.80 rows=200 width=40) (actual time=24.326..24.328 rows=12301 loops=1)
                                                  Buckets: 16384 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 725kB
                                                  ->  Subquery Scan on movie_ratings  (cost=4686.30..4690.80 rows=200 width=40) (actual time=20.987..23.540 rows=12301 loops=1)
                                                        ->  HashAggregate  (cost=4686.30..4688.80 rows=200 width=40) (actual time=20.987..23.018 rows=12301 loops=1)
                                                              Group Key: movie_to_check_3.id
                                                              Batches: 1  Memory Usage: 2465kB
                                                              ->  Hash Join  (cost=3748.03..4532.72 rows=30715 width=16) (actual time=12.609..17.599 rows=35514 loops=1)
                                                                    Hash Cond: (movie_to_check_3.id = ratings.movie_id)
                                                                    ->  CTE Scan on movie_to_check movie_to_check_3  (cost=0.00..181.92 rows=9096 width=8) (actual time=0.001..0.481 rows=13174 loops=1)
                                                                    ->  Hash  (cost=2228.57..2228.57 rows=121557 width=16) (actual time=12.484..12.484 rows=121557 loops=1)
                                                                          Buckets: 131072  Batches: 1  Memory Usage: 6722kB
                                                                          ->  Seq Scan on ratings  (cost=0.00..2228.57 rows=121557 width=16) (actual time=0.010..5.534 rows=121557 loops=1)
                                      ->  Hash  (cost=1578.58..1578.58 rows=90958 width=16) (actual time=14.208..14.208 rows=90958 loops=1)
                                            Buckets: 131072  Batches: 1  Memory Usage: 5288kB
                                            ->  Seq Scan on movie_genres  (cost=0.00..1578.58 rows=90958 width=16) (actual time=0.005..6.299 rows=90958 loops=1)
                                ->  Hash  (cost=0.04..0.04 rows=2 width=8) (actual time=0.002..0.003 rows=1 loops=1)
                                      Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                      ->  CTE Scan on search_genres  (cost=0.00..0.04 rows=2 width=8) (actual time=0.001..0.001 rows=1 loops=1)
                          ->  Hash  (cost=1.20..1.20 rows=20 width=40) (actual time=0.012..0.012 rows=20 loops=1)
                                Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                ->  Seq Scan on genres  (cost=0.00..1.20 rows=20 width=40) (actual time=0.006..0.007 rows=20 loops=1)
              ->  Sort  (cost=3353.16..3356.87 rows=1483 width=16) (actual time=7.055..7.214 rows=6625 loops=1)
                    Sort Key: movie_to_check_1.id
                    Sort Method: quicksort  Memory: 239kB
                    ->  Hash Join  (cost=3069.25..3275.05 rows=1483 width=16) (actual time=5.606..6.841 rows=2605 loops=1)
                          Hash Cond: (movie_to_check_1.id = movies.id)
                          ->  CTE Scan on movie_to_check movie_to_check_1  (cost=0.00..181.92 rows=9096 width=8) (actual time=0.000..0.425 rows=13174 loops=1)
                          ->  Hash  (cost=2976.84..2976.84 rows=7393 width=16) (actual time=5.599..5.599 rows=7397 loops=1)
                                Buckets: 8192  Batches: 1  Memory Usage: 411kB
                                ->  Seq Scan on movies  (cost=0.00..2976.84 rows=7393 width=16) (actual time=0.010..5.166 rows=7397 loops=1)
                                      Filter: (box_office <> 0)
                                      Rows Removed by Filter: 37950
Planning Time: 1.871 ms
Execution Time: 128.222 ms
```

### Explanation
To sum this up, the query plan relies heavily on hash joins on the tables with CTES to join the data together. This is used in tandem with sorts and sequential scans to grab the data. 

### Composite Index on movie_id and rating for ratings
To reduce the cost of the join this a composite index was used to ease the join.

***Results***
```
GroupAggregate  (cost=25355.25..47902.66 rows=162918 width=160) (actual time=122.011..141.917 rows=13167 loops=1)
  Group Key: movie_to_check.id, movie_views.view, movie_ratings.avg, movies.box_office, movie_to_check.duration, movie_to_check.year, movie_to_check.month
  CTE search_genres
    ->  Index Scan using movie_genre_movie_id_index on movie_genres movie_genres_1  (cost=0.29..8.33 rows=2 width=8) (actual time=0.037..0.040 rows=1 loops=1)
          Index Cond: (movie_id = 40000)
  CTE movie_to_check
    ->  Hash Join  (cost=1687.13..5083.82 rows=9096 width=80) (actual time=4.444..22.754 rows=13174 loops=1)
          Hash Cond: (movies_1.id = movie_genres_2.movie_id)
          ->  Seq Scan on movies movies_1  (cost=0.00..2976.84 rows=45346 width=24) (actual time=0.007..10.213 rows=45346 loops=1)
                Filter: (id <> 40000)
                Rows Removed by Filter: 1
          ->  Hash  (cost=1573.43..1573.43 rows=9096 width=8) (actual time=4.371..4.372 rows=13175 loops=1)
                Buckets: 16384  Batches: 1  Memory Usage: 643kB
                ->  Nested Loop  (cost=55.54..1573.43 rows=9096 width=8) (actual time=0.387..3.258 rows=13175 loops=1)
                      ->  CTE Scan on search_genres search_genres_1  (cost=0.00..0.04 rows=2 width=8) (actual time=0.039..0.042 rows=1 loops=1)
                      ->  Bitmap Heap Scan on movie_genres movie_genres_2  (cost=55.54..741.22 rows=4548 width=16) (actual time=0.343..2.256 rows=13175 loops=1)
                            Recheck Cond: (genre_id = search_genres_1.genre_id)
                            Heap Blocks: exact=669
                            ->  Bitmap Index Scan on movie_genre_genre_id  (cost=0.00..54.40 rows=4548 width=0) (actual time=0.265..0.265 rows=13175 loops=1)
                                  Index Cond: (genre_id = search_genres_1.genre_id)
  ->  Incremental Sort  (cost=20263.10..37515.68 rows=162918 width=160) (actual time=121.958..131.388 rows=29749 loops=1)
        Sort Key: movie_to_check.id, movie_views.view, movie_ratings.avg, movies.box_office, movie_to_check.duration, movie_to_check.year, movie_to_check.month
        Presorted Key: movie_to_check.id
        Full-sort Groups: 904  Sort Method: quicksort  Average Memory: 28kB  Peak Memory: 28kB
        ->  Merge Left Join  (cost=20187.68..22741.26 rows=162918 width=160) (actual time=121.918..125.681 rows=29749 loops=1)
              Merge Cond: (movie_to_check.id = movie_to_check_1.id)
              Filter: ((movie_views.view IS NOT NULL) OR (movie_ratings.avg IS NOT NULL) OR (movies.box_office IS NOT NULL))
              Rows Removed by Filter: 15
              ->  Sort  (cost=16834.52..16889.45 rows=21971 width=152) (actual time=114.410..115.092 rows=29764 loops=1)
                    Sort Key: movie_to_check.id
                    Sort Method: quicksort  Memory: 3544kB
                    ->  Hash Join  (cost=14432.11..15250.04 rows=21971 width=152) (actual time=98.840..110.444 rows=29764 loops=1)
                          Hash Cond: (movie_genres.genre_id = genres.id)
                          ->  Hash Left Join  (cost=14430.66..15178.69 rows=21971 width=128) (actual time=98.808..108.373 rows=29764 loops=1)
                                Hash Cond: (movie_genres.genre_id = search_genres.genre_id)
                                ->  Hash Join  (cost=14430.59..15074.27 rows=21971 width=128) (actual time=98.793..106.251 rows=29764 loops=1)
                                      Hash Cond: (movie_to_check.id = movie_genres.movie_id)
                                      ->  Hash Left Join  (cost=11715.04..11945.71 rows=9096 width=120) (actual time=81.066..84.631 rows=13174 loops=1)
                                            Hash Cond: (movie_to_check.id = movie_ratings.id)
                                            ->  Hash Left Join  (cost=7021.74..7228.04 rows=9096 width=88) (actual time=53.425..55.487 rows=13174 loops=1)
                                                  Hash Cond: (movie_to_check.id = movie_views.id)
                                                  ->  CTE Scan on movie_to_check  (cost=0.00..181.92 rows=9096 width=80) (actual time=4.446..4.934 rows=13174 loops=1)
                                                  ->  Hash  (cost=7019.24..7019.24 rows=200 width=16) (actual time=48.964..48.966 rows=13069 loops=1)
                                                        Buckets: 16384 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 741kB
                                                        ->  Subquery Scan on movie_views  (cost=780.45..7019.24 rows=200 width=16) (actual time=21.816..47.983 rows=13069 loops=1)
                                                              ->  GroupAggregate  (cost=780.45..7017.24 rows=200 width=16) (actual time=21.815..47.375 rows=13069 loops=1)
                                                                    Group Key: movie_to_check_2.id
                                                                    ->  Merge Join  (cost=780.45..6759.62 rows=51124 width=16) (actual time=21.804..43.384 rows=64705 loops=1)
                                                                          Merge Cond: (watched_movies.movie_id = movie_to_check_2.id)
                                                                          ->  Index Only Scan using idx_watched_movies_movie_id on watched_movies  (cost=0.42..4655.55 rows=222875 width=8) (actual time=0.053..9.485 rows=222820 loops=1)
                                                                                Heap Fetches: 107
                                                                          ->  Sort  (cost=780.03..802.77 rows=9096 width=8) (actual time=21.745..23.411 rows=64810 loops=1)
                                                                                Sort Key: movie_to_check_2.id
                                                                                Sort Method: quicksort  Memory: 385kB
                                                                                ->  CTE Scan on movie_to_check movie_to_check_2  (cost=0.00..181.92 rows=9096 width=8) (actual time=0.000..20.744 rows=13174 loops=1)
                                            ->  Hash  (cost=4690.80..4690.80 rows=200 width=40) (actual time=27.628..27.630 rows=12301 loops=1)
                                                  Buckets: 16384 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 725kB
                                                  ->  Subquery Scan on movie_ratings  (cost=4686.30..4690.80 rows=200 width=40) (actual time=23.990..26.765 rows=12301 loops=1)
                                                        ->  HashAggregate  (cost=4686.30..4688.80 rows=200 width=40) (actual time=23.989..26.239 rows=12301 loops=1)
                                                              Group Key: movie_to_check_3.id
                                                              Batches: 1  Memory Usage: 2465kB
                                                              ->  Hash Join  (cost=3748.03..4532.72 rows=30715 width=16) (actual time=14.190..20.310 rows=35514 loops=1)
                                                                    Hash Cond: (movie_to_check_3.id = ratings.movie_id)
                                                                    ->  CTE Scan on movie_to_check movie_to_check_3  (cost=0.00..181.92 rows=9096 width=8) (actual time=0.001..0.476 rows=13174 loops=1)
                                                                    ->  Hash  (cost=2228.57..2228.57 rows=121557 width=16) (actual time=13.976..13.976 rows=121557 loops=1)
                                                                          Buckets: 131072  Batches: 1  Memory Usage: 6722kB
                                                                          ->  Seq Scan on ratings  (cost=0.00..2228.57 rows=121557 width=16) (actual time=0.017..6.004 rows=121557 loops=1)
                                      ->  Hash  (cost=1578.58..1578.58 rows=90958 width=16) (actual time=17.395..17.395 rows=90958 loops=1)
                                            Buckets: 131072  Batches: 1  Memory Usage: 5288kB
                                            ->  Seq Scan on movie_genres  (cost=0.00..1578.58 rows=90958 width=16) (actual time=0.011..7.556 rows=90958 loops=1)
                                ->  Hash  (cost=0.04..0.04 rows=2 width=8) (actual time=0.003..0.003 rows=1 loops=1)
                                      Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                      ->  CTE Scan on search_genres  (cost=0.00..0.04 rows=2 width=8) (actual time=0.001..0.001 rows=1 loops=1)
                          ->  Hash  (cost=1.20..1.20 rows=20 width=40) (actual time=0.018..0.018 rows=20 loops=1)
                                Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                ->  Seq Scan on genres  (cost=0.00..1.20 rows=20 width=40) (actual time=0.008..0.011 rows=20 loops=1)
              ->  Sort  (cost=3353.16..3356.87 rows=1483 width=16) (actual time=7.500..7.651 rows=6625 loops=1)
                    Sort Key: movie_to_check_1.id
                    Sort Method: quicksort  Memory: 239kB
                    ->  Hash Join  (cost=3069.25..3275.05 rows=1483 width=16) (actual time=6.105..7.283 rows=2605 loops=1)
                          Hash Cond: (movie_to_check_1.id = movies.id)
                          ->  CTE Scan on movie_to_check movie_to_check_1  (cost=0.00..181.92 rows=9096 width=8) (actual time=0.002..0.399 rows=13174 loops=1)
                          ->  Hash  (cost=2976.84..2976.84 rows=7393 width=16) (actual time=6.096..6.096 rows=7397 loops=1)
                                Buckets: 8192  Batches: 1  Memory Usage: 411kB
                                ->  Seq Scan on movies  (cost=0.00..2976.84 rows=7393 width=16) (actual time=0.018..5.687 rows=7397 loops=1)
                                      Filter: (box_office <> 0)
                                      Rows Removed by Filter: 37950
Planning Time: 2.263 ms
Execution Time: 142.944 ms
```

### Improvements
The query plan did not change, so there was no real improvements. This may be due to the fact that much of the query plan was never executed. 

### Index on movies_id ON movies for box_office != 0
Since the query plan trys to sequential scan movies and filter the results, this can be replaced with an index causing a small improvement.

***Resutls***
```
GroupAggregate  (cost=22632.25..45179.67 rows=162918 width=160) (actual time=93.120..114.572 rows=13167 loops=1)
  Group Key: movie_to_check.id, movie_views.view, movie_ratings.avg, movies.box_office, movie_to_check.duration, movie_to_check.year, movie_to_check.month
  CTE search_genres
    ->  Index Scan using movie_genre_movie_id_index on movie_genres movie_genres_1  (cost=0.29..8.33 rows=2 width=8) (actual time=0.024..0.024 rows=1 loops=1)
          Index Cond: (movie_id = 40000)
  CTE movie_to_check
    ->  Hash Join  (cost=1687.13..5083.82 rows=9096 width=80) (actual time=2.643..14.572 rows=13174 loops=1)
          Hash Cond: (movies_1.id = movie_genres_2.movie_id)
          ->  Seq Scan on movies movies_1  (cost=0.00..2976.84 rows=45346 width=24) (actual time=0.009..6.151 rows=45346 loops=1)
                Filter: (id <> 40000)
                Rows Removed by Filter: 1
          ->  Hash  (cost=1573.43..1573.43 rows=9096 width=8) (actual time=2.601..2.603 rows=13175 loops=1)
                Buckets: 16384  Batches: 1  Memory Usage: 643kB
                ->  Nested Loop  (cost=55.54..1573.43 rows=9096 width=8) (actual time=0.239..1.937 rows=13175 loops=1)
                      ->  CTE Scan on search_genres search_genres_1  (cost=0.00..0.04 rows=2 width=8) (actual time=0.024..0.025 rows=1 loops=1)
                      ->  Bitmap Heap Scan on movie_genres movie_genres_2  (cost=55.54..741.22 rows=4548 width=16) (actual time=0.212..1.324 rows=13175 loops=1)
                            Recheck Cond: (genre_id = search_genres_1.genre_id)
                            Heap Blocks: exact=669
                            ->  Bitmap Index Scan on movie_genre_genre_id  (cost=0.00..54.40 rows=4548 width=0) (actual time=0.164..0.165 rows=13175 loops=1)
                                  Index Cond: (genre_id = search_genres_1.genre_id)
  ->  Incremental Sort  (cost=17540.10..34792.68 rows=162918 width=160) (actual time=93.089..103.285 rows=29749 loops=1)
        Sort Key: movie_to_check.id, movie_views.view, movie_ratings.avg, movies.box_office, movie_to_check.duration, movie_to_check.year, movie_to_check.month
        Presorted Key: movie_to_check.id
        Full-sort Groups: 904  Sort Method: quicksort  Average Memory: 28kB  Peak Memory: 28kB
        ->  Merge Left Join  (cost=17464.68..20018.26 rows=162918 width=160) (actual time=93.065..97.138 rows=29749 loops=1)
              Merge Cond: (movie_to_check.id = movie_to_check_1.id)
              Filter: ((movie_views.view IS NOT NULL) OR (movie_ratings.avg IS NOT NULL) OR (movies.box_office IS NOT NULL))
              Rows Removed by Filter: 15
              ->  Sort  (cost=16834.52..16889.45 rows=21971 width=152) (actual time=90.775..91.514 rows=29764 loops=1)
                    Sort Key: movie_to_check.id
                    Sort Method: quicksort  Memory: 3544kB
                    ->  Hash Join  (cost=14432.11..15250.04 rows=21971 width=152) (actual time=76.276..87.121 rows=29764 loops=1)
                          Hash Cond: (movie_genres.genre_id = genres.id)
                          ->  Hash Left Join  (cost=14430.66..15178.69 rows=21971 width=128) (actual time=76.259..84.992 rows=29764 loops=1)
                                Hash Cond: (movie_genres.genre_id = search_genres.genre_id)
                                ->  Hash Join  (cost=14430.59..15074.27 rows=21971 width=128) (actual time=76.250..82.893 rows=29764 loops=1)
                                      Hash Cond: (movie_to_check.id = movie_genres.movie_id)
                                      ->  Hash Left Join  (cost=11715.04..11945.71 rows=9096 width=120) (actual time=66.185..69.646 rows=13174 loops=1)
                                            Hash Cond: (movie_to_check.id = movie_ratings.id)
                                            ->  Hash Left Join  (cost=7021.74..7228.04 rows=9096 width=88) (actual time=42.331..44.327 rows=13174 loops=1)
                                                  Hash Cond: (movie_to_check.id = movie_views.id)
                                                  ->  CTE Scan on movie_to_check  (cost=0.00..181.92 rows=9096 width=80) (actual time=2.644..3.094 rows=13174 loops=1)
                                                  ->  Hash  (cost=7019.24..7019.24 rows=200 width=16) (actual time=39.681..39.683 rows=13069 loops=1)
                                                        Buckets: 16384 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 741kB
                                                        ->  Subquery Scan on movie_views  (cost=780.45..7019.24 rows=200 width=16) (actual time=14.389..38.894 rows=13069 loops=1)
                                                              ->  GroupAggregate  (cost=780.45..7017.24 rows=200 width=16) (actual time=14.388..38.376 rows=13069 loops=1)
                                                                    Group Key: movie_to_check_2.id
                                                                    ->  Merge Join  (cost=780.45..6759.62 rows=51124 width=16) (actual time=14.381..33.957 rows=64705 loops=1)
                                                                          Merge Cond: (watched_movies.movie_id = movie_to_check_2.id)
                                                                          ->  Index Only Scan using idx_watched_movies_movie_id on watched_movies  (cost=0.42..4655.55 rows=222875 width=8) (actual time=0.022..8.467 rows=222820 loops=1)
                                                                                Heap Fetches: 107
                                                                          ->  Sort  (cost=780.03..802.77 rows=9096 width=8) (actual time=14.355..15.897 rows=64810 loops=1)
                                                                                Sort Key: movie_to_check_2.id
                                                                                Sort Method: quicksort  Memory: 385kB
                                                                                ->  CTE Scan on movie_to_check movie_to_check_2  (cost=0.00..181.92 rows=9096 width=8) (actual time=0.000..13.638 rows=13174 loops=1)
                                            ->  Hash  (cost=4690.80..4690.80 rows=200 width=40) (actual time=23.849..23.850 rows=12301 loops=1)
                                                  Buckets: 16384 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 725kB
                                                  ->  Subquery Scan on movie_ratings  (cost=4686.30..4690.80 rows=200 width=40) (actual time=20.490..23.019 rows=12301 loops=1)
                                                        ->  HashAggregate  (cost=4686.30..4688.80 rows=200 width=40) (actual time=20.490..22.469 rows=12301 loops=1)
                                                              Group Key: movie_to_check_3.id
                                                              Batches: 1  Memory Usage: 2465kB
                                                              ->  Hash Join  (cost=3748.03..4532.72 rows=30715 width=16) (actual time=12.397..16.975 rows=35514 loops=1)
                                                                    Hash Cond: (movie_to_check_3.id = ratings.movie_id)
                                                                    ->  CTE Scan on movie_to_check movie_to_check_3  (cost=0.00..181.92 rows=9096 width=8) (actual time=0.000..0.449 rows=13174 loops=1)
                                                                    ->  Hash  (cost=2228.57..2228.57 rows=121557 width=16) (actual time=12.279..12.280 rows=121557 loops=1)
                                                                          Buckets: 131072  Batches: 1  Memory Usage: 6722kB
                                                                          ->  Seq Scan on ratings  (cost=0.00..2228.57 rows=121557 width=16) (actual time=0.009..5.598 rows=121557 loops=1)
                                      ->  Hash  (cost=1578.58..1578.58 rows=90958 width=16) (actual time=9.944..9.945 rows=90958 loops=1)
                                            Buckets: 131072  Batches: 1  Memory Usage: 5288kB
                                            ->  Seq Scan on movie_genres  (cost=0.00..1578.58 rows=90958 width=16) (actual time=0.004..4.392 rows=90958 loops=1)
                                ->  Hash  (cost=0.04..0.04 rows=2 width=8) (actual time=0.001..0.002 rows=1 loops=1)
                                      Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                      ->  CTE Scan on search_genres  (cost=0.00..0.04 rows=2 width=8) (actual time=0.000..0.001 rows=1 loops=1)
                          ->  Hash  (cost=1.20..1.20 rows=20 width=40) (actual time=0.012..0.012 rows=20 loops=1)
                                Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                ->  Seq Scan on genres  (cost=0.00..1.20 rows=20 width=40) (actual time=0.006..0.008 rows=20 loops=1)
              ->  Sort  (cost=630.16..633.87 rows=1483 width=16) (actual time=2.286..2.442 rows=6625 loops=1)
                    Sort Key: movie_to_check_1.id
                    Sort Method: quicksort  Memory: 239kB
                    ->  Hash Join  (cost=346.26..552.05 rows=1483 width=16) (actual time=0.900..2.050 rows=2605 loops=1)
                          Hash Cond: (movie_to_check_1.id = movies.id)
                          ->  CTE Scan on movie_to_check movie_to_check_1  (cost=0.00..181.92 rows=9096 width=8) (actual time=0.001..0.393 rows=13174 loops=1)
                          ->  Hash  (cost=253.84..253.84 rows=7393 width=16) (actual time=0.894..0.894 rows=7397 loops=1)
                                Buckets: 8192  Batches: 1  Memory Usage: 411kB
                                ->  Index Only Scan using idx_movies_box_office on movies  (cost=0.28..253.84 rows=7393 width=16) (actual time=0.017..0.452 rows=7397 loops=1)
                                      Heap Fetches: 88
Planning Time: 1.214 ms
Execution Time: 115.338 ms
```

### Improvements
Removed sequential scan on movies at end of plan and replaced with index leads to small improvement since most of the execution time is the joins and scans on CTEs. 

# Get_Genre_Analytics

## 1st Query 
```
SELECT genres.id FROM genres WHERE genres.name = :genre
```

***Explain***
```
Seq Scan on genres  (cost=0.00..1.25 rows=1 width=8) (actual time=0.007..0.008 rows=1 loops=1)
  Filter: (name = 'Action'::text)
  Rows Removed by Filter: 19
Planning Time: 0.165 ms
Execution Time: 0.038 ms
```

### Explanation
Sequential scans the table for matching text after removing all other rows that don't meet condition. No index was added as this was sufficiently fast. 

## 2nd Query
```
WITH movie_in_genre AS (
    SELECT
        movies.id AS movie_id, movies.name
    FROM
        movies
    JOIN 
        movie_genres ON movie_genres.movie_id = movies.id 
        AND movie_genres.genre_id = :genre_id
    GROUP BY
        movies.id
),
movie_views AS (
    SELECT
        movie_in_genre.movie_id,
        COUNT(watched_movies.movie_id) AS views
    FROM
        movie_in_genre
    JOIN
        watched_movies
    ON movie_in_genre.movie_id = watched_movies.movie_id
    GROUP BY
        movie_in_genre.movie_id
),
movie_ratings AS (
    SELECT
        movie_in_genre.movie_id,
        ROUND(AVG(ratings.rating), 1) AS movie_avg 
    FROM
        movie_in_genre
    JOIN
        ratings
    ON movie_in_genre.movie_id = ratings.movie_id
    GROUP BY
        movie_in_genre.movie_id
),
movie_likeness AS (
    SELECT
        movie_in_genre.movie_id,
        SUM(CASE WHEN liked_movies.liked = True THEN 1 ELSE 0 END) AS total_likes,
        SUM(CASE WHEN liked_movies.liked = False THEN 1 ELSE 0 END) AS total_dislikes
    FROM
        movie_in_genre
    JOIN
        liked_movies
    ON movie_in_genre.movie_id = liked_movies.movie_id
    GROUP BY
        movie_in_genre.movie_id
),
most_viewed_movies AS (
    SELECT 
        m.movie_id, 
        m.rank 
    FROM (
        SELECT 
        movie_views.movie_id, 
        ROW_NUMBER() OVER (ORDER BY movie_views.views DESC) AS rank 
        FROM movie_views
    ) AS m LIMIT 1
),
filtered_ratings AS (
    SELECT 
        high_ratings, 
        low_ratings 
    FROM (
        (SELECT FIRST_VALUE(movie_id) OVER (ORDER BY rank) AS high_ratings, FIRST_VALUE(movie_id) OVER (ORDER BY rank DESC) AS low_ratings
        FROM (
            SELECT 
            m.movie_id, 
            m.rank 
            FROM (
            SELECT 
                movie_ratings.movie_id, 
                ROW_NUMBER() OVER (ORDER BY movie_ratings.movie_avg DESC) AS rank 
            FROM movie_ratings ) AS m
            ) AS temp
        LIMIT 1)
    ) AS done
),
filtered_views AS (
    SELECT high, low FROM (
    (SELECT FIRST_VALUE(movie_id) OVER (ORDER BY rank) AS high, FIRST_VALUE(movie_id) OVER (ORDER BY rank DESC) AS low
    FROM (
        SELECT 
        m.movie_id, 
        m.rank 
        FROM (
        SELECT 
            movie_views.movie_id, 
            ROW_NUMBER() OVER (ORDER BY movie_views.views DESC) AS rank 
        FROM movie_views) AS m
        ) AS temp 
    LIMIT 1)
    ) AS done
)

SELECT
    COALESCE(ROUND(AVG(movie_views.views), 1)::real,0)  AS avg_views,
    COALESCE(ROUND(AVG(movie_ratings.movie_avg), 1)::real,0)  AS avg_ratings,
    COALESCE(ROUND(AVG(movie_likeness.total_likes), 1)::real,0) AS avg_likes,
    COALESCE(ROUND(AVG(movie_likeness.total_dislikes), 1)::real,0) AS avg_dislikes,
    COALESCE(MAX(movie_views.views),0) AS most_views,
    COALESCE(MAX(movie_ratings.movie_avg)::real,0) AS highest_rating,
    COALESCE(MIN(movie_views.views),0) AS least_views,
    COALESCE(MIN(movie_ratings.movie_avg)::real,0) AS lowest_rating,
    (SELECT high_ratings FROM filtered_ratings) AS highest_rated_movie,
    (SELECT low_ratings FROM filtered_ratings) AS lowest_rated_movie,
    (SELECT high FROM filtered_views) AS highest_viewed_movie,
    (SELECT low FROM filtered_views) AS lowest_viewed_movie
FROM 
    movie_in_genre
LEFT JOIN
    movie_views ON movie_in_genre.movie_id = movie_views.movie_id
LEFT JOIN
    movie_ratings ON movie_in_genre.movie_id = movie_ratings.movie_id
LEFT JOIN
    movie_likeness ON movie_in_genre.movie_id = movie_likeness.movie_id
```

***Explain***
```
Aggregate  (cost=22491.22..22491.25 rows=1 width=72) (actual time=109.166..109.177 rows=1 loops=1)
  CTE movie_in_genre
    ->  HashAggregate  (cost=3907.40..3973.10 rows=6570 width=25) (actual time=17.342..17.859 rows=6589 loops=1)
          Group Key: movies.id
          Batches: 1  Memory Usage: 721kB
          ->  Hash Join  (cost=908.46..3890.98 rows=6570 width=25) (actual time=2.763..16.150 rows=6589 loops=1)
                Hash Cond: (movies.id = movie_genres.movie_id)
                ->  Seq Scan on movies  (cost=0.00..2863.47 rows=45347 width=25) (actual time=0.004..3.287 rows=45347 loops=1)
                ->  Hash  (cost=826.34..826.34 rows=6570 width=8) (actual time=2.725..2.726 rows=6589 loops=1)
                      Buckets: 8192  Batches: 1  Memory Usage: 322kB
                      ->  Bitmap Heap Scan on movie_genres  (cost=75.21..826.34 rows=6570 width=8) (actual time=0.474..2.025 rows=6589 loops=1)
                            Recheck Cond: (genre_id = 21)
                            Heap Blocks: exact=669
                            ->  Bitmap Index Scan on movie_genre_genre_id  (cost=0.00..73.57 rows=6570 width=0) (actual time=0.341..0.342 rows=6589 loops=1)
                                  Index Cond: (genre_id = 21)
  CTE movie_views
    ->  HashAggregate  (cost=9518.98..9520.98 rows=200 width=16) (actual time=43.432..43.819 rows=6535 loops=1)
          Group Key: movie_in_genre_2.movie_id
          Batches: 1  Memory Usage: 737kB
          ->  Hash Join  (cost=7524.69..9334.34 rows=36927 width=16) (actual time=31.946..40.437 rows=32208 loops=1)
                Hash Cond: (movie_in_genre_2.movie_id = watched_movies.movie_id)
                ->  CTE Scan on movie_in_genre movie_in_genre_2  (cost=0.00..131.40 rows=6570 width=8) (actual time=0.001..1.384 rows=6589 loops=1)
                ->  Hash  (cost=3867.75..3867.75 rows=222875 width=8) (actual time=31.850..31.850 rows=222875 loops=1)
                      Buckets: 262144  Batches: 2  Memory Usage: 6396kB
                      ->  Seq Scan on watched_movies  (cost=0.00..3867.75 rows=222875 width=8) (actual time=0.012..13.376 rows=222875 loops=1)
  CTE movie_ratings
    ->  HashAggregate  (cost=4425.73..4428.73 rows=200 width=40) (actual time=17.388..18.277 rows=6154 loops=1)
          Group Key: movie_in_genre_3.movie_id
          Batches: 1  Memory Usage: 1249kB
          ->  Hash Join  (cost=3748.03..4314.81 rows=22185 width=16) (actual time=13.282..15.887 rows=17765 loops=1)
                Hash Cond: (movie_in_genre_3.movie_id = ratings.movie_id)
                ->  CTE Scan on movie_in_genre movie_in_genre_3  (cost=0.00..131.40 rows=6570 width=8) (actual time=0.000..0.244 rows=6589 loops=1)
                ->  Hash  (cost=2228.57..2228.57 rows=121557 width=16) (actual time=13.150..13.150 rows=121557 loops=1)
                      Buckets: 131072  Batches: 1  Memory Usage: 6722kB
                      ->  Seq Scan on ratings  (cost=0.00..2228.57 rows=121557 width=16) (actual time=0.014..6.071 rows=121557 loops=1)
  CTE filtered_ratings
    ->  Subquery Scan on done  (cost=35.93..35.96 rows=1 width=16) (actual time=4.340..4.341 rows=1 loops=1)
          ->  Limit  (cost=35.93..35.95 rows=1 width=24) (actual time=4.339..4.340 rows=1 loops=1)
                ->  WindowAgg  (cost=35.93..39.43 rows=200 width=24) (actual time=4.338..4.339 rows=1 loops=1)
                      ->  Sort  (cost=35.93..36.43 rows=200 width=24) (actual time=4.335..4.336 rows=2 loops=1)
                            Sort Key: m.rank
                            Sort Method: quicksort  Memory: 577kB
                            ->  WindowAgg  (cost=24.79..28.29 rows=200 width=24) (actual time=2.878..3.863 rows=6154 loops=1)
                                  ->  Sort  (cost=24.79..25.29 rows=200 width=16) (actual time=2.875..3.008 rows=6154 loops=1)
                                        Sort Key: m.rank DESC
                                        Sort Method: quicksort  Memory: 529kB
                                        ->  Subquery Scan on m  (cost=11.64..17.14 rows=200 width=16) (actual time=1.070..2.413 rows=6154 loops=1)
                                              ->  WindowAgg  (cost=11.64..15.14 rows=200 width=48) (actual time=1.069..2.178 rows=6154 loops=1)
                                                    ->  Sort  (cost=11.64..12.14 rows=200 width=40) (actual time=1.056..1.207 rows=6154 loops=1)
                                                          Sort Key: movie_ratings_1.movie_avg DESC
                                                          Sort Method: quicksort  Memory: 529kB
                                                          ->  CTE Scan on movie_ratings movie_ratings_1  (cost=0.00..4.00 rows=200 width=40) (actual time=0.001..0.259 rows=6154 loops=1)
  CTE filtered_views
    ->  Subquery Scan on done_1  (cost=35.93..35.96 rows=1 width=16) (actual time=3.921..3.922 rows=1 loops=1)
          ->  Limit  (cost=35.93..35.95 rows=1 width=24) (actual time=3.921..3.921 rows=1 loops=1)
                ->  WindowAgg  (cost=35.93..39.43 rows=200 width=24) (actual time=3.921..3.921 rows=1 loops=1)
                      ->  Sort  (cost=35.93..36.43 rows=200 width=24) (actual time=3.918..3.918 rows=2 loops=1)
                            Sort Key: m_1.rank
                            Sort Method: quicksort  Memory: 601kB
                            ->  WindowAgg  (cost=24.79..28.29 rows=200 width=24) (actual time=2.346..3.383 rows=6535 loops=1)
                                  ->  Sort  (cost=24.79..25.29 rows=200 width=16) (actual time=2.344..2.482 rows=6535 loops=1)
                                        Sort Key: m_1.rank DESC
                                        Sort Method: quicksort  Memory: 550kB
                                        ->  Subquery Scan on m_1  (cost=11.64..17.14 rows=200 width=16) (actual time=0.615..1.861 rows=6535 loops=1)
                                              ->  WindowAgg  (cost=11.64..15.14 rows=200 width=24) (actual time=0.615..1.592 rows=6535 loops=1)
                                                    ->  Sort  (cost=11.64..12.14 rows=200 width=16) (actual time=0.613..0.795 rows=6535 loops=1)
                                                          Sort Key: movie_views_1.views DESC
                                                          Sort Method: quicksort  Memory: 550kB
                                                          ->  CTE Scan on movie_views movie_views_1  (cost=0.00..4.00 rows=200 width=16) (actual time=0.001..0.254 rows=6535 loops=1)
  InitPlan 6 (returns $5)
    ->  CTE Scan on filtered_ratings  (cost=0.00..0.02 rows=1 width=8) (actual time=4.341..4.341 rows=1 loops=1)
  InitPlan 7 (returns $6)
    ->  CTE Scan on filtered_ratings filtered_ratings_1  (cost=0.00..0.02 rows=1 width=8) (actual time=0.000..0.000 rows=1 loops=1)
  InitPlan 8 (returns $7)
    ->  CTE Scan on filtered_views  (cost=0.00..0.02 rows=1 width=8) (actual time=3.922..3.922 rows=1 loops=1)
  InitPlan 9 (returns $8)
    ->  CTE Scan on filtered_views filtered_views_1  (cost=0.00..0.02 rows=1 width=8) (actual time=0.000..0.000 rows=1 loops=1)
  ->  Hash Left Join  (cost=3723.23..4364.99 rows=6570 width=56) (actual time=98.398..100.331 rows=6589 loops=1)
        Hash Cond: (movie_in_genre.movie_id = movie_likeness.movie_id)
        ->  Hash Left Join  (cost=13.00..637.15 rows=6570 width=48) (actual time=81.516..82.992 rows=6589 loops=1)
              Hash Cond: (movie_in_genre.movie_id = movie_ratings.movie_id)
              ->  Hash Left Join  (cost=6.50..384.28 rows=6570 width=16) (actual time=62.227..63.096 rows=6589 loops=1)
                    Hash Cond: (movie_in_genre.movie_id = movie_views.movie_id)
                    ->  CTE Scan on movie_in_genre  (cost=0.00..131.40 rows=6570 width=8) (actual time=17.344..17.580 rows=6589 loops=1)
                    ->  Hash  (cost=4.00..4.00 rows=200 width=16) (actual time=44.862..44.862 rows=6535 loops=1)
                          Buckets: 8192 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 371kB
                          ->  CTE Scan on movie_views  (cost=0.00..4.00 rows=200 width=16) (actual time=43.434..44.499 rows=6535 loops=1)
              ->  Hash  (cost=4.00..4.00 rows=200 width=40) (actual time=19.283..19.284 rows=6154 loops=1)
                    Buckets: 8192 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 353kB
                    ->  CTE Scan on movie_ratings  (cost=0.00..4.00 rows=200 width=40) (actual time=17.390..18.931 rows=6154 loops=1)
        ->  Hash  (cost=3707.73..3707.73 rows=200 width=24) (actual time=16.877..16.878 rows=5896 loops=1)
              Buckets: 8192 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 387kB
              ->  Subquery Scan on movie_likeness  (cost=3703.73..3707.73 rows=200 width=24) (actual time=16.042..16.554 rows=5896 loops=1)
                    ->  HashAggregate  (cost=3703.73..3705.73 rows=200 width=24) (actual time=16.041..16.341 rows=5896 loops=1)
                          Group Key: movie_in_genre_1.movie_id
                          Batches: 1  Memory Usage: 993kB
                          ->  Hash Join  (cost=3057.49..3560.52 rows=19095 width=9) (actual time=12.903..14.798 rows=14519 loops=1)
                                Hash Cond: (movie_in_genre_1.movie_id = liked_movies.movie_id)
                                ->  CTE Scan on movie_in_genre movie_in_genre_1  (cost=0.00..131.40 rows=6570 width=8) (actual time=0.000..0.232 rows=6589 loops=1)
                                ->  Hash  (cost=1818.33..1818.33 rows=99133 width=9) (actual time=12.783..12.783 rows=99134 loops=1)
                                      Buckets: 131072  Batches: 1  Memory Usage: 5671kB
                                      ->  Seq Scan on liked_movies  (cost=0.00..1818.33 rows=99133 width=9) (actual time=0.015..7.142 rows=99134 loops=1)
Planning Time: 1.992 ms
Execution Time: 109.920 ms
```

### Explanation
Essentially, the query planner is trying to aggregate values from multiple CTE expressions. The planner scans through all the CTEs to obtain the pieces of information it needs and the CTEs themselves are formed from a series of hash joins (makes up most of the execution time) and sequential scans on the other CTEs. Withe few base CTEs made up of index scans or bitmaps. 

### Composite Index on movie_id and genre_id for movie_genres
To try and improve performance it we added a composite index on movie_id and genre_id for movie_genres to try to reduce the cost of the bitmap scan. 

***Results***
```
Aggregate  (cost=22491.26..22491.29 rows=1 width=72) (actual time=114.890..114.906 rows=1 loops=1)
  CTE movie_in_genre
    ->  HashAggregate  (cost=3907.40..3973.10 rows=6570 width=25) (actual time=17.961..18.511 rows=6589 loops=1)
          Group Key: movies.id
          Batches: 1  Memory Usage: 721kB
          ->  Hash Join  (cost=908.46..3890.98 rows=6570 width=25) (actual time=2.417..16.717 rows=6589 loops=1)
                Hash Cond: (movies.id = movie_genres.movie_id)
                ->  Seq Scan on movies  (cost=0.00..2863.47 rows=45347 width=25) (actual time=0.004..3.293 rows=45347 loops=1)
                ->  Hash  (cost=826.34..826.34 rows=6570 width=8) (actual time=2.392..2.393 rows=6589 loops=1)
                      Buckets: 8192  Batches: 1  Memory Usage: 322kB
                      ->  Bitmap Heap Scan on movie_genres  (cost=75.21..826.34 rows=6570 width=8) (actual time=0.238..1.888 rows=6589 loops=1)
                            Recheck Cond: (genre_id = 21)
                            Heap Blocks: exact=669
                            ->  Bitmap Index Scan on movie_genre_genre_id  (cost=0.00..73.57 rows=6570 width=0) (actual time=0.168..0.168 rows=6589 loops=1)
                                  Index Cond: (genre_id = 21)
  CTE movie_views
    ->  HashAggregate  (cost=9518.98..9520.98 rows=200 width=16) (actual time=45.460..45.811 rows=6535 loops=1)
          Group Key: movie_in_genre_2.movie_id
          Batches: 1  Memory Usage: 737kB
          ->  Hash Join  (cost=7524.69..9334.34 rows=36927 width=16) (actual time=32.885..42.624 rows=32208 loops=1)
                Hash Cond: (movie_in_genre_2.movie_id = watched_movies.movie_id)
                ->  CTE Scan on movie_in_genre movie_in_genre_2  (cost=0.00..131.40 rows=6570 width=8) (actual time=0.001..1.426 rows=6589 loops=1)
                ->  Hash  (cost=3867.75..3867.75 rows=222875 width=8) (actual time=32.765..32.766 rows=222875 loops=1)
                      Buckets: 262144  Batches: 2  Memory Usage: 6396kB
                      ->  Seq Scan on watched_movies  (cost=0.00..3867.75 rows=222875 width=8) (actual time=0.009..13.737 rows=222875 loops=1)
  CTE movie_ratings
    ->  HashAggregate  (cost=4425.73..4428.73 rows=200 width=40) (actual time=20.185..21.082 rows=6154 loops=1)
          Group Key: movie_in_genre_3.movie_id
          Batches: 1  Memory Usage: 1249kB
          ->  Hash Join  (cost=3748.03..4314.81 rows=22185 width=16) (actual time=14.597..18.538 rows=17765 loops=1)
                Hash Cond: (movie_in_genre_3.movie_id = ratings.movie_id)
                ->  CTE Scan on movie_in_genre movie_in_genre_3  (cost=0.00..131.40 rows=6570 width=8) (actual time=0.000..0.266 rows=6589 loops=1)
                ->  Hash  (cost=2228.57..2228.57 rows=121557 width=16) (actual time=14.417..14.417 rows=121557 loops=1)
                      Buckets: 131072  Batches: 1  Memory Usage: 6722kB
                      ->  Seq Scan on ratings  (cost=0.00..2228.57 rows=121557 width=16) (actual time=0.018..6.113 rows=121557 loops=1)
  CTE filtered_ratings
    ->  Subquery Scan on done  (cost=35.93..35.96 rows=1 width=16) (actual time=4.836..4.838 rows=1 loops=1)
          ->  Limit  (cost=35.93..35.95 rows=1 width=24) (actual time=4.835..4.837 rows=1 loops=1)
                ->  WindowAgg  (cost=35.93..39.43 rows=200 width=24) (actual time=4.833..4.835 rows=1 loops=1)
                      ->  Sort  (cost=35.93..36.43 rows=200 width=24) (actual time=4.830..4.832 rows=2 loops=1)
                            Sort Key: m.rank
                            Sort Method: quicksort  Memory: 577kB
                            ->  WindowAgg  (cost=24.79..28.29 rows=200 width=24) (actual time=3.223..4.296 rows=6154 loops=1)
                                  ->  Sort  (cost=24.79..25.29 rows=200 width=16) (actual time=3.219..3.361 rows=6154 loops=1)
                                        Sort Key: m.rank DESC
                                        Sort Method: quicksort  Memory: 529kB
                                        ->  Subquery Scan on m  (cost=11.64..17.14 rows=200 width=16) (actual time=1.071..2.671 rows=6154 loops=1)
                                              ->  WindowAgg  (cost=11.64..15.14 rows=200 width=48) (actual time=1.070..2.415 rows=6154 loops=1)
                                                    ->  Sort  (cost=11.64..12.14 rows=200 width=40) (actual time=1.057..1.281 rows=6154 loops=1)
                                                          Sort Key: movie_ratings_1.movie_avg DESC
                                                          Sort Method: quicksort  Memory: 529kB
                                                          ->  CTE Scan on movie_ratings movie_ratings_1  (cost=0.00..4.00 rows=200 width=40) (actual time=0.001..0.257 rows=6154 loops=1)
  CTE filtered_views
    ->  Subquery Scan on done_1  (cost=35.93..35.96 rows=1 width=16) (actual time=4.366..4.367 rows=1 loops=1)
          ->  Limit  (cost=35.93..35.95 rows=1 width=24) (actual time=4.365..4.366 rows=1 loops=1)
                ->  WindowAgg  (cost=35.93..39.43 rows=200 width=24) (actual time=4.365..4.366 rows=1 loops=1)
                      ->  Sort  (cost=35.93..36.43 rows=200 width=24) (actual time=4.363..4.363 rows=2 loops=1)
                            Sort Key: m_1.rank
                            Sort Method: quicksort  Memory: 601kB
                            ->  WindowAgg  (cost=24.79..28.29 rows=200 width=24) (actual time=2.709..3.802 rows=6535 loops=1)
                                  ->  Sort  (cost=24.79..25.29 rows=200 width=16) (actual time=2.707..2.859 rows=6535 loops=1)
                                        Sort Key: m_1.rank DESC
                                        Sort Method: quicksort  Memory: 550kB
                                        ->  Subquery Scan on m_1  (cost=11.64..17.14 rows=200 width=16) (actual time=0.683..1.879 rows=6535 loops=1)
                                              ->  WindowAgg  (cost=11.64..15.14 rows=200 width=24) (actual time=0.683..1.633 rows=6535 loops=1)
                                                    ->  Sort  (cost=11.64..12.14 rows=200 width=16) (actual time=0.680..0.842 rows=6535 loops=1)
                                                          Sort Key: movie_views_1.views DESC
                                                          Sort Method: quicksort  Memory: 550kB
                                                          ->  CTE Scan on movie_views movie_views_1  (cost=0.00..4.00 rows=200 width=16) (actual time=0.001..0.281 rows=6535 loops=1)
  InitPlan 6 (returns $5)
    ->  CTE Scan on filtered_ratings  (cost=0.00..0.02 rows=1 width=8) (actual time=4.837..4.838 rows=1 loops=1)
  InitPlan 7 (returns $6)
    ->  CTE Scan on filtered_ratings filtered_ratings_1  (cost=0.00..0.02 rows=1 width=8) (actual time=0.000..0.000 rows=1 loops=1)
  InitPlan 8 (returns $7)
    ->  CTE Scan on filtered_views  (cost=0.00..0.02 rows=1 width=8) (actual time=4.367..4.367 rows=1 loops=1)
  InitPlan 9 (returns $8)
    ->  CTE Scan on filtered_views filtered_views_1  (cost=0.00..0.02 rows=1 width=8) (actual time=0.000..0.000 rows=1 loops=1)
  ->  Hash Left Join  (cost=3723.27..4365.03 rows=6570 width=56) (actual time=103.195..105.109 rows=6589 loops=1)
        Hash Cond: (movie_in_genre.movie_id = movie_likeness.movie_id)
        ->  Hash Left Join  (cost=13.00..637.15 rows=6570 width=48) (actual time=86.974..88.405 rows=6589 loops=1)
              Hash Cond: (movie_in_genre.movie_id = movie_ratings.movie_id)
              ->  Hash Left Join  (cost=6.50..384.28 rows=6570 width=16) (actual time=64.857..65.712 rows=6589 loops=1)
                    Hash Cond: (movie_in_genre.movie_id = movie_views.movie_id)
                    ->  CTE Scan on movie_in_genre  (cost=0.00..131.40 rows=6570 width=8) (actual time=17.963..18.196 rows=6589 loops=1)
                    ->  Hash  (cost=4.00..4.00 rows=200 width=16) (actual time=46.878..46.879 rows=6535 loops=1)
                          Buckets: 8192 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 371kB
                          ->  CTE Scan on movie_views  (cost=0.00..4.00 rows=200 width=16) (actual time=45.463..46.499 rows=6535 loops=1)
              ->  Hash  (cost=4.00..4.00 rows=200 width=40) (actual time=22.111..22.111 rows=6154 loops=1)
                    Buckets: 8192 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 353kB
                    ->  CTE Scan on movie_ratings  (cost=0.00..4.00 rows=200 width=40) (actual time=20.188..21.745 rows=6154 loops=1)
        ->  Hash  (cost=3707.77..3707.77 rows=200 width=24) (actual time=16.213..16.215 rows=5896 loops=1)
              Buckets: 8192 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 387kB
              ->  Subquery Scan on movie_likeness  (cost=3703.77..3707.77 rows=200 width=24) (actual time=15.321..15.865 rows=5896 loops=1)
                    ->  HashAggregate  (cost=3703.77..3705.77 rows=200 width=24) (actual time=15.320..15.638 rows=5896 loops=1)
                          Group Key: movie_in_genre_1.movie_id
                          Batches: 1  Memory Usage: 993kB
                          ->  Hash Join  (cost=3057.52..3560.55 rows=19096 width=9) (actual time=11.135..13.942 rows=14519 loops=1)
                                Hash Cond: (movie_in_genre_1.movie_id = liked_movies.movie_id)
                                ->  CTE Scan on movie_in_genre movie_in_genre_1  (cost=0.00..131.40 rows=6570 width=8) (actual time=0.001..0.248 rows=6589 loops=1)
                                ->  Hash  (cost=1818.34..1818.34 rows=99134 width=9) (actual time=10.938..10.938 rows=99134 loops=1)
                                      Buckets: 131072  Batches: 1  Memory Usage: 5671kB
                                      ->  Seq Scan on liked_movies  (cost=0.00..1818.34 rows=99134 width=9) (actual time=0.020..4.581 rows=99134 loops=1)
Planning Time: 2.044 ms
Execution Time: 115.839 ms
```

### Improvements
No change in plan or performance. 

### Index on movie_id for watched_movies
This index may remove the sequential scan done on watched movies, hence reduce the execution time. 

***Results***
```
Aggregate  (cost=18443.76..18443.80 rows=1 width=72) (actual time=79.936..79.954 rows=1 loops=1)
  CTE movie_in_genre
    ->  HashAggregate  (cost=3907.40..3973.10 rows=6570 width=25) (actual time=12.718..13.429 rows=6589 loops=1)
          Group Key: movies.id
          Batches: 1  Memory Usage: 721kB
          ->  Hash Join  (cost=908.46..3890.98 rows=6570 width=25) (actual time=1.919..11.557 rows=6589 loops=1)
                Hash Cond: (movies.id = movie_genres.movie_id)
                ->  Seq Scan on movies  (cost=0.00..2863.47 rows=45347 width=25) (actual time=0.002..2.318 rows=45347 loops=1)
                ->  Hash  (cost=826.34..826.34 rows=6570 width=8) (actual time=1.897..1.899 rows=6589 loops=1)
                      Buckets: 8192  Batches: 1  Memory Usage: 322kB
                      ->  Bitmap Heap Scan on movie_genres  (cost=75.21..826.34 rows=6570 width=8) (actual time=0.177..1.518 rows=6589 loops=1)
                            Recheck Cond: (genre_id = 21)
                            Heap Blocks: exact=669
                            ->  Bitmap Index Scan on movie_genre_genre_id  (cost=0.00..73.57 rows=6570 width=0) (actual time=0.123..0.123 rows=6589 loops=1)
                                  Index Cond: (genre_id = 21)
  CTE movie_views
    ->  HashAggregate  (cost=5471.49..5473.49 rows=200 width=16) (actual time=13.115..13.478 rows=6535 loops=1)
          Group Key: movie_in_genre_2.movie_id
          Batches: 1  Memory Usage: 737kB
          ->  Nested Loop  (cost=0.42..5286.85 rows=36927 width=16) (actual time=0.038..10.176 rows=32208 loops=1)
                ->  CTE Scan on movie_in_genre movie_in_genre_2  (cost=0.00..131.40 rows=6570 width=8) (actual time=0.000..1.580 rows=6589 loops=1)
                ->  Index Only Scan using idx_watched_movies_movie_id on watched_movies  (cost=0.42..0.72 rows=6 width=8) (actual time=0.001..0.001 rows=5 loops=6589)
                      Index Cond: (movie_id = movie_in_genre_2.movie_id)
                      Heap Fetches: 20
  CTE movie_ratings
    ->  HashAggregate  (cost=4425.73..4428.73 rows=200 width=40) (actual time=19.582..20.546 rows=6154 loops=1)
          Group Key: movie_in_genre_3.movie_id
          Batches: 1  Memory Usage: 1249kB
          ->  Hash Join  (cost=3748.03..4314.81 rows=22185 width=16) (actual time=14.327..17.741 rows=17765 loops=1)
                Hash Cond: (movie_in_genre_3.movie_id = ratings.movie_id)
                ->  CTE Scan on movie_in_genre movie_in_genre_3  (cost=0.00..131.40 rows=6570 width=8) (actual time=0.001..0.283 rows=6589 loops=1)
                ->  Hash  (cost=2228.57..2228.57 rows=121557 width=16) (actual time=14.145..14.145 rows=121557 loops=1)
                      Buckets: 131072  Batches: 1  Memory Usage: 6722kB
                      ->  Seq Scan on ratings  (cost=0.00..2228.57 rows=121557 width=16) (actual time=0.016..6.096 rows=121557 loops=1)
  CTE filtered_ratings
    ->  Subquery Scan on done  (cost=35.93..35.96 rows=1 width=16) (actual time=5.653..5.656 rows=1 loops=1)
          ->  Limit  (cost=35.93..35.95 rows=1 width=24) (actual time=5.652..5.655 rows=1 loops=1)
                ->  WindowAgg  (cost=35.93..39.43 rows=200 width=24) (actual time=5.651..5.653 rows=1 loops=1)
                      ->  Sort  (cost=35.93..36.43 rows=200 width=24) (actual time=5.648..5.650 rows=2 loops=1)
                            Sort Key: m.rank
                            Sort Method: quicksort  Memory: 577kB
                            ->  WindowAgg  (cost=24.79..28.29 rows=200 width=24) (actual time=3.634..4.817 rows=6154 loops=1)
                                  ->  Sort  (cost=24.79..25.29 rows=200 width=16) (actual time=3.629..3.790 rows=6154 loops=1)
                                        Sort Key: m.rank DESC
                                        Sort Method: quicksort  Memory: 529kB
                                        ->  Subquery Scan on m  (cost=11.64..17.14 rows=200 width=16) (actual time=1.233..2.977 rows=6154 loops=1)
                                              ->  WindowAgg  (cost=11.64..15.14 rows=200 width=48) (actual time=1.233..2.707 rows=6154 loops=1)
                                                    ->  Sort  (cost=11.64..12.14 rows=200 width=40) (actual time=1.218..1.480 rows=6154 loops=1)
                                                          Sort Key: movie_ratings_1.movie_avg DESC
                                                          Sort Method: quicksort  Memory: 529kB
                                                          ->  CTE Scan on movie_ratings movie_ratings_1  (cost=0.00..4.00 rows=200 width=40) (actual time=0.001..0.327 rows=6154 loops=1)
  CTE filtered_views
    ->  Subquery Scan on done_1  (cost=35.93..35.96 rows=1 width=16) (actual time=4.480..4.482 rows=1 loops=1)
          ->  Limit  (cost=35.93..35.95 rows=1 width=24) (actual time=4.480..4.481 rows=1 loops=1)
                ->  WindowAgg  (cost=35.93..39.43 rows=200 width=24) (actual time=4.479..4.480 rows=1 loops=1)
                      ->  Sort  (cost=35.93..36.43 rows=200 width=24) (actual time=4.476..4.477 rows=2 loops=1)
                            Sort Key: m_1.rank
                            Sort Method: quicksort  Memory: 601kB
                            ->  WindowAgg  (cost=24.79..28.29 rows=200 width=24) (actual time=2.740..3.903 rows=6535 loops=1)
                                  ->  Sort  (cost=24.79..25.29 rows=200 width=16) (actual time=2.737..2.896 rows=6535 loops=1)
                                        Sort Key: m_1.rank DESC
                                        Sort Method: quicksort  Memory: 550kB
                                        ->  Subquery Scan on m_1  (cost=11.64..17.14 rows=200 width=16) (actual time=0.713..2.127 rows=6535 loops=1)
                                              ->  WindowAgg  (cost=11.64..15.14 rows=200 width=24) (actual time=0.713..1.825 rows=6535 loops=1)
                                                    ->  Sort  (cost=11.64..12.14 rows=200 width=16) (actual time=0.711..0.927 rows=6535 loops=1)
                                                          Sort Key: movie_views_1.views DESC
                                                          Sort Method: quicksort  Memory: 550kB
                                                          ->  CTE Scan on movie_views movie_views_1  (cost=0.00..4.00 rows=200 width=16) (actual time=0.001..0.271 rows=6535 loops=1)
  InitPlan 6 (returns $6)
    ->  CTE Scan on filtered_ratings  (cost=0.00..0.02 rows=1 width=8) (actual time=5.654..5.655 rows=1 loops=1)
  InitPlan 7 (returns $7)
    ->  CTE Scan on filtered_ratings filtered_ratings_1  (cost=0.00..0.02 rows=1 width=8) (actual time=0.000..0.000 rows=1 loops=1)
  InitPlan 8 (returns $8)
    ->  CTE Scan on filtered_views  (cost=0.00..0.02 rows=1 width=8) (actual time=4.481..4.482 rows=1 loops=1)
  InitPlan 9 (returns $9)
    ->  CTE Scan on filtered_views filtered_views_1  (cost=0.00..0.02 rows=1 width=8) (actual time=0.000..0.000 rows=1 loops=1)
  ->  Hash Left Join  (cost=3723.27..4365.03 rows=6570 width=56) (actual time=66.077..68.986 rows=6589 loops=1)
        Hash Cond: (movie_in_genre.movie_id = movie_likeness.movie_id)
        ->  Hash Left Join  (cost=13.00..637.15 rows=6570 width=48) (actual time=49.114..51.299 rows=6589 loops=1)
              Hash Cond: (movie_in_genre.movie_id = movie_ratings.movie_id)
              ->  Hash Left Join  (cost=6.50..384.28 rows=6570 width=16) (actual time=27.441..28.723 rows=6589 loops=1)
                    Hash Cond: (movie_in_genre.movie_id = movie_views.movie_id)
                    ->  CTE Scan on movie_in_genre  (cost=0.00..131.40 rows=6570 width=8) (actual time=12.719..13.113 rows=6589 loops=1)
                    ->  Hash  (cost=4.00..4.00 rows=200 width=16) (actual time=14.709..14.710 rows=6535 loops=1)
                          Buckets: 8192 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 371kB
                          ->  CTE Scan on movie_views  (cost=0.00..4.00 rows=200 width=16) (actual time=13.117..14.275 rows=6535 loops=1)
              ->  Hash  (cost=4.00..4.00 rows=200 width=40) (actual time=21.666..21.666 rows=6154 loops=1)
                    Buckets: 8192 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 353kB
                    ->  CTE Scan on movie_ratings  (cost=0.00..4.00 rows=200 width=40) (actual time=19.584..21.239 rows=6154 loops=1)
        ->  Hash  (cost=3707.77..3707.77 rows=200 width=24) (actual time=16.955..16.957 rows=5896 loops=1)
              Buckets: 8192 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 387kB
              ->  Subquery Scan on movie_likeness  (cost=3703.77..3707.77 rows=200 width=24) (actual time=16.010..16.599 rows=5896 loops=1)
                    ->  HashAggregate  (cost=3703.77..3705.77 rows=200 width=24) (actual time=16.009..16.357 rows=5896 loops=1)
                          Group Key: movie_in_genre_1.movie_id
                          Batches: 1  Memory Usage: 993kB
                          ->  Hash Join  (cost=3057.52..3560.55 rows=19096 width=9) (actual time=11.955..14.544 rows=14519 loops=1)
                                Hash Cond: (movie_in_genre_1.movie_id = liked_movies.movie_id)
                                ->  CTE Scan on movie_in_genre movie_in_genre_1  (cost=0.00..131.40 rows=6570 width=8) (actual time=0.001..0.286 rows=6589 loops=1)
                                ->  Hash  (cost=1818.34..1818.34 rows=99134 width=9) (actual time=11.772..11.772 rows=99134 loops=1)
                                      Buckets: 131072  Batches: 1  Memory Usage: 5671kB
                                      ->  Seq Scan on liked_movies  (cost=0.00..1818.34 rows=99134 width=9) (actual time=0.019..4.840 rows=99134 loops=1)
Planning Time: 1.286 ms
Execution Time: 80.799 ms
```

### Improvements
The new index on watched_movies removes the original sequential scan on watched_movies and replaces it with an index scan and improved execution time. No additional indices were creaated for liked_movies, ratings, or movies since they scan the entire table already and would provide no improvements. 

## New Results Improvements

### Get_Recommend
1. 0.4496 s

Minor improvement, but this is probably because most of the execution time is a result of matrix multiplication rather than the query itself.

### Create_Prediction
1. 0.2169 s

Small improvement, since similar to Get_Recommended, matrix multiplication occurs, but on a smaller scale.

### Get_Genre_Analytics
1. 0.0778 s

Sizable improvement, since this endpoint execution time is almost entirely dependent on the query.