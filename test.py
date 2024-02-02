import subprocess
import os
import time


cmd = """ffmpeg -i rtsp://admin:'mFrance&2012phileli'@192.168.1.174:554 -c copy -f flv rtmp://127.0.0.1/live/door"""
# print(cmd)

# Run the command in the background using subprocess.Popen
process = subprocess.Popen(cmd, shell=True, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                preexec_fn=os.setsid)

# Get the process ID (PID)
pid = process.pid
print("ffmpeg process started with PID:", pid)
time.sleep(5)


