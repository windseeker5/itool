import subprocess
import time
import ffmpeg
import sqlite3
import os 
from datetime import datetime
from rq import Queue
from redis import Redis
import psutil




def GetKpi(db):
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



def GetFfmpegPid():
    pid_list = []

    # Find all running processes that contain 'ffmpeg' in their name
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'ffmpeg' in process.info['name'] or any('ffmpeg' in arg for arg in process.info['cmdline']):
            pid_list.append(process.pid)
    return(pid_list)




def start_ffmpeg_liv(url):
    return subprocess.Popen(['ffmpeg', '-v', 'verbose', 
            '-thread_queue_size', '4096', '-i', url,
            '-c', 'copy', '-f', 'flv', 'rtmp://127.0.0.1/live/live'])



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
    return(p)
    #return

