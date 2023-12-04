#OS imports
import hashlib
import shutil
import os
import sys
import string
import configparser

from datetime import datetime

from RetroManagerDatabase import *
import RetroManagerDevice
import rm_util



class RetroManagerCore():
    
    default_filepath = os.path.join(os.path.expanduser("~"), "RetroManager")   
    #Library (Need to make this changeable)
    filepath_library = os.path.join(default_filepath, "Library")
    os.makedirs(filepath_library, exist_ok=True)#Create directory if it doesnt exist
    #Open/Create Database
    rmdb = RetroManagerDatabase(os.path.join(default_filepath, "retromanager.db"))

    def __init__(self):
        super().__init__()


    """
    Import passed rmGame
    """
    def importGame(self, game :rmGame):
        print("Trying to import rmGame object")
        self.importGames([game.filePath])
        

    """
    Imports all games passed in a list
    """
    def importGames(self, gamePaths):
        try:
            if len(gamePaths) > 0:
                for file_path in gamePaths:
                    # TODO Check if the game is already in Database and offer to merge?

                    new_path = False
                    gamefolder = os.path.join(self.filepath_library,os.path.splitext(os.path.basename(file_path))[0])
                    # If the game folder doesn't exist then create it
                    if not os.path.exists(gamefolder):
                        os.makedirs(gamefolder, exist_ok=True)# Create directory if it doesnt exist
                    else:
                        # At this point a folder with the same name already exists so we check for and 
                        # create an incremented version
                        i = 0
                        while os.path.exists(gamefolder + f"_{i}"):
                            i = i+1
                        # when we exist we have found a folder that didnt exist  
                        gamefolder =  gamefolder + f"_{i}" 
                        os.makedirs(gamefolder, exist_ok=True)# Create directory if it doesnt exist
                    # Check if file already exists. It shouldn't. but if it does then we dont want to overwrite it. TODO or do we?
                    gameROMpath = os.path.join(gamefolder, os.path.basename(file_path))
                    if not os.path.exists(gameROMpath):
                        new_path = shutil.copy(file_path, gameROMpath)
                    if(new_path):
                        title = (os.path.splitext(os.path.basename(new_path))[0]).split('.')[0]
                        # Add the game to the database
                        self.rmdb.addGame(title, new_path, rm_util.detectConsoleFromROM(new_path))
                        logging.info(f"imported file {file_path} as {title}")
                    else:
                        logging.error(f"Didn't import {file_path}. Bailed for your protection.")

                    # Import cover image if it exists
                    cover_path = os.path.splitext(file_path)[0]
                    for ext_img in rm_util.supported_img_ext:
                        imgFile = cover_path + ext_img
                        if os.path.exists(imgFile):
                            shutil.copy(imgFile, gamefolder)

                    # Import the save games
                            
                                    
                return True
            else:
                logging.warn("RetroManagerCore~importGames: empty list of gamepaths received")
        except Exception as e:
            logging.error(f"RetroManagerCore~importGames: {str(e)}")
        return False      

    def importSaves(self, device: RetroManagerDevice):
        # Add the saves to the library
        listOfSaves = device.scanForSaves()
        print(f"Found ({len(listOfSaves)}) save files.")
        for save in listOfSaves:
            # Build the save title
            title = os.path.splitext(os.path.split(save.filePath)[1])[0] + f" - {datetime.utcfromtimestamp(os.path.getmtime(save.filePath)).strftime('%Y%m%d_%H%M%S')}"
            savefolder = os.path.join(self.filepath_library,"_saves")
            # If the save folder doesn't exist then create it
            if not os.path.exists(savefolder):
                    os.makedirs(savefolder, exist_ok=True)# Create directory if it doesnt exist
            #Copy the save to the saves folder. TODO replace this with matching it to a game
            NewSavepath = os.path.join(savefolder, title + os.path.splitext(save.filePath)[1])
            if not os.path.exists(NewSavepath):
                new_path = shutil.copy(save.filePath, NewSavepath)
            if(new_path):
                sha256hash = compute_sha256(new_path)
                self.rmdb.createSave(save.gameDBID, title, new_path, "", os.path.getmtime(save.filePath), sha256hash)
            else:
                logging.error(f"RetroManagerCore~importSaves: ERROR importing save ({NewSavepath})")

        return False   

    def retrieveGamesFromLocation(self, basePath):
        return False

def compute_sha256(file_name):
    hash_sha256 = hashlib.sha256()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()    
    
        
        
