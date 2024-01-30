
import sys
import os
import yaml
import socket
import time

from util import PlaylistToDb
from util import DowloadPlaylist
from util import ExportPlaylist
from util import Header
from util import LoadConfig
from util import StartWeb

if __name__ == '__main__':

    conf = LoadConfig()

    streams = '-'
    choice = ""

    folder = "iptv_data"

    if not os.path.exists(folder): 
        os.makedirs(folder) 


    while True:
        Header(streams)
        print("  [1] Install Docker & Nginx-rmtp")
        print("  [2] Download m3u file from service provider(SP)")
        print("  [3] Convert m3u file to Sqlite db")
        print("  [4] Export your filtered \ smaller m3u file")
        print("  [5] Start local web service for your m3u files")
        print("  [x] Exit ")
        print("")
        choice = input("  Enter Choice > ")
        choice = choice.strip()
        

        #1
        if (choice == "1"):
            print('runing function 1')

        #2
        elif (choice == "2"):
            ip = Header(streams)
            pl = DowloadPlaylist( conf['m3u_serv'] , 
                                  folder+"/"+conf['m3u_orig'] )
            time.sleep(7)  

        #3
        elif (choice == "3"):
            ip = Header(streams)
            stat = PlaylistToDb( folder+"/"+conf['m3u_orig'], 
                                 folder+"/"+conf['sql_db'], 
                                 conf['db_schema'])
            streams = stat['stream']
            time.sleep(15) 
          
        #4    
        elif (choice == "4"):
            ip = Header(streams)
            exp = ExportPlaylist( folder+"/"+conf['m3u_expt'], 
                                  folder+"/"+conf['sql_db'], 
                                  "categories", ip )
            time.sleep(10) 

        #5
        elif (choice == "5"):
            ip = Header(streams)
            StartWeb(folder)


        #X
        elif (choice == "x"):
            sys.exit()
        

        
        
        
        else:    
            print("Invalid Option. Please Try Again.")
            sys.exit()


 

















"""

== Recette Gagnant a date

# Voici la recette pour encoder le fichier 

ffmpeg -i input.mkv -c:v libx264 -preset medium -b:v 3000k -maxrate 3000k -bufsize 6000k \
-vf "scale=1280:-1,format=yuv420p" -g 50 -c:a aac -b:a 128k -ac 2 -ar 44100 file.flv


# pour streamer sur nginx un fichier bien encode

ffmpeg -re -i file2.flv -c copy -f flv rtmp://127.0.0.1/live/test2  


# Recette pour faire restreaming one-shot - a tester

# RDS

ffmpeg -i http://slip50863.cdngold.me:80/c8bb0d2998/297afed6ea/412907 \
-c:v libx264 -preset medium \
-b:v 3000k -maxrate 3000k -bufsize 6000k \
-vf "scale=1280:-1,format=yuv420p" -g 50 -c:a aac -b:a 128k -ac 2 -ar 44100 \
-f flv rtmp://127.0.0.1/live/test1 


# CRAVE1
ffmpeg -i http://slip50863.cdngold.me:80/c8bb0d2998/297afed6ea/414054 \
-c:v libx264 -preset medium \
-b:v 3000k -maxrate 3000k -bufsize 6000k \
-vf "scale=1280:-1,format=yuv420p" -g 50 -c:a aac -b:a 128k -ac 2 -ar 44100 \
-f flv rtmp://127.0.0.1/live/test2


"""