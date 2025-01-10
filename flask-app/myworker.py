import logging
from rq import Worker, Queue
from redis import Redis
import sys
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('worker.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def run_worker():
    try:
        #redis_conn = Redis(host='redis', port=6379)
        redis_conn = Redis(host='localhost', port=6379)

        queue = Queue(connection=redis_conn)  # Explicitly pass the connection
        worker = Worker([queue])  # Pass the queue as a list
        worker.work()
    except Exception as e:
        logger.exception("Worker failed with exception: %s", e)
        sys.exit(1)

if __name__ == '__main__':
    while True:
        try:
            run_worker()
        except KeyboardInterrupt:
            logger.info("Worker stopped by user")
            sys.exit(0)
        except Exception:
            logger.exception("Worker crashed, restarting...")
            time.sleep(5)  # Wait for a few seconds before restarting
