from rq import Queue
from redis import Redis
import time 


import psutil


# List to store process IDs
pid_list = []

# Find all running processes that contain 'ffmpeg' in their name
for process in psutil.process_iter(['pid', 'name', 'cmdline']):
    if 'ffmpeg' in process.info['name'] or any('ffmpeg' in arg for arg in process.info['cmdline']):
        pid_list.append(process.pid)

# Print the list of process IDs
print(pid_list)
print(type(pid_list))