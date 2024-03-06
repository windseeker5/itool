import subprocess
import time
import ffmpeg



def teststream():
    print('> Initalize variable...')
    input_url = "http://slip50863.cdngold.me:80/c8bb0d2998/297afed6ea/412907"
    output_url = "rtmp://127.0.0.1/live/sport"

    print('> Runnig the command....')
    ffmpeg.input(input_url).output(output_url, c="copy", f="flv").run()

    return(ffmpeg)




def ReStream(url):
    # Start the ffmpeg process
    ffmpeg_process = subprocess.Popen(['ffmpeg', '-i', url, 
    '-c', 'copy', '-f', 'flv', 'rtmp://127.0.0.1/live/sport'])

    # Get the process ID (PID) of the ffmpeg process
    pid = str(ffmpeg_process.pid)
    ffmpeg_id = id(pid)

    print(f'ffmpeg PID is {ffmpeg_id}')

    return(ffmpeg_id)




def KillProc(pid):
    #
    # Kill the ffmpeg process
    subprocess.Popen(['kill', '-kill', pid])
    return()
