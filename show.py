from rq import Queue
from redis import Redis
import time 

redis_conn = Redis()
q = Queue(connection=redis_conn)


from MyLib import ReStream
from MyLib import KillProc
from MyLib import GetRQJob
from MyLib import GetFfmpegPid


rqid = GetRQJob()

print(f'RQ JOB: {rqid}')
print(type(rqid))


ffid = GetFfmpegPid()

print(f'ffmpeg pids: {ffid}')
print(type(ffid))




