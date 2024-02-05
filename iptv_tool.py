
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
from util import Restreaming
from util import RandomStream

# Next improvements :

#  - GUI choice for filtered streams before export
#  - Export name 
#  - possibility to export multiple based on diff filters
#  - Show submenu with Categories , type  and names
#  
#  - Download the docker images +nginx config
#
#  - Pass the restream name for the export from YAML config instead of
#    hardcoded like it is.



if __name__ == '__main__':

    conf = LoadConfig()
    streams = '-'
    rst_info = '-'
    choice = ""

    folder = "iptv_data"

    if not os.path.exists(folder): 
        os.makedirs(folder) 

    while True:
        Header(streams, rst_info)
        print("  [1] Install Docker & Nginx-rmtp")
        print("  [2] Download m3u file from service provider(SP)")
        print("  [3] Convert m3u file to Sqlite db")
        print("  [4] Export your filtered \ smaller m3u file")
        print("  [5] Start local web service for your m3u files")
        print("  [6] re/streaming IPTV")
        print("  [q] Exit ")
        print("")
        choice = input("  Enter Choice > ")
        choice = choice.strip()
        

        # MENU OPTION 1
        if (choice == "1"):
            print('runing function 1')

        # MENU OPTION 2
        elif (choice == "2"):
            ip = Header(streams, rst_info)
            pl = DowloadPlaylist( conf['m3u_service'] , 
                                  folder+"/"+ conf['m3u_file_fullsize'] )
            time.sleep(7)  

        # MENU OPTION 3
        elif (choice == "3"):
            ip = Header(streams, rst_info)
            stat = PlaylistToDb( folder+"/"+conf['m3u_file_fullsize'], 
                                 folder+"/"+conf['db_file'], 
                                 conf['db_schema'])
            streams = stat['stream']
            time.sleep(15) 
          
        # MENU OPTION 4    
        elif (choice == "4"):
            ip = Header(streams, rst_info)
            exp = ExportPlaylist( folder+"/"+conf['m3u_file_downsized'], 
                                  folder+"/"+conf['db_file'], 
                                  "categories", ip )
            time.sleep(15) 

        # MENU OPTION 5
        elif (choice == "5"):
            ip = Header(streams, rst_info)
            StartWeb(folder)

        # MENU OPTION 6
        elif (choice == "6"):
            ip = Header(streams, rst_info)
            rst_info = Restreaming(conf['restreams'])


        # MENU OPTION q
        elif (choice == "q"):
            sys.exit()
        
        # MENU OPTION 6
        elif (choice == "x"):
            ip = Header(streams, rst_info)
            RDM_ST = RandomStream(folder+"/"+conf['db_file'], 
                                  conf['db_schema'])

        else:    
            print("Invalid Option. Please Try Again.")
            sys.exit()


 

