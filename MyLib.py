import subprocess
import time
import ffmpeg
import sqlite3
import os 
from datetime import datetime

from rq import Queue
from redis import Redis


import psutil



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






def GetFfmpegPid():
    # List to store process IDs
    pid_list = []

    # Find all running processes that contain 'ffmpeg' in their name
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'ffmpeg' in process.info['name'] or any('ffmpeg' in arg for arg in process.info['cmdline']):
            pid_list.append(process.pid)

    return(pid_list)




def ReStream(url):
    # Start the ffmpeg process
    ffmpeg_process = subprocess.Popen(['ffmpeg', '-i', url, 
    '-c', 'copy', '-f', 'flv', 'rtmp://127.0.0.1/live/sport'])

    # Get the process ID (PID) of the ffmpeg process
    pid = str(ffmpeg_process.pid)
    print(f'ffmpeg PID is {pid}')

    return(pid)



def KillProc(pid_str):
    # Send SIGTERM signal to the process
    # Replace 'pid_str' with the actual process ID string you want to kill

    # Convert the PID string to an integer
    pid = int(pid_str)
    p = os.kill(pid, 15)
    return(p)


