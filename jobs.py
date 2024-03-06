# jobs.py
import time
import random
import ffmpeg

def Restream():
    print('> Initalize variable...')
    input_url = "http://slip50863.cdngold.me:80/c8bb0d2998/297afed6ea/412907"
    output_url = "rtmp://127.0.0.1/live/sport"

    print('> Runnig the command....')
    ffmpeg.input(input_url).output(output_url, c="copy", f="flv").run()

    return(ffmpeg)


def long_running_jobs():
    jobs_running_time = random.randint(100, 400)
    time.sleep(jobs_running_time)
    return f'Jobs finished. Total run time: {jobs_running_time}'
