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