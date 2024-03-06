from rq import Queue
from redis import Redis
import time 

from MyLib import ReStream
from MyLib import KillProc


redis_conn = Redis()
q = Queue(connection=redis_conn)



print("> Starting a ReStream process with RQ Redis...")

url = """http://slip50863.cdngold.me:80/c8bb0d2998/297afed6ea/412907"""


# Enqueue a job
# job = q.enqueue(ReStream, url)


job = q.enqueue( ReStream, 
                     args=(url,),
                     job_timeout=3600,
                    )

# Get the metadata of the job
meta_data = job.meta

print(f"Enqueued job with ID: {job.id}")

print(f'> meta is: {meta_data}')

print(f'ffmpeg id is : {ffmpeg_id}')
