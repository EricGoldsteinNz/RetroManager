#OS imports
import shutil
import os
import sys
import string
import configparser

from RetroManagerDatabase import *


#supported_rom_ext = [
#    "bin", "bkp", "fig", "gen", "sfc", "gd3", "gd7", "dx2", "bsx", "swc", "nes",
#    "nfc", "fds", "unf", "gba", "agb", "gbz", "gbc", "gb", "sgb",  "md", "smc", "smd", "sms", "zfb", "zfc", "zgb", "zip", "zmd", "zsf"
#]

# Dictionary that include supported ROM extensions. 
# If an extension is used by multiple devices it is set to a blank string ""
supported_rom_ext = {
    ".bin"  : "",
    ".bkp"  : "",
    ".dx2"  : "",
    ".fds"  : "NES",
    ".fig"  : "SNES",
    ".gb"   : "Game Boy",
    ".gba"  : "GBA",
    ".gbc"  : "GBC",
    ".gcm"  : "GameCube",
    ".gd3"  : "SNES",
    ".gd7"  : "SNES",
    ".gen"  : "SNES",
    ".md"   : "MegaDrive",
    ".nes"  : "NES",
    ".nez"  : "NES",
    ".sfc"  : "SNES",
    ".smc"  : "SNES",
    ".smd"  : "MegaDrive",
    ".sms"  : "Sega Master System",
    ".zfb"  : "Arcade (Final Burn)",
    ".zfc"  : "NES",
    ".zgb"  : "", # Used by SF2000 for Game Boy, Game Boy Color, and Game Boy Advance
    ".zip"  : "",
    ".zmd"  : "MegaDrive",
    ".zsf"  : "SNES"
}


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
                    # Check if file already exists. It shouldn't. but if it does then we 
                    gameROMpath = os.path.join(gamefolder, os.path.basename(file_path))
                    if not os.path.exists(gameROMpath):
                        new_path = shutil.copy(file_path, gameROMpath)
                    if(new_path):
                        title = (os.path.splitext(os.path.basename(new_path))[0]).split('.')[0]
                        # Add the game to the database
                        self.rmdb.addGame(title, new_path, RetroManagerCore.detectConsoleFromROM(new_path))
                        logging.info(f"imported file {file_path} as {title}")
                    else:
                        logging.error(f"Didn't import {file_path}. Bailed for your protection.")                     
                return True
            else:
                logging.warn("RetroManagerCore~importGames: empty list of gamepaths received")
        except Exception as e:
            logging.error(f"RetroManagerCore~importGames: {str(e)}")
        return False
       
    def createDeviceConfigFile(self, mountpoint):
        #Check the drive is actually mounted
        if not os.path.exists(mountpoint):
            logging.error(f"RetroManagerCore~createDeviceConfigFile: failed to find {mountpoint}")
            return False
        #Check if a config file already exists
            
        #Create the empty config file
        
        return True
        
    def retrieveGamesFromLocation(self, basePath):
        return False
    
    def check_is_game_file(filename):
        for ext in supported_rom_ext:
            if filename.lower().endswith(ext):
                return True
        return False
    
    def detectConsoleFromROM(romPath):
        # Check for single use filenames first  
        ext = os.path.splitext(romPath)[1].lower()
        console = supported_rom_ext.get(ext,"")
        if console != "":
            return console
        # TODO if the extension is a zip or zip subtype then peek inside 


        return ""
        
        
