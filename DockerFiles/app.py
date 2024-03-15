from flask import ( Flask, render_template, session, redirect, request,
                    url_for, flash, abort, logging, jsonify )

import sqlite3
from rq import Queue
from redis import Redis
import subprocess
import time

from MyLib import ReStream
from MyLib import KillProc
from MyLib import GetFfmpegPid
from MyLib import GetKpi


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


db = """iptv_data/smartersiptv.db"""


#redis_conn = Redis(host='tv.dresdell.com', port=6379)
#redis_conn = Redis()
redis_conn = Redis(host='127.0.0.1', port=6379)
q = Queue(connection=redis_conn)


# GetKpi from db
kpi = GetKpi(db)





##
## ROUTES AND PAGES
##


# home page
@app.route('/')
def index():
    # List RQ Job and FFmpeg id
    fpids = GetFfmpegPid()
    if len(fpids) == 0 :
        fpids = None

    return render_template('index.html', fpids=fpids, kpi=kpi)




# home page
@app.route('/test')
def test():
    # List RQ Job and FFmpeg id
    fpids = GetFfmpegPid()
    if len(fpids) == 0 :
        fpids = None

    return render_template('test.html', fpids=fpids, kpi=kpi)





# Cancel ffmpeg job
@app.route('/delete/<id>')
def delete(id):
    # Killing ffmpeg job
    k = KillProc(id)

    flash(f"ffmpeg restream process #{k} was killed...")

    time.sleep(2)  # Sleep for 2 seconds
    #return render_template('index2.html', jobs=jobs)
    return redirect(url_for('index'))





# Add ffmpeg job
@app.route('/qjob/<path:long_url>')
def qjob(long_url):

    job = q.enqueue( ReStream, 
                     args=(long_url,),
                     job_timeout=3600,
                     # result_ttl=20 
                    )
    
    time.sleep(1)  # Sleep for 2 seconds
    return redirect(url_for('index'))






# Search for Liv or vod
@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query')
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM smartersiptv WHERE tvg_name LIKE ?", ('%' + search_query + '%',))
    items = cursor.fetchall()
    conn.close()

    fpids = GetFfmpegPid()
    if len(fpids) == 0 :
        fpids = None

    return render_template('index.html', items=items, fpids=fpids, kpi=kpi )




if __name__ == '__main__':
    app.run(debug=True)


#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000, debug=True)





