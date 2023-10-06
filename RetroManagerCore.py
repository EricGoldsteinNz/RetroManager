#OS imports
import shutil
import os
import sys
import string
import configparser

from RetroManagerDatabase import *
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
        
    def retrieveGamesFromLocation(self, basePath):
        return False
    
    
        
        
