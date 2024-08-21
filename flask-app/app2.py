from flask import Flask, render_template, jsonify
from threading import Thread
from tasks import UpdatePlaylist, DownloadVod, status

app = Flask(__name__)





@app.route('/updatedb', methods=['POST'])
def updatedb():
    if not status["running"]:

        m3u_url = """http://cf.7563kc.cloud/get.php?username=c8bb0d2998&password=297afed6ea&type=m3u_plus&output=ts"""
        pl_name = "iptv_data/Smartersiptv.m3u"
        db_name = "iptv_data/smartersiptv.db"


        thread = Thread(target=UpdatePlaylist, args=(m3u_url, pl_name, db_name, ))
        thread.start()
        return jsonify({"message": "Task started"}), 202
    else:
        return jsonify({"message": "Task is already running"}), 409





@app.route('/downloadvod', methods=['POST'])
def downloadvod():
    if not status["running"]:

        vod = "http://cf.7563kc.cloud:80/movie/c8bb0d2998/297afed6ea/317922.mp4"
        vod_nm ="MyTest.mp4"

        thread = Thread(target=DownloadVod, args=(vod, vod_nm, ))
        thread.start()
        return jsonify({"message": "Task started"}), 202
    else:
        return jsonify({"message": "Task is already running"}), 409






@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(status), 200




@app.route('/')
def index():
    return render_template('index2.html')





if __name__ == '__main__':
    app.run(debug=True, port=5001)
