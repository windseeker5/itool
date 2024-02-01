
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
        print("  [6] re/streaming IPTV")
        print("  [x] Exit ")
        print("")
        choice = input("  Enter Choice > ")
        choice = choice.strip()
        

        # MENU OPTION 1
        if (choice == "1"):
            print('runing function 1')

        # MENU OPTION 2
        elif (choice == "2"):
            ip = Header(streams)
            pl = DowloadPlaylist( conf['m3u_serv'] , 
                                  folder+"/"+conf['m3u_orig'] )
            time.sleep(7)  

        # MENU OPTION 3
        elif (choice == "3"):
            ip = Header(streams)
            stat = PlaylistToDb( folder+"/"+conf['m3u_orig'], 
                                 folder+"/"+conf['sql_db'], 
                                 conf['db_schema'])
            streams = stat['stream']
            time.sleep(15) 
          
        # MENU OPTION 4    
        elif (choice == "4"):
            ip = Header(streams)
            exp = ExportPlaylist( folder+"/"+conf['m3u_expt'], 
                                  folder+"/"+conf['sql_db'], 
                                  "categories", ip )
            time.sleep(15) 

        # MENU OPTION 5
        elif (choice == "5"):
            ip = Header(streams)
            StartWeb(folder)

        # MENU OPTION 6
        elif (choice == "6"):
            ip = Header(streams)
            print( "> Re/Streaming IPTV assets.....")

        # MENU OPTION X
        elif (choice == "x"):
            sys.exit()
        
        
        
        else:    
            print("Invalid Option. Please Try Again.")
            sys.exit()


 

