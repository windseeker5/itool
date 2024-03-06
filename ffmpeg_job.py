import subprocess
import time

# Start the ffmpeg process
ffmpeg_process = subprocess.Popen(['ffmpeg', '-i', 'http://slip50863.cdngold.me:80/c8bb0d2998/297afed6ea/412907', 
'-c', 'copy', '-f', 'flv', 'rtmp://127.0.0.1/live/sport'])

# Get the process ID (PID) of the ffmpeg process
ffmpeg_pid = ffmpeg_process.pid

# Wait for 60 seconds
time.sleep(60)

# Kill the ffmpeg process
subprocess.Popen(['kill', '-kill', str(ffmpeg_pid)])
