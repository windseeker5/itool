import json
import requests
import pandas as pd
import sys, os , datetime
from tqdm import tqdm
from time import sleep
import sqlite3


api_key = 'da835367527db6ee192714cc83849e02'

d = '2010-01-01'
number = 6  # Minimum movie score
qt_movie = 500  # This mean 10 page of 20 movies 



# Function to map a list of genre IDs to genre names
def map_ids_to_genres(genre_ids):
    return [genre_dict.get(genre_id, 'Unknown') for genre_id in genre_ids]



##
## Retreive movies genre liste from TMDB
##

url = "https://api.themoviedb.org/3/genre/movie/list?language=en"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkYTgzNTM2NzUyN2RiNmVlMTkyNzE0Y2M4Mzg0OWUwMiIsInN1YiI6IjY1YzdiZDQ0YjZjZmYxMDE2NGE0ZjY3MiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.gNjAz5H6uYtoO3YT80t82HDVOdnCr4hkVnmuxcykFpQ"
}

response = requests.get(url, headers=headers)

data = response.json()
genre_list = data['genres']

# Convert the list of dictionaries into a dictionary mapping genre IDs to genre names
genre_dict = {genre['id']: genre['name'] for genre in genre_list}


##
## Retreiving last 1000 movie with with pre-filters
##

# We will first create an empty dataframe to store all the movie detail
df = pd.DataFrame()

# Our for loop will iterate through each page, get json data convert it into dataframe and append it to original dataframe 

print("> Downloading  Movies info...")
print("")

for i in tqdm(range(1, qt_movie )):

        url = f'https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US\
        &page={i}&primary_release_date.gte={d}&sort_by=popularity.desc&vote_average.gte={number}&vote_count.gte=50&api_key={api_key}'

        response = requests.get(url)
        temporary_df = pd.DataFrame(response.json()['results'])
        df = pd.concat([df, temporary_df],ignore_index=True)



##
## Downloading additional info fro each df movie in database
##

# Creating an empty database with required columns
details_df = pd.DataFrame(columns=['id','budget','production_companies','revenue','runtime','tagline'])

counter_to_sleep=1

print("> Downloading movies additional information per movie...")
print("")

# We are using try,catch block to catch exceptions if anything goes wrong.
try:

    for i in tqdm(df.id.values):
    # for i in df.id.values:
        url = f'https://api.themoviedb.org/3/movie/{i}?api_key={api_key}'
        response = requests.get(url)
        data = response.json()
        new_row = {
                    'id' : i,
                    'budget' : data['budget'],
                    'production_companies' : [i.get('name') for i in data['production_companies']],
                    'revenue' : data['revenue'],
                    'runtime' : data['runtime'],
                    'tagline' : data['tagline']
                    }
        details_df.loc[len(details_df)] = new_row
        
        counter_to_sleep+=1
        
        # we ask thread to sleep after every 40 iterations
        if counter_to_sleep%40==0: sleep(1)
            
except Exception as e:
    logging.error(traceback.format_exc())


print("> Merging datasets")

merged_df = pd.merge(df,details_df,on="id",how="inner")


# Export DataFrame to Excel
# merged_df.to_excel('output.xlsx', index=False)

df = merged_df.copy()

# Add image column to the dataframe
df['poster_img'] = "https://image.tmdb.org/t/p/w500" + df['poster_path'] 

# Create a new column 'genres' by mapping lists of genre IDs to genre names
df['genres'] = df['genre_ids'].apply(map_ids_to_genres)

# Convert list column to JSON string
df['production_companies'] = df['production_companies'].apply(json.dumps)
df['genre_ids'] = df['genre_ids'].apply(json.dumps)
df['genres'] = df['genres'].apply(json.dumps)


df['release_date'] = pd.to_datetime(df['release_date'], format='%Y-%m-%d')


print("> Saving to as Sqlite database")

# Connect to SQLite database
conn = sqlite3.connect('iptv_data/smartersiptv.db')

# Save DataFrame to SQLite
df.to_sql('movies', conn, index=False, if_exists='replace')

# Close the connection
conn.close()