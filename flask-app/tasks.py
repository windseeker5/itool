import subprocess
import pandas as pd
import re
import sqlite3
import numpy as np
import requests
import sys, os , datetime
from tqdm import tqdm
from time import sleep
import psutil
import json
import time
import ffmpeg
from datetime import datetime
import yaml

from rq import Queue
from redis import Redis


status = {
    "task_name": None,
    "pid": None,
    "progress": 0,
    "result": None,
    "running": False
}





def GetUserSession():
 
    # Command to run
    command = "ss -Ht sport = :8080 | grep -c 'ESTAB'"

    # Run the command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Check the result
    if result.returncode == 0:
        # Convert the output to an integer
        count = int(result.stdout.strip())
    else:
        print("Error message:")
        count = ''
        print(result.stderr)
    return(count)



def LoadConfig():
    """
    This function loading user config from config.yml file
    """
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
        
        status["result"] = line.strip()  # Update the result with the latest output
        status["progress"] += 10  # Update progress (this is a placeholder, adjust as needed)

    process.wait()  # Wait for the process to finish
    status["running"] = False

    return status




def BuildMovieDB():
    """
    This function is building the SQLite table recommendation engine and scores. 
    Need to be improved. Ex: TV like Silicon valley is not there. 
    """  

    global status

    status["task_name"] = "Building Reco Engine"
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

            status["progress"] = i
            status["result"] = i

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

    status["result"] = "Task Completed"
    status["progress"] = 100  # Mark progress as 100% when complete
    status["running"] = False

    return status



def GetKpi(db):
    """
    This function is retrieving service provider KPI from SQLite table
    """  

    filename = os.path.basename(db)

    # Get the creation time of the file
    creation_time = os.path.getctime(db)

    # Convert creation time to datetime object
    creation_datetime = datetime.utcfromtimestamp(creation_time)

    # Format the datetime object as CCYYMMdd
    cr_tm = creation_datetime.strftime('%Y/%m/%d')

    # Connect to the SQLite database
    conn = sqlite3.connect(db)

    # Create a cursor object using the cursor() method
    cursor = conn.cursor()

    # Get total steam assets
    SQL = """SELECT count(*) 
    FROM smartersiptv"""
    cursor.execute(SQL)
    asset = cursor.fetchone()[0]

    # Get categories
    SQL = """SELECT COUNT(DISTINCT group_title) 
    FROM smartersiptv"""
    cursor.execute(SQL)
    categories = cursor.fetchone()[0]

    # Get live channels
    SQL = """SELECT COUNT(tvg_name) 
    FROM smartersiptv
    WHERE st_type  = 'LIV'"""
    cursor.execute(SQL)
    liv = cursor.fetchone()[0]

    # Get vod streams
    SQL = """SELECT COUNT(tvg_name) 
    FROM smartersiptv
    WHERE st_type  = 'VOD'"""
    cursor.execute(SQL)
    vod = cursor.fetchone()[0]

    kpi = { 'dbname' : filename, 
            'cr_tm' : cr_tm,
            'asset': asset,
            'categories': categories,
            'liv': liv,
            'vod': vod }

    # Close the connection
    conn.close()
    return(kpi)



def GetStreamName():
    
    flag_file = "ffmpeg_proc.pid"
    if os.path.exists(flag_file):
        with open(flag_file, "r") as file:
            st_nm = file.readline()
    else:
        st_nm = None
    return(st_nm)





def GetFfmpegPid():
    pid_list = []

    # Find all running processes that contain 'ffmpeg' in their name
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'ffmpeg' in process.info['name'] or any('ffmpeg' in arg for arg in process.info['cmdline']):
            pid_list.append(process.pid)
    return(pid_list)




def start_ffmpeg_liv(url):
    # New bog with audio codec issue
    # ffmpeg -i input_file -c:v copy -c:a aac -b:a 128k output.flv

    return subprocess.Popen(['ffmpeg', '-v', 'verbose', 
            '-thread_queue_size', '4096', '-i', url,
            '-c:v', 'copy', '-c:a', 'aac', '-f', 'flv', 'rtmp://127.0.0.1/live/live'])



def start_ffmpeg_vod(url):
    return subprocess.Popen(['ffmpeg', '-re', '-i', url, 
            '-c:v', 'copy', '-c:a', 'aac', '-f', 'flv', 'rtmp://127.0.0.1/live/live'])   




def ffmpeg_should_continue():
    flag_file = "ffmpeg_proc.pid"
    return os.path.exists(flag_file)




def ReStream(type, url):

    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:

        if type =="LIV":
            ffmpeg_process = start_ffmpeg_liv(url)

            # Get the process ID (PID) of the ffmpeg process
            pid = str(ffmpeg_process.pid)
            print(f'ffmpeg PID is {pid}')


        if type =='VOD':
            # Start the ffmpeg process
            ffmpeg_process = start_ffmpeg_vod(url)

            # Get the process ID (PID) of the ffmpeg process
            pid = str(ffmpeg_process.pid)
            print(f'ffmpeg PID is {pid}')

        while True:
            if ffmpeg_process.poll() is not None or not ffmpeg_should_continue():
                retry_count += 1
                break
            time.sleep(5)  

        if retry_count >= max_retries:
            break

    return(pid)




def KillProc(pid_str):

    flag_file = "ffmpeg_proc.pid"

    # Check if the file exists before trying to delete it
    if os.path.exists(flag_file):
        os.remove(flag_file)
        print(f"File '{flag_file}' has been deleted.")
    else:
        print(f"File '{flag_file}' does not exist.")

    # Send SIGTERM signal to the process
    # Convert the PID string to an integer
    pid = int(pid_str)
    p = os.kill(pid, 15)

    # Add a delay of 3 seconds
    time.sleep(3)


    # List all files in the directory
    files = os.listdir('/nginx/hls/')

    # Delete each file in the directory
    for file in files:
        file_path = os.path.join('/nginx/hls/', file)
        os.remove(file_path)

    return(p)
    #return

