import subprocess
import time
import ffmpeg
import sqlite3
import os 
from datetime import datetime

from rq import Queue
from redis import Redis

redis_conn = Redis()
q = Queue(connection=redis_conn)





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






def GetRQJob():

    # Get all active job IDs
    active_job_ids = [job.id for job in q.jobs if job.get_status() == "queued" or job.get_status() == "started"]
    print(active_job_ids)
    #print("Active job IDs:")
    #for job_id in active_job_ids:
    #    print(job_id)
    
    #return(job_id)



def GetFfmpegPid():

    try:
        # Define the command to run
        command = 'pgrep -f "ffmpeg -i http://"'

        # Run the command and capture the output
        output = subprocess.check_output(command, shell=True)

        # Decode the output and get the PID
        pid = output.decode().strip()

        pid_list = [pid]
        print(f"PID:{pid_list}")

    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        pid_list = None

    return(pid_list)




def ReStream(url):
    # Start the ffmpeg process
    ffmpeg_process = subprocess.Popen(['ffmpeg', '-i', url, 
    '-c', 'copy', '-f', 'flv', 'rtmp://127.0.0.1/live/sport'])

    # Get the process ID (PID) of the ffmpeg process
    pid = str(ffmpeg_process.pid)
    print(f'ffmpeg PID is {pid}')

    return(pid)



def KillProc(pid):
    # Kill the ffmpeg process
    p = subprocess.Popen(['kill', '-kill', pid])
    pid = str(p.pid)
    print(f'Killing is {pid}')

    return(pid)


