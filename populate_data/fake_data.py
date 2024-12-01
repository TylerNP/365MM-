import os 
import dotenv
import sqlalchemy
from sqlalchemy import create_engine
from faker import Faker
import numpy as np
import random

def generate_scaled_interaction_distribution(sum : int) -> dict[str,int]:
    distribution = np.random.default_rng().exponential(1, 3)
    scaled_distribution = sum * distribution / distribution.sum()
    output = {}
    output["watched"] = round(scaled_distribution[0])
    output["saved"] = round(scaled_distribution[1])
    output["liked"] = round(scaled_distribution[2])//2
    output["rated"] = round(scaled_distribution[2]) - output["liked"]
    return output

def generate_genre_distribution(n : float, p : float, limit : int) -> int:
    while True:
        value = np.random.default_rng().negative_binomial(n,p)
        if value <= limit:
            return value

def insert_user_interaction_scores(
    table : str, 
    user_id : int, 
    other_ids : list[int], 
    other_id_name : str, 
    score_name : str, 
    score_val : list[any], 
    score_prob : list[float],
    connection : sqlalchemy.Engine
) -> None:
    for id in other_ids:
        sql_to_execute = f"INSERT INTO {table} (user_id, {other_id_name}, {score_name}) VALUES (:user_id, :id, :score)"
        values = {"user_id": user_id, "id":id, "score": np.random.choice(score_val, 1, p = score_prob).item()}
        connection.execute(sqlalchemy.text(sql_to_execute), values)

def insert_user_interaction(
    table : str, 
    user_id : int, 
    other_ids : list[int], 
    other_id_name : str, 
    connection : sqlalchemy.Engine
) -> None:
    for id in other_ids:
        sql_to_execute = f"INSERT INTO {table} (user_id, {other_id_name}) VALUES (:user_id, :id)"
        values = {"user_id": user_id, "id":id}
        connection.execute(sqlalchemy.text(sql_to_execute), values)
        

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True, use_insertmanyvalues=True)

genres = []
movie_ids = []
with engine.begin() as connection:
    # Populate genre info
    results = connection.execute(sqlalchemy.text("SELECT genres.id FROM genres ORDER BY genres.id"))
    for result in results:
        genres.append(result.id)
    movies = connection.execute(sqlalchemy.text("SELECT movies.id FROM movies ORDER BY movies.id"))
    for movie in movies:
        movie_ids.append(movie.id)

fake = Faker()

num_cast = 1000
movie_in_sample_distribution = np.random.default_rng().negative_binomial(1, 0.02, num_cast) # ~ 49 average movies for every cast member
with engine.begin() as connection:
    for i in range(num_cast):
        sql_to_execute = """
            INSERT INTO cast_and_crew (firstname, lastname) VALUES (:first, :last) RETURNING cast_and_crew.id
        """
        name = {"first": fake.first_name(), "last": fake.last_name()}
        cast_id = connection.execute(sqlalchemy.text(sql_to_execute), name).scalar_one()
        movies = random.sample(movie_ids, movie_in_sample_distribution[i])
        for movie in movies:
            sql_to_execute = """
                INSERT INTO roles (movie_id, cast_id, role) VALUES (:movie, :cast_id, :role)
            """
            role = {"movie": movie, "cast_id": cast_id, "role": "Actor"}
            connection.execute(sqlalchemy.text(sql_to_execute), role)

# Streaming Services
num_services = 15
services_sample_distribution = np.random.default_rng().negative_binomial(500, 0.2, num_services)

with engine.begin() as connection:
    for i in range(num_services):
        sql_to_execute = "INSERT INTO streaming_services (name) VALUES (:name) RETURNING streaming_services.id"
        service_id = connection.execute(sqlalchemy.text(sql_to_execute), {"name":fake.word()+str(np.random.randint(0,100))} ).scalar_one()
        movies = random.sample(movie_ids, services_sample_distribution[i])
        for movie in movies:
            sql_to_execute = "INSERT INTO available_streaming (service_id, movie_id) VALUES (:service, :movie)"
            connection.execute(sqlalchemy.text(sql_to_execute), {"service": service_id, "movie": movie})

# Create Groups
num_groups = 4000
group_members_sample_distribution = np.random.default_rng().negative_binomial(1, 0.05, num_groups)
groups = []

with engine.begin() as connection:
    for i in range(num_groups):
        name = fake.sentence()
        desc = fake.paragraph()
        sql_to_execute = """
            INSERT INTO groups (name, description) VALUES (:name, :desc) RETURNING groups.id
        """
        group_id = connection.execute(sqlalchemy.text(sql_to_execute), {"name": name, "desc": desc}).scalar_one()
        groups.append((group_id, group_members_sample_distribution[i]))
        group_genres = random.sample(genres, generate_genre_distribution(1, 0.25, len(genres)))
        for genre in group_genres:
            sql_to_execute = """
                INSERT INTO liked_genres_groups (genre_id, group_id, score) VALUES (:genre, :group_id, :score)
            """
            score_scale = [x for x in range(11)]
            score_prob = [0.0104, 0.0104, 0.0208, 0.0312, 0.052, 0.0833, 0.1041, 0.1562, 0.1883, 0.2308, 0.1125]
            liked = {"genre": genre, "group_id": group_id, "score": np.random.choice(score_scale, 1, p=score_prob).item()}
            connection.execute(sqlalchemy.text(sql_to_execute), liked)
            
num_users = 50000
movie_interaction_sample_distribution = np.random.default_rng().negative_binomial(1, 0.07, num_users) # ~ 14 interactions
user_ids = []

with engine.begin() as connection:
    for i in range(num_users):
        sql_to_execute = "INSERT INTO users (username) VALUES (:name) RETURNING users.id"
        username = {"name": fake.name()+fake.name()+str(np.random.randint(0,999999))}
        user_id = connection.execute(sqlalchemy.text(sql_to_execute), username).scalar_one()
        user_ids.append(user_id)
        interaction_types = generate_scaled_interaction_distribution(movie_interaction_sample_distribution[i])
        score_scale = [x for x in range(11)]
        user_genres = random.sample(genres, generate_genre_distribution(1, 0.3, len(genres)))
        genre_score_prob = [0.0104, 0.0104, 0.0208, 0.0312, 0.052, 0.0833, 0.1041, 0.1562, 0.1883, 0.2308, 0.1125]
        insert_user_interaction_scores("liked_genres", user_id, user_genres, "genre_id", "score", score_scale, genre_score_prob, connection)
        liked = random.sample(movie_ids, interaction_types["liked"])
        like_scale = [True, False]
        like_prob = [0.35, 0.65]
        insert_user_interaction_scores("liked_movies", user_id, liked, "movie_id", "liked", like_scale, like_prob, connection)
        saved = random.sample(movie_ids, interaction_types["saved"])
        insert_user_interaction("saved_movies", user_id, saved, "movie_id", connection)
        watched = random.sample(movie_ids, interaction_types["watched"])
        insert_user_interaction("watched_movies", user_id, saved, "movie_id", connection)
        rated = random.sample(movie_ids, interaction_types["rated"])
        rating_score_prob = [0.01, 0.01, 0.02, 0.03, 0.05, 0.10, 0.15, 0.20, 0.25, 0.12, 0.06]
        insert_user_interaction_scores("ratings", user_id, rated, "movie_id", "rating", score_scale, rating_score_prob, connection)

# Add users to groups
with engine.begin() as connection:
    for group in groups:
        group_id = group[0]
        users_in_group = random.sample(user_ids, group[1])
        group_roles = ["Member"]*group[1]
        if group[1] > 0:
            group_roles[0] = "Owner"
        i = 0
        for user in users_in_group:
            sql_to_execute = "INSERT INTO groups_joined (user_id, group_id, role) VALUES (:user_id, :group_id, :role)"
            user_join = {"user_id": user, "group_id": group_id, "role": group_roles[i]}
            connection.execute(sqlalchemy.text(sql_to_execute), user_join)
            i += 1

with engine.begin() as connection:
    sql_to_execute = """
        with info AS (
            SELECT DISTINCT 
                FIRST_VALUE(cast_id) OVER (PARTITION BY roles.movie_id ORDER BY roles.cast_id) AS cast_id, 
                movie_id AS movie_id 
            FROM 
                roles 
            ORDER BY 
                movie_id
        )

        UPDATE 
            roles 
        SET 
            role = 'Director' 
        WHERE EXISTS (
            SELECT 
                1 
            FROM 
                info 
            WHERE 
                roles.movie_id = info.movie_id 
                AND roles.cast_id = info.cast_id
        );
    """
    connection.execute(sqlalchemy.text(sql_to_execute))
