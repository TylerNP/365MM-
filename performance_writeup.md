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
1. 200.8101 s

# Performance Tuning
Top 3 Slowest Endpoints:
    - Get_recommended (200.8101s)
    - Create_Prediction (0.3141s)
    - Get_Genre_Analytics (0.1098s)

## Get_Recommended

### First Query
```
EXPLAIN
SELECT 
    user_id, movie_id, rating 
FROM 
    ratings 
ORDER BY 
    user_id, rating  
```