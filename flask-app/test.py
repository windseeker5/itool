import sqlite3, subprocess, os, time
from threading import Thread
from tasks import *





# Mockup user database
users = {'admin': 'password'}


# Load config from yaml
conf = LoadConfig()
folder = conf['data_folder'] 
flag_file = "ffmpeg_proc.pid"
m3u_url = conf['m3u_service'] 
pl_name = conf['data_folder'] + "/" + conf['m3u_file_fullsize'] # "iptv_data/Smartersiptv.m3u"
db_name = conf['data_folder'] + "/" + conf['db_file'] # "iptv_data/smartersiptv.db"


print("> Debuging my Update Playlist....")

UpdatePlaylist(m3u_url, pl_name, db_name)

