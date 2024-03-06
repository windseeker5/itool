from rq import Queue
from redis import Redis
import time 

redis_conn = Redis()
q = Queue(connection=redis_conn)






# Wait for a short while to ensure the job is processing
time.sleep(1)

# Get all active job IDs
active_job_ids = [job.id for job in q.jobs if job.get_status() == "queued" or job.get_status() == "started"]

print("Active job IDs:")
for job_id in active_job_ids:
    print(job_id)
