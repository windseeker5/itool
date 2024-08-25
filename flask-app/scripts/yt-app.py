from flask import Flask, request, jsonify, render_template, redirect, url_for
from threading import Thread
import yt_dlp
import os, re 



app = Flask(__name__)



# Global variable to store the status of the download process
download_status = {
    'status': 'idle',
    'progress': 0,
    'file_path': None
}





# Function to download the video or audio in the background
def download_media(url, download_type):
    global download_status
    download_status['status'] = 'in_progress'
    download_status['progress'] = 0

    ydl_opts = {
        'progress_hooks': [progress_hook],
        'outtmpl': '%(title)s.%(ext)s',
    }

    # Configure download type
    if download_type == 'audio':
        ydl_opts.update({
            'format': 'bestaudio/best',  # Select the best audio format available
        })
    elif download_type == 'video':
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',  # Best video and audio combined
            'merge_output_format': 'mp4',  # Merge video and audio into mp4 format
        })


    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            download_status['status'] = 'completed'
    except Exception as e:
        download_status['status'] = 'failed'
        download_status['error'] = str(e)




# Progress hook to update the download status

def progress_hook(d):
    global download_status
    if d['status'] == 'downloading':
        # Strip ANSI escape sequences from the progress string
        progress_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str']).strip()
        download_status['progress'] = progress_str
    elif d['status'] == 'finished':
        download_status['file_path'] = d['filename']




@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('url')
        download_type = request.form.get('download_type')
        if url and download_type:
            # Start the download in a separate thread
            download_thread = Thread(target=download_media, args=(url, download_type))
            download_thread.start()
            return redirect(url_for('status'))
        else:
            return render_template('home.html', error="YouTube URL and download type are required")
    
    return render_template('home.html')





@app.route('/status', methods=['GET'])
def status():
    return render_template('status.html')





@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify(download_status)






if __name__ == '__main__':
   # os.environ['HTTP_PROXY'] = 'http://webproxystatic-on.tsl.telus.com:8080'
   # os.environ['HTTPS_PROXY'] = 'http://webproxystatic-on.tsl.telus.com:8080'
    app.run(debug=True, port=8000)
