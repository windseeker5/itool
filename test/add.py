from rq import Queue
from redis import Redis
import time 

from MyLib import ReStream
from MyLib import KillProc

from MyLib import ReStream
from MyLib import KillProc
from MyLib import GetRQJob
from MyLib import GetFfmpegPid



redis_conn = Redis()
q = Queue(connection=redis_conn)



print("> Starting a ReStream process with RQ Redis...")

url = """http://slip50863.cdngold.me:80/c8bb0d2998/297afed6ea/412907"""


job = q.enqueue( ReStream, 
                     args=(url,),
                     job_timeout=None,
                    )

print(f"Enqueued job with ID: {job.id}")


