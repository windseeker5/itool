from rq import Queue
from redis import Redis

redis_conn = Redis()
q = Queue(connection=redis_conn)

from MyLib import ReStream
from MyLib import KillProc
from MyLib import GetRQJob
from MyLib import GetFfmpegPid

mypid = '14132'
k = KillProc(mypid)


print(f'k  : {k}')
print(type(k))