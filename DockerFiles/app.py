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

from util import PlaylistToDb
from util import DowloadPlaylist
from util import LoadConfig



app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

db = """iptv_data/smartersiptv.db"""

redis_conn = Redis(host='tv.dresdell.com', port=6379)
q = Queue(connection=redis_conn)


# Mock user database (replace this with a real user database)
users = {'admin': 'password'}


# GetKpi from db
kpi = GetKpi(db)


conf = LoadConfig()
folder = "iptv_data"  # Data Folder 



#pl = DowloadPlaylist( conf['m3u_service'] , folder+"/"+ conf['m3u_file_fullsize'] )

#stat = PlaylistToDb( folder+"/"+conf['m3u_file_fullsize'], 
#                     folder+"/"+conf['db_file'], 
#                     conf['db_schema'])



##
## ROUTES AND PAGES
##



@app.route('/')
def index():
    # List RQ Job and FFmpeg id
    fpids = GetFfmpegPid()
    if len(fpids) == 0 :
        fpids = None

    if session:
        print(session)
  
    return render_template('index.html', fpids=fpids, kpi=kpi, session=session)




@app.route('/manage')
def manage():
    # List RQ Job and FFmpeg id
    fpids = GetFfmpegPid()
    if len(fpids) == 0 :
        fpids = None

    if session:
        print(session)
        print(session['username'])
        print(type(session['username']))
  
    return render_template('manage.html', fpids=fpids, kpi=kpi, session=session)






@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Perform the actual login check here (this is a basic example)
        if username == 'admin' and password == 'password':
            print("Saving user in session....")
            session['username'] = username  
            return redirect(url_for('index'))
        else:
            return render_template('login3.html', message='Invalid credentials')
    else:
        return render_template('login.html')





@app.route('/logout')
def logout():
    print(f'sesion : {session}')
    session.pop('username', None)
    return redirect(url_for('index'))






# Add ffmpeg job
@app.route('/qjob/<path:type>/<path:long_url>')
def qjob(type, long_url):

    job = q.enqueue( ReStream, 
                     args=(type, long_url,),
                     job_timeout=3600,
                     # result_ttl=20 
                    )
    
    time.sleep(2)  # Sleep for 2 seconds
    return redirect(url_for('manage'))






# Cancel ffmpeg job
@app.route('/delete/<id>')
def delete(id):
    # Killing ffmpeg job
    k = KillProc(id)

    flash(f"ffmpeg restream process #{k} was killed...")

    time.sleep(2)  # Sleep for 2 seconds
    #return render_template('index2.html', jobs=jobs)
    return redirect(url_for('manage'))





# Search for Liv or vod
@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query')
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("""SELECT 
                            s.tvg_id,
                            s.tvg_name,
                            s.vod_name,
                            s.tvg_logo,
                            s.group_title,
                            s.st_uri,
                            s.st_type,
                            m.genres,
                            m.vote_average,
                            m.popularity,
                            m.original_language,
                            CASE
                                WHEN m.original_language IN ('fr', 'en') AND m.vote_average >= 7 THEN 1
                                ELSE 0
                            END AS hot
                        FROM
                            smartersiptv AS s LEFT OUTER JOIN movies AS m ON 
                                s.vod_name = m.original_title

                        WHERE s.tvg_name LIKE ?""", ('%' + search_query + '%',))
    
    items = cursor.fetchall()
    conn.close()

    fpids = GetFfmpegPid()
    if len(fpids) == 0 :
        fpids = None

    return render_template('manage.html', items=items, fpids=fpids, kpi=kpi )



#@app.route('/explore', methods=['GET', 'POST'])
#def explore():
#    if request.method == 'POST':
#        # Your existing POST method logic
#        pass
#    else:
#        # Your GET method logic
#        pass



# Explore best hot
@app.route('/exploremov', methods=['GET', 'POST'])
def exploremov():
    search_query = request.form.get('search_query')
    conn = sqlite3.connect(db)
    cursor = conn.cursor()


    cursor.execute("""SELECT 
    s.tvg_id,
    s.tvg_name,
    s.vod_name,
    s.tvg_logo,
    s.group_title,
    s.st_uri,
    s.st_type,
    m.genres,
    ROUND(m.vote_average, 1),
    m.tagline,
    m.popularity,
    m.original_language,
    CASE
        WHEN m.original_language IN ('fr', 'en') AND m.vote_average >= 7.5 THEN 1
        ELSE 0
    END AS hot
FROM
    smartersiptv AS s
        LEFT OUTER JOIN
    movies AS m ON s.vod_name = m.original_title
WHERE
    s.group_title IN ('EN - NEW RELEASE')
    -- s.group_title IN ('ENGLISH SERIES','FRANCE SÉRIES','NETFLIX  SERIES','APPLE+ SERIES','NORDIC SERIES', 'QUÉBEC SERIES')
    
    AND hot = 1
ORDER BY
    m.vote_average DESC;""")

  
    items = cursor.fetchall()
    conn.close()

    fpids = GetFfmpegPid()
    if len(fpids) == 0 :
        fpids = None

    exp_type = "movies"

    return render_template('explore.html',items=items,fpids=fpids,kpi=kpi,exp_type=exp_type )







# Explore best hot
@app.route('/exploretv', methods=['GET', 'POST'])
def exploretv():
    search_query = request.form.get('search_query')
    conn = sqlite3.connect(db)
    cursor = conn.cursor()


    cursor.execute("""SELECT 
    s.tvg_id,
    s.tvg_name,
    s.vod_name,
    s.tvg_logo,
    s.group_title,
    s.st_uri,
    s.st_type,
    m.genres,
    ROUND(m.vote_average, 1),
    m.tagline,
    m.popularity,
    m.original_language,
    CASE
        WHEN m.original_language IN ('fr', 'en') AND m.vote_average >= 7.5 THEN 1
        ELSE 0
    END AS hot
FROM
    smartersiptv AS s
        LEFT OUTER JOIN
    movies AS m ON s.vod_name = m.original_title
WHERE
    -- s.group_title IN ('EN - NEW RELEASE')
    s.group_title IN ('ENGLISH SERIES','FRANCE SÉRIES','NETFLIX  SERIES','APPLE+ SERIES','NORDIC SERIES', 'QUÉBEC SERIES')
    
    AND hot = 1
ORDER BY
    m.vote_average DESC;""")

  
    items = cursor.fetchall()
    conn.close()

    fpids = GetFfmpegPid()
    if len(fpids) == 0 :
        fpids = None

    exp_type = "tv shows"

    return render_template('explore.html',items=items,fpids=fpids,kpi=kpi,exp_type=exp_type )










if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

