import subprocess
import pandas as pd
import re
import subprocess
import sqlite3
import numpy as np



status = {
    "task_name": None,
    "pid": None,
    "progress": 0,
    "result": None,
    "running": False
}




def UpdatePlaylist(m3u_url, pl_name, db_name):
    """
    The function to handle the download latest playlist from iptv service provider and convert it in 
    SQLite database for efficiency.    
    """
    
    global status
    
    status["task_name"] = "updating playlist"
    status["running"] = True

    command = ["curl", "-o", pl_name, m3u_url]

    process = subprocess.Popen(command, stderr=subprocess.PIPE, text=True)
    status["pid"] = process.pid  # Store the PID of the process

    while True:
        line = process.stderr.readline()
        if not line:
            break
        
        print(f"Raw output: {line.strip()}")

        status["result"] = line.strip()  # Update the result with the latest output
        status["progress"] += 10  # Update progress (this is a placeholder, adjust as needed)

    process.wait()  # Wait for the process to finish

    print(f"  * File saved in {pl_name}")

    status["result"] = "Task Completed"
    status["progress"] = 100  # Mark progress as 100% when complete
    status["running"] = False



    ##
    ## Creating the SQLite DataBase
    ##
    
    paired_rows = []
    data = []

    print(f"""  > Creating database {db_name}""")

    status["task_name"] = "Updating DB"
    status["progress"] = 0  # Mark progress as 100% when complete
    status["running"] = True


    # first row pattern for saving playlist
    row0 = """#EXTM3U"""

    # Open and read the text file
    with open(pl_name, 'r') as file:
        lines = file.readlines()

        for i in range(1, len(lines), 2):     
            if i + 1 < len(lines):
                # Process the pair of rows
                row1 = lines[i].strip()

                # Define a regular expression pattern to extract values
                pattern = re.compile(r'tvg-id="([^"]*)" tvg-name="([^"]*)" tvg-logo="([^"]*)" group-title="([^"]*)"')
                match = pattern.search(row1)

                # Check if there is a match
                if match:
                    tvg_id = match.group(1)
                    tvg_name = match.group(2)
                    tvg_logo = match.group(3)
                    group_title = match.group(4)

                row2 = lines[i + 1].strip()
                st_uri = row2
                row2 = '\n' + row2

                match = re.search(r'(?<=- ).*?(?=\()', tvg_name)
                if match:
                    vod_name = match.group(0).rstrip()

                else:
                    vod_name = None


                row_data = {
                    'tvg_id': tvg_id, 
                    'tvg_name': tvg_name,
                    'tvg_logo': tvg_logo,
                    'vod_name': vod_name,
                    'group_title': group_title,
                    'row1': row1,
                    'row2': row2,
                    'st_uri': st_uri,
                    }


                status["task_name"] = "Updating DB"
                status["progress"] = 50  # Mark progress as 100% when complete
                status["running"] = True

                # Append the dictionary to the list
                data.append(row_data)
                                                                               
        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(data)
       
        # Define the file extensions
        file_extensions = ['.mp4', '.mov', '.avi', '.m4v', '.mkv', '.mp3' ]
        df['st_type'] = np.where(df['row2'].str.contains('|'.join(file_extensions)), 'VOD', 'LIV')
        
        df['to_download_ind'] = 0 

        # Create a schema group_name
        df_group = df.group_title.value_counts().reset_index()
        df_group['to_keep_ind'] = 0

        db_table = "smartersiptv"

        # SQLite database connection
        conn = sqlite3.connect(db_name)  
        df.to_sql(db_table, conn, index=True, if_exists='replace') 
        df_group.to_sql( 'categories', conn, index=True, if_exists='replace')
        conn.close()

        status["result"] = "Task Completed"
        status["progress"] = 100  # Mark progress as 100% when complete
        status["running"] = False

    return status





def DownloadVod(file_url, file_nm):
    """
    The function to handle the download latest playlist from iptv service provider and convert it in 
    SQLite database for efficiency.    
    """  

    global status

    status["task_name"] = "Downloading VOD from IPTV"
    status["running"] = True
    status["progress"] = 0
    status["result"] = None

    command = ['wget', '-O', file_nm, file_url]

    process = subprocess.Popen(command, stderr=subprocess.PIPE, text=True)
    status["pid"] = process.pid  # Store the PID of the process

    while True:
        line = process.stderr.readline()
        if not line:
            break
        
        print(f"Raw output: {line.strip()}")

        status["result"] = line.strip()  # Update the result with the latest output
        status["progress"] += 10  # Update progress (this is a placeholder, adjust as needed)

    process.wait()  # Wait for the process to finish

    status["result"] = "Task Completed"
    status["progress"] = 100  # Mark progress as 100% when complete
    status["running"] = False

    return status

    





def BuildMovieDB():
    """
    This function is building the SQLite table recommendation engine and scores. 
    Need to be improved. Ex: TV like Silicon valley is not there. 
    """  

    global status

    status["task_name"] = "Building Reco Engien"
    status["running"] = True
    status["progress"] = 0
    status["result"] = None

    api_key = 'da835367527db6ee192714cc83849e02'

    d = '2010-01-01'
    number = 7  # Minimum movie score
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

    return()