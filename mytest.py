# mytest.py
import subprocess

def mytest(url):
    print("  > Testing ls -lah...")
    # docker build -t kdc-nginx-rtmp .
    command = ["ffmpeg", "-i", url, "-c", "copy", "-f", "flv", "rtmp://127.0.0.1/live/sport"]
 
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        # Handle errors, if any
        print(f"Error: {e}")

    return()



import subprocess
import psutil

def mytest2(url):
    print("  > Testing ls -lah...")
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

    return pid
