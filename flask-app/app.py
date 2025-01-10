from flask import Flask, render_template, session, redirect, request, url_for, flash, abort, logging, jsonify
from redis import Redis
from rq import Worker, Queue
import sqlite3, subprocess, os, time
from threading import Thread
from tasks import *





app = Flask(__name__)

app.secret_key = 'your_secret_key_here'

redis_conn = Redis(host='redis', port=6379)
#redis_conn = Redis(host='localhost', port=6379)
q = Queue(connection=redis_conn)


# Mockup user database
users = {'admin': 'password'}


# Load config from yaml
conf = LoadConfig()
folder = conf['data_folder'] 
flag_file = "ffmpeg_proc.pid"
m3u_url = conf['m3u_service'] 
pl_name = conf['data_folder'] + "/" + conf['m3u_file_fullsize'] # "iptv_data/Smartersiptv.m3u"
db_name = conf['data_folder'] + "/" + conf['db_file'] # "iptv_data/smartersiptv.db"

# GetKpi from db
kpi = GetKpi(db_name)



##################################################################################
##
## ROUTES AND PAGES
##
##################################################################################



@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(status), 200






@app.route('/')
def index():
    fpids = GetFfmpegPid()
    fname = GetStreamName()
    usess = GetUserSession()
    
    # GetKpi from db
    kpi = GetKpi(db_name)

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

    return render_template('index.html', status=status, fpids=fpids, kpi=kpi, 
                                         session=session, fname=fname,
                                         usess=usess )







@app.route('/updatedb', methods=['GET', 'POST'])
def updatedb():
    if not status["running"]:

        udb_thread = Thread(target=UpdatePlaylist, args=(m3u_url, pl_name, db_name, ))
        udb_thread.start()

    return redirect(url_for('index'))







# Video Download from app
@app.route('/download/<path:type>/<path:long_url>')
def download(type, long_url):

    # Find stream name 
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT tvg_name FROM smartersiptv WHERE st_uri = ?", (long_url,))    
    st_name = cursor.fetchall()
    st_nm = st_name[0][0]

    conn.close()

    # Extract the file extension from lon_url
    _, file_extension = os.path.splitext(long_url)

    # Example video URL and file name
    file_url = long_url
    file_nm = folder + "/" + st_nm + file_extension

    print(f"file_nm : {file_nm}")

    # Start the download in a separate thread
    download_thread = Thread(target=DownloadVod, args=(file_url, file_nm))
    download_thread.start()

    time.sleep(1)  

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
  
    return render_template('manage.html', status=status, fpids=fpids, kpi=kpi, 
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
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT tvg_name FROM smartersiptv WHERE st_uri = ?", (long_url,))    
    st_name = cursor.fetchall()
    st_nm = st_name[0][0]
    conn.close()

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

    return redirect(url_for('index'))







@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query')

    if not search_query:
        flash('Please enter an asset to search !', category='error')
        return redirect(url_for('manage'))


    # Split the search query into individual words
    search_terms = search_query.split()
    
    # Construct the SQL query with placeholders for each search term
    sql_query = """SELECT 
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
                    WHERE """
    
    # Add LIKE conditions for each word in the search terms, combined with AND
    sql_query += " AND ".join(["s.tvg_name LIKE ?"] * len(search_terms))
    
    # Prepare the values for the placeholders
    like_values = ['%' + term + '%' for term in search_terms]
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(sql_query, like_values)
    
    items = cursor.fetchall()
    conn.close()

    fpids = GetFfmpegPid()
    fname = GetStreamName()
    usess = GetUserSession()

    if len(fpids) == 0:
        fpids = None
        fname = None

        if os.path.exists(flag_file):
            os.remove(flag_file)

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - ")
    print(f"fpids {fpids}")
    print(f"fname {fname}")
  
    return render_template('manage.html', status=status, items=items, fpids=fpids, kpi=kpi,
                                          session=session, fname=fname,
                                          usess=usess )









if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

