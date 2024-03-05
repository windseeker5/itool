from rq import Queue
from redis import Redis

# Connect to Redis server
# redis_conn = Redis()

print("> Starting debug...")

# Connect to the Redis server
redis_conn = Redis(host='localhost', port=6379)


# Create a Queue object for the desired queue
#queue = Queue('queue_name', connection=redis_conn)
queue = Queue(connection=redis_conn)



# Get all job IDs in the queue
job_ids = queue.job_ids

# Get details of each job
for job_id in job_ids:
    job = queue.fetch_job(job_id)
    print(f"Job ID: {job.id}, Status: {job.get_status()}")
