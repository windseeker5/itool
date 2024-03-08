import subprocess
import time
import ffmpeg
import sqlite3

from rq import Queue
from redis import Redis

from MyLib import ReStream
from MyLib import KillProc
from MyLib import GetRQJob
from MyLib import GetFfmpegPid
from MyLib import GetKpi





redis_conn = Redis()
q = Queue(connection=redis_conn)


db = """/home/kdresdell/Documents/DEV/itool/iptv_data/smartersiptv.db"""

url = """http://slip50863.cdngold.me:80/c8bb0d2998/297afed6ea/412907"""

import os

db = """/home/kdresdell/Documents/DEV/itool/iptv_data/smartersiptv.db"""
filename = os.path.basename(db)
print(filename)

