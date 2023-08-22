#OS imports
import shutil
import os
import sys
import string

from RetroManagerDatabase import *

supported_rom_ext = [
    "bin", "bkp", "fig", "gen", "sfc", "gd3", "gd7", "dx2", "bsx", "swc", "nes",
    "nfc", "fds", "unf", "gba", "agb", "gbz", "gbc", "gb", "sgb",  "md", "smc", "smd", "sms", "zfb", "zfc", "zgb", "zip", "zmd", "zsf"
]

class RetroManagerCore():
    
    default_filepath = os.path.join(os.path.expanduser("~"), "RetroManager")   
    #Library (Need to make this changeable)
    filepath_library = os.path.join(default_filepath, "Library")
    os.makedirs(filepath_library, exist_ok=True)#Create directory if it doesnt exist
    #Open/Create Database
    rmdb = RetroManagerDatabase(os.path.join(default_filepath, "retromanager.db"))

    def __init__(self):
        super().__init__()

    def importGames(self, gamePaths):
        try:
            if len(gamePaths) > 0:
                for file_path in gamePaths:
                    #TODO: Check if file already exists
                    new_path = shutil.copy(file_path, filepath_library)
                    if(new_path):
                        title = (os.path.splitext(os.path.basename(new_path))[0]).split('.')[0]
                        rmdb.addGame(title, new_path)
                        print(f"imported file {file_path} as {title}")                        
                return True
        except Exception as e:
            print (f"RetroManagerCore~importGames: {str(e)}")
        return False
       
    def createDeviceConfigFile(self, mountpoint):
        #Check the drive is actually mounted
        
        #Check if a config file already exists
            
        #Create the empty config file
        
        return True
        
    def retrieveGamesFromLocation(self, basePath):
        return False