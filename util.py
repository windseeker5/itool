import re
import pandas as pd
import subprocess
import sqlite3
import numpy as np
import pyfiglet
import sys
import csv
import datetime
import os
import socket
import yaml


 
def Header(video_cnt):
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    os.system('clear')
    title = pyfiglet.figlet_format("ITOOL", font = "isometric1" ) 
    print(title) 
    print(f"~ ip : {ip_address}      Edit > config.yml      Streams : {video_cnt}")
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

                row_data = {
                    'tvg_id': tvg_id, 
                    'tvg_name': tvg_name,
                    'tvg_logo': tvg_logo,
                    'group_title': group_title,
                    'row1': row1,
                    'row2': row2,
                    'st_uri': st_uri,
                    }

                # Append the dictionary to the list
                data.append(row_data)
                                                                               
        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(data)
       
        # Remove newline characters from the 'st_uri
        #df['st_uri'] = df['st_uri'].str.replace('\n', '')

        # Define the file extensions
        file_extensions = ['.mp4', '.mov', '.avi', '.m4v', '.mkv', '.mp3' ]
        df['st_type'] = np.where(df['row2'].str.contains('|'.join(file_extensions)), 'VOD', 'LIV')
        
        df['to_restream_ind'] = 0 
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
    print(f"""  ! Edit table categories & add 1 for keeping""")
    df = pd.read_pickle('df_playlist.pkl')

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
        new_line = f"""#EXTM3U\n#EXTINF:-1 tvg-id="" tvg-name="CA: KD Sport Live" tvg-logo="http://{ip}:8000/kdcmedia.jpg" group-title="CA| DRESDELL HD",CA: KD Live Sport\nhttp://{ip}:8080/hls/sport.m3u8\n#EXTINF:-1 tvg-id="" tvg-name="CA: KD Doorbell" tvg-logo="http://{ip}:8000/kdcmedia.jpg" group-title="CA| DRESDELL HD",CA: KD Doorbell\nhttp://{ip}:8080/hls/door.m3u8\n"""
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



def StartWeb(folder):

    os.chdir(folder)
    print(f'  * Serving /{folder}/', flush=True)

    from http.server import HTTPServer, SimpleHTTPRequestHandler

    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)

    print('  * Listening at http://127.0.0.1:8000/     > ctrl+c to quit <', flush=True)
    print(" ")
    
    httpd.serve_forever()



def Restreaming(streams) :

    print( "  > Re/Streaming IPTV assets.....")

    print(streams)
    print(type(streams))
    print(" >")

    # List of commands
    commands = [
        "ls -l",
        "echo 'Hello, World!'",
        "pwd"
    ]

    # Execute each command in the list
    for command in commands:
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command '{command}': {e}")

    sys.exit()