from flask import ( Flask, render_template, session, redirect, request,
                    url_for, flash, abort, logging, jsonify )

import sqlite3


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


from rq import Queue
from redis import Redis
import subprocess
from util import ReStream

# Connect to the Redis server
redis_conn = Redis(host='localhost', port=6379)

# Create a queue named 'ffmpeg_jobs'
q = Queue(connection=redis_conn)






@app.route('/delete/<id>')
def delete(id):

    # Fetch the job by its ID
    job = q.fetch_job(id)

    # Check if the job exists and is queued
    if job is not None and job.get_status() == 'queued':
        # Cancel the job
        job.cancel()
        print(f"Job {id} has been cancelled.")
    else:
        print(f"Job {id} not found or already running.")

    flash("Bot was deleted")

    # Get all jobs in the queue
    jobs = q.jobs

    #return render_template('index2.html', jobs=jobs)
    return redirect(url_for('index'))






@app.route('/')
def index():

    q = Queue(connection=redis_conn)
    # Get all jobs in the queue
    jobs = q.jobs
    print(jobs)
    print(type(jobs))

    return render_template('index2.html', jobs=jobs)





@app.route('/qjob/<path:long_url>')
def qjob(long_url):

    job = q.enqueue( ReStream, 
                     args=(long_url,),
                     job_timeout=3600,
                     # result_ttl=20 
                    )

    flash(f"Bot creation was successfull! your ID is {job.get_id()}")
    
  # Get all jobs in the queue
    jobs = q.jobs
    print(jobs)
    print(type(jobs))

    #return render_template('index2.html', jobs=jobs)
    return redirect(url_for('index'))




@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query')
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM smartersiptv WHERE tvg_name LIKE ?", ('%' + search_query + '%',))
    items = cursor.fetchall()
    conn.close()

  # Get all jobs in the queue
    jobs = q.jobs
    print(jobs)
    print(type(jobs))

    return render_template('index2.html', items=items, jobs=jobs)






if __name__ == '__main__':
    app.run(debug=True)

