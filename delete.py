from rq import Queue
from redis import Redis

redis_conn = Redis()
q = Queue(connection=redis_conn)







# Assuming job_id is the ID of the job you want to cancel
job_id = "bf020de4-c78b-4ab6-baa7-69180fec8ee5"

# Fetch the job by its ID
job = q.fetch_job(job_id)

if job is not None:
    # Cancel the job
    job.cancel()
    print(f"Cancelled job with ID: {job_id}")
else:
    print(f"Job with ID {job_id} not found")
