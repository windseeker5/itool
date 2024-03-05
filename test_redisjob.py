from rq import Queue
from redis import Redis
from mytest import mytest2  # Import mytest function from mytest module
import subprocess

# Connect to the Redis server
redis_conn = Redis(host='localhost', port=6379)

# Create a queue named 'ffmpeg_jobs'
q = Queue(connection=redis_conn)




url = ["""http://slip50863.cdngold.me:80/c8bb0d2998/297afed6ea/412907"""]

job = q.enqueue(mytest2, 
                args=(url) )

#job = q.enqueue(mytest, 
#                args=(url) ,
#                job_timeout=72000,
#                result_ttl=86400 )
