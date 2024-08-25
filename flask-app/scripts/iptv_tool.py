
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
from util import RandomStream
from util import BatchDownload
from util import BuidlRunDocker
from util import BuildMovieDB

# Next improvements :
#
#  - Download the docker images +nginx config
#



if __name__ == '__main__':

    conf = LoadConfig()
    streams = '-'
    rst_info = '-'
    choice = ""
    folder = "iptv_data"  # Data Folder 

    if not os.path.exists(folder): 
        os.makedirs(folder) 



    while True:
        Header(streams, rst_info)
        print("  [1] Build docker image & run it ")
        print("  [2] Download m3u file from service provider(SP)")
        print("  [3] Convert m3u file to Sqlite db")
        print("  [4] Export your filtered to smaller m3u file")
        print("  [5] ")
        print("  [6] Build movies DB for reco engine")
        print("  [7] Download VOD flaged 1 in DB")
        print("  [q] Exit ")
        print("")
        choice = input("  Enter Choice > ")
        choice = choice.strip()
        

        # MENU OPTION 1
        if (choice == "1"):
            ip = Header(streams, rst_info)
            DocPath = r"""/home/kdresdell/Documents/DEV/itool/DockerFiles/"""
            docid = BuidlRunDocker( DocPath )
            time.sleep(20)  

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
            BuildMovieDB()
            time.sleep(10) 


        # MENU OPTION 7
        elif (choice == "7"):
            ip = Header(streams, rst_info)
            MyDownload = BatchDownload( folder+"/"+conf['db_file'], 
                                        conf['db_schema'],
                                        folder )
            time.sleep(15) 


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


 

