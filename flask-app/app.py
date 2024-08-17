from flask import ( Flask, render_template, session, redirect, request,
                    url_for, flash, abort, logging, jsonify )
import sqlite3
from rq import Queue
from redis import Redis
import subprocess, os, threading
import time

from MyLib import ReStream, KillProc, GetFfmpegPid, GetKpi, GetStreamName, GetUserSession
from util import PlaylistToDb, DowloadPlaylist, LoadConfig, download_video


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

db = """iptv_data/smartersiptv.db"""

redis_conn = Redis(host='redis', port=6379)

q = Queue(connection=redis_conn)

# Mock user database (replace this with a real user database)
users = {'admin': 'password'}

# GetKpi from db
kpi = GetKpi(db)
conf = LoadConfig()

folder = conf['data_folder'] 
flag_file = "ffmpeg_proc.pid"

print("- Loading config >")
print(f" folder - {folder}")
print(f" flag_file - {flag_file}")



##################################################################################
##
## ROUTES AND PAGES
##
##################################################################################


@app.route('/')
def index():
    fpids = GetFfmpegPid()
    fname = GetStreamName()
    usess = GetUserSession()

    # Init variable if no streaming
    if len(fpids) == 0 :
        fpids = None
        fname = None
        if os.path.exists(flag_file):
            os.remove(flag_file)

    # Sanity check for gost streaming
    if fname is None and fpids is not None:
        for f in fpids:
            k = KillProc(f)
            print(f"- Killing gosth ffmpeg {f}")
            time.sleep(1)  
            return redirect(url_for('index'))

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - ")
    print(f"fpids {fpids}")
    print(f"fname {fname}")
    print(f"usess {usess}")

    return render_template('index.html', fpids=fpids, kpi=kpi, 
                                         session=session, fname=fname,
                                         usess=usess )





# Video Download from app
@app.route('/download/<path:type>/<path:long_url>')
def download(type, long_url):

    # Based on long_url, find stream name 
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT tvg_name FROM smartersiptv WHERE st_uri = ?", (long_url,))    
    st_name = cursor.fetchall()
    st_nm = st_name[0][0]

    # Extract the file extension from lon_url
    _, file_extension = os.path.splitext(long_url)

    # Output the file extension
    print(file_extension)  # Output: .mkv


    # Write the variable to the file
    with open(flag_file, "w") as file:
        file.write(st_nm)

    # Example video URL and file name
    file_url = long_url
    file_nm = folder + "/" + st_nm + file_extension

    print(f"file_nm : {file_nm}")

    # Start the download in a separate thread
    download_thread = threading.Thread(target=download_video, args=(file_url, file_nm))
    download_thread.start()

    time.sleep(1)  # Sleep for 2 seconds

    return redirect(url_for('index'))





@app.route('/manage')
def manage():
    fpids = GetFfmpegPid()
    fname = GetStreamName()
    usess = GetUserSession()

    # Init variable if no streaming
    if len(fpids) == 0 :
        fpids = None
        fname = None
        if os.path.exists(flag_file):
            os.remove(flag_file)

    # Sanity check for gost streaming
    if fname is None and fpids is not None:
        for f in fpids:
            k = KillProc(f)
            print(f"- Killing gosth ffmpeg {f}")
            time.sleep(1)  
            return redirect(url_for('index'))

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - ")
    print(f"fpids {fpids}")
    print(f"fname {fname}")
  
    return render_template('manage.html', fpids=fpids, kpi=kpi, 
                                          session=session, fname=fname, 
                                          usess=usess )





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
            return render_template('login.html', message='Invalid credentials')
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

    # Based on long_url, find stream name 
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT tvg_name FROM smartersiptv WHERE st_uri = ?", (long_url,))    
    st_name = cursor.fetchall()
    st_nm = st_name[0][0]

    # Write the variable to the file
    with open(flag_file, "w") as file:
        file.write(st_nm)

    # send the job to redis
    job = q.enqueue( ReStream, 
                     args=(type, long_url,),
                     job_timeout=43200,
                     result_ttl=43200 
                    )
    
    time.sleep(2)  # Sleep for 2 seconds
    return redirect(url_for('index'))





# Cancel ffmpeg job
@app.route('/delete/<id>')
def delete(id):
    
    if os.path.exists(flag_file):
        os.remove(flag_file)

    k = KillProc(id)

    time.sleep(5)  # Sleep for 3 seconds
    return redirect(url_for('index'))



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
    fname = GetStreamName()
    usess = GetUserSession()

    if len(fpids) == 0 :
        fpids = None
        fname = None

        if os.path.exists(flag_file):
            os.remove(flag_file)

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - ")
    print(f"fpids {fpids}")
    print(f"fname {fname}")
  
    return render_template('manage.html', items=items, fpids=fpids, kpi=kpi,
                                          session=session, fname=fname,
                                          usess=usess ) 





# Explore best hot
@app.route('/exploremov', methods=['GET', 'POST'])
def exploremov():
    fpids = GetFfmpegPid()
    fname = GetStreamName()    
    usess = GetUserSession()

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

    exp_type = "movies"
 
    if len(fpids) == 0 :
        fpids = None
        fname = None

        if os.path.exists(flag_file):
            os.remove(flag_file)

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - ")
    print(f"fpids {fpids}")
    print(f"fname {fname}")

    return render_template('explore.html',items=items,fpids=fpids,
                                          kpi=kpi,exp_type=exp_type,fname=fname,
                                          usess=usess  )







# Explore best hot
@app.route('/exploretv', methods=['GET', 'POST'])
def exploretv():
    fpids = GetFfmpegPid()
    fname = GetStreamName()
    usess = GetUserSession()

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

    exp_type = "tv shows"

    if len(fpids) == 0 :
        fpids = None
        fname = None

        if os.path.exists(flag_file):
            os.remove(flag_file)

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - ")
    print(f"fpids {fpids}")
    print(f"fname {fname}")

    return render_template('explore.html',items=items,fpids=fpids,
                                          kpi=kpi,exp_type=exp_type,fname=fname,
                                          usess=usess )





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

