import re
import pandas as pd
import subprocess
import sqlite3
import numpy as np
import pyfiglet
import csv
import socket
import yaml
import time
import shlex
import random
import subprocess
import psutil
import json
import requests
import sys, os , datetime
from tqdm import tqdm
from time import sleep




def download_video(file_url, file_nm):
    # Define the wget command to download the video
    linux_command = ['wget', '-O', file_nm, file_url]

    # Use subprocess to run the command
    subprocess.run(linux_command)



def BuildMovieDB():
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






def Header(video_cnt, rst_info):
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    os.system('clear')
    title = pyfiglet.figlet_format("ITOOL", font = "isometric1" ) 
    print(title) 
    print(f"~ ip:{ip_address} | Streams:{video_cnt} | Restreaming:{rst_info}")
    print("")

    return(ip_address)


def LoadConfig():

    config_file = "config.yml"

    if os.path.exists(config_file):
        print(f"The file {config_file} exists.")

        # loading config from confi.yml file
        with open("config.yml","r") as file_object:
            config = yaml.load(file_object,Loader=yaml.SafeLoader)

        # Extract the schema from filename
        db_schema = config['db_file'].split("/")[-1].split(".db")[0]
        config["db_schema"] = db_schema

    else:
        print(f"""\n  > The file {config_file} does not exist! \n  > You need to create a config.yml with your setings\n""")
        sys.exit()

    return(config)


def BuidlRunDocker(DockerfilePath):
    # Change the working directory to a different folder
    print(f"  > Changing to path {DockerfilePath}")
    os.chdir(DockerfilePath)

    print("  > Run docker Redis server localy...")
    # docker run --name my-redis -p 6379:6379 -d redis
    command = ["docker", "run", "--name", "my-redis", "-p", "6379:6379", "-d", "redis"]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        # Handle errors, if any
        print(f"Error: {e}")


    print("  > Building the Docker image...take few minutes...")
    # docker build -t kdc-nginx-rtmp .
    command = ["docker", "build", "-t", "kdc-nginx-rtmp", "."]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        # Handle errors, if any
        print(f"Error: {e}")


    print("  > run -d -p 1935:1935 -p 8080:8080 --name kdc-nginx-rtmp  ..take few minutes...")
    # docker run -d -p 1935:1935 -p 8080:8080 --name kdc-nginx-rtmp kdc-nginx-rtmp
    command = ["docker", "run", "-d", "-p", "1935:1935", "-p", "8080:8080", "--name", "kdc-nginx-rtmp", "kdc-nginx-rtmp"]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        # Handle errors, if any
        print(f"Error: {e}")


    return()



def DowloadPlaylist(m3u_url, pl_name):
    
    url = m3u_url
    output_file = pl_name

    # Use the -o option to specify the output file
    command = ["curl", "-o", output_file, url]

    print("  > Downloading your playlist...take few minutes...")
    # Run the curl command
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        # Handle errors, if any
        print(f"Error: {e}")
    
    print(f"  * File saved in {pl_name}")
    return(pl_name)



def PlaylistToDb(pl_file, db_file, db_table ):
    global video_cnt
    file_path = pl_file
    paired_rows = []
    data = []

    print(f"""  > Creating database {db_file}""")

    # first row pattern for saving playlist
    row0 = """#EXTM3U"""

    # Open and read the text file
    with open(file_path, 'r') as file:
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


        # SQLite database connection
        conn = sqlite3.connect(db_file)  
        df.to_sql(db_table, conn, index=True, if_exists='replace') 
        df_group.to_sql( 'categories', conn, index=True, if_exists='replace')
        conn.close()

        df.to_pickle('df_playlist.pkl')
        

        ##
        ## Add stats from database and next steps to filter group befrore export
        ##

        video_cnt = df.shape[0]
        video_group_cnt = df_group.shape[0]
        TYPE_CNT = df.st_type.value_counts()

        VOD = TYPE_CNT['VOD']
        LIV = TYPE_CNT['LIV']

        d = dict()
        d['stream'] = video_cnt
        d['vod'] = VOD
        d['liv'] = LIV

        print(" ")
        print(f"    * Video assets imported : {video_cnt}")
        print(f"    * VOD assets : {VOD}")
        print(f"    * Live streams : {LIV}" )
        print(f"    * Group categories : {video_group_cnt}" )

        return(d)



def ExportPlaylist(export_file, db_file, db_table, ip):
    df = pd.read_pickle('df_playlist.pkl')

    # Cleaning unwanted categories     
    print ('  > Cleaning unwanted categories...')
    
    SQL = f"""WITH M AS (
    SELECT group_title, count, to_keep_ind
    FROM categories
    WHERE group_title LIKE 'ENGLISH%' OR 
          group_title LIKE 'FRANCE%' OR 
          group_title LIKE 'NETFLIX%SERIES%' OR 
          group_title LIKE 'QUEBEC%' OR 
          group_title LIKE 'EN -%' OR 
          group_title LIKE 'APPLE+%' OR 
          group_title LIKE 'FR -%' OR 
          group_title LIKE 'AMAZON%' OR 
          group_title LIKE 'QUÉBEC%' OR 
          group_title LIKE 'CA|%' OR 
          group_title LIKE 'QC %' OR 
          group_title LIKE '%QMJHL%'
),
Filtered AS (
    SELECT *
    FROM M
    WHERE group_title NOT LIKE '%KIDS%' AND
          group_title NOT LIKE '%ENFANTS%' AND
          group_title NOT LIKE '%ANIMATION%' AND
          group_title NOT LIKE '%FOX%' AND
          group_title NOT LIKE '%WWE%' AND
          group_title NOT LIKE '%ANIME%' AND
          group_title NOT LIKE '%Biblical%' AND
          group_title NOT LIKE '%MUSIC%' AND
          group_title NOT LIKE '%MUSIQUE%' AND
          group_title NOT LIKE '%BOXING%' AND
          group_title NOT LIKE '%CFL%'
)
UPDATE categories
SET to_keep_ind = 1
WHERE group_title IN (SELECT group_title FROM Filtered);"""

    conn = sqlite3.connect(db_file)  # Replace 'your_database.db' with your database file
    cursor = conn.cursor()
    cursor.execute(SQL)

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()


    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)  # Replace 'your_database.db' with your database file

    # Write your SQL query
    SQL= f"""SELECT group_title,
                    count,
                    to_keep_ind
              FROM {db_table}
              WHERE to_keep_ind = 1""" 
         

    # Read data from SQLite into a DataFrame
    df_group = pd.read_sql(SQL, conn)
    conn.close()

    print("")
    print("  * TOP 10 Categories :")
    print("")
    print(df_group.head(10))

    # Merging df with dg_group
    df_f = pd.merge(df, df_group, on='group_title', how='left')

    ##
    ## Filtering unwanted streaming from my export playlist
    ##

    df_f = df_f[ df_f['to_keep_ind']==1 ].copy()

    df_f['out_format'] = df_f['row1'] + df_f['row2']

    df_f['out_format'].to_csv( "export_file.tmp", 
                               index=False, 
                               header=None, 
                               escapechar='~', 
                               quoting=csv.QUOTE_NONE)
    
    ##
    ## Adding row0 as the header of the exported playlist
    ##
    print("")
    print(f"   > Writing your playlist {export_file}")

    # Open the file in read mode to read the existing content
    with open("export_file.tmp", 'r') as file:
        existing_content = file.read()

    # Open the file in write mode to add a line at the top
    with open("export_file.tmp", 'w') as file:
        new_line = f"""#EXTM3U\n#EXTINF:-1 tvg-id="" tvg-name="CA: KD Sport Live" tvg-logo="http://{ip}:8000/kdcmedia.jpg" group-title="CA| DRESDELL HD",CA: KD Live\nhttp://tv.dresdell.com:8080/hls/live.m3u8\n"""
        file.write(new_line + existing_content)
        # Adding my own streaming or restreaming server


    with open("export_file.tmp", 'r') as infile, open(export_file, 'w') as outfile:
        for line in infile:
            # Replace '~' with nothing
            updated_line = line.replace('~', '')
            # Write the updated line to the output file
            outfile.write(updated_line)
    
    # Delete tmp file
    os.remove("export_file.tmp")

    return()







def ReStream(url):
    print(f"""  > Restreaming {url} to local server...""")
    
    command = ["ffmpeg", "-i", url, "-c", "copy", "-f", "flv", "rtmp://127.0.0.1/live/sport"]
 
    try:
        # Start the ffmpeg process
        process = subprocess.Popen(command)
        # Retrieve the PID of the ffmpeg process
        pid = process.pid
        print(f"  > ffmpeg PID: {pid}")

        # Wait for the process to finish
        process.wait()
    except subprocess.CalledProcessError as e:
        # Handle errors, if any
        print(f"Error: {e}")

    return(pid)





def RandomStream(db_file, db_table):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)  # Replace 'your_database.db' with your database file

    ##
    ## Few Question to build the SQL query and filter selection
    ##

    print(" > What type of streaming your are looking for: 1=>live chanel 2=> Video on demand ) ?")
    choice = input("   Enter Choice > ")
    choice = choice.strip()
            
    # MENU OPTION 1
    if (choice == "1"):
        print('   * Setting query for live streaming....')
        vodtype = 'LIV'
    else:
        vodtype = 'VOD'


    print(" > What categories are looking for ? Here are the top 25 ....")

    SQL = """SELECT 
    group_title,
    count
    from categories limit 26"""

    df_cat = pd.read_sql(SQL, conn)

    print("")
    print(f"   {df_cat}")
    print("")

    choice = input("   Enter your category > ")
    vodcat = choice.strip()

    print("")
    choice = input("   Enter your filters for stream name  > ")
    filters = choice.strip()


    filters_list = filters.split()

    # Build the string using a list comprehension and join
    filters_string = ' OR '.join([f"tvg_name like '%{item}%'" for item in filters_list])

    # Add the necessary parentheses if needed
    final_string = f"({filters_string})"

    SQL = f"""SELECT st_uri, tvg_name FROM {db_table} WHERE st_type = '{vodtype}' AND group_title LIKE '%{vodcat}%'
    AND ( {filters_string} )"""

    df_rdm = pd.read_sql(SQL, conn)
    conn.close()

    print("")
    print("  * Your SQL Query :")
    print('')
    print(SQL)

    stat = df_rdm.shape[0]
    print(f"  > Your Query Result : {stat}")

    vod_list = df_rdm['st_uri'].tolist()

    for i in range(0, stat):
        print(i)

        random_item = random.choice(vod_list)

        # Remove the selected item from the list
        vod_list.remove(random_item)

        print(" > Playing a random video asset from your Query....")
        print("   * Random item:", random_item)

        # Define the mpv command with options (e.g., --no-fullscreen)
        mpv_command = ['mpv', '--no-fullscreen', '--start=00:05:00', random_item]

        # Use subprocess to run the mpv command
        subprocess.run(mpv_command)







def BatchDownload(db_file, db_table, folder):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)  

    print(" > Looking for VOD flag as to_dowload in database....")

    SQL = f"""SELECT tvg_name, st_uri
             FROM {db_table}
             WHERE  to_download_ind = 1"""

    df_down = pd.read_sql(SQL, conn)

    print("")
    print(f"   {df_down}")
    print("")

    max_item = df_down.shape[0]

    for i in range(0, max_item):

        file_type = df_down.iloc[i]['st_uri']
        file_extension = os.path.splitext(file_type)[1]

        file_nm = folder + "/" + df_down.iloc[i]['tvg_name'] + file_extension
        file_url = df_down.iloc[i]['st_uri']

        print("")
        print(f"""  > Downloading VOD {i}/{max_item} |  {file_nm}...""")
        print("")

        # Define the mpv command with options (e.g., --no-fullscreen)
        linux_command = ['wget', '-O', file_nm, file_url]

        # Use subprocess to run the mpv command
        subprocess.run(linux_command)
        
    return(df_down)


