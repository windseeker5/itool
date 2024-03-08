from flask import ( Flask, render_template, session, redirect, request,
                    url_for, flash, abort, logging, jsonify )

import sqlite3
from rq import Queue
from redis import Redis
import subprocess

from MyLib import ReStream
from MyLib import KillProc
from MyLib import GetRQJob
from MyLib import GetFfmpegPid
from MyLib import GetKpi



app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

db = """iptv_data/smartersiptv.db"""



# RQ & redis setup - need redis server as docker 
redis_conn = Redis()
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
    print(fpids)
    return render_template('index2.html', fpids=fpids, kpi=kpi)




# Cancel ffmpeg job
@app.route('/delete/<id>')
def delete(id):

    # Killing ffmpeg job
    k = KillProc(id)

    flash(f"ffmpeg restream process #{k} was killed...")

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

    return render_template('index2.html', items=items, fpids=fpids, kpi=kpi )








if __name__ == '__main__':
    app.run(debug=True)

