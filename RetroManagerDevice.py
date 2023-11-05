import os
import configparser
import logging
import shutil



from RetroManagerCore import RetroManagerCore, rmGame
import rm_util
 


class RetroManagerDevice():
    _static_ConfigFileName = "RetroManager.conf"
    # [General]
    _static_general = "General"
    _static_general_devicename = "Name"
    _static_general_devicename_DEFAULT = "Unnamed Device"
    _static_general_deviceType = "Type"
    _static_general_deviceType_DEFAULT = "Generic"
    # [ROMLocations]
    _static_ROMLocations = "ROMLocations"  
    _static_ROMLocations_DEFAULT = "DEFAULT"
    _static_ROMLocations_DEFAULT_DEFAULT = "ROMS"
    _static_ROMLocations_GB = "Nintendo - Game Boy"
    _static_ROMLocations_GB_DEFAULT = "GB"
    _static_ROMLocations_GBC = "Nintendo - Game Boy Color"
    _static_ROMLocations_GBC_DEFAULT = "GBC"
    _static_ROMLocations_GBA = "Nintendo - Game Boy Advance"
    _static_ROMLocations_GBA_DEFAULT = "GBA"
    _static_ROMLocations_NES = "Nintendo - Nintendo Entertainment System"
    _static_ROMLocations_NES_DEFAULT = "FC"
    _static_ROMLocations_SNES = "Nintendo - Super Nintendo Entertainment System"
    _static_ROMLocations_SNES_DEFAULT = "SFC"
    _static_ROMLocations_GG = "Sega - Game Gear"
    _static_ROMLocations_GG_DEFAULT = "GG"
    _static_ROMLocations_MD = "Sega - Mega Drive - Genesis"
    _static_ROMLocations_MD_DEFAULT = "MD"

    _static_ROMLocationsDictionary = {
    _static_ROMLocations_GB : _static_ROMLocations_GB_DEFAULT,
    _static_ROMLocations_GBC : _static_ROMLocations_GBC_DEFAULT,
    _static_ROMLocations_GBA : _static_ROMLocations_GBA_DEFAULT,
    _static_ROMLocations_NES : _static_ROMLocations_NES_DEFAULT,
    _static_ROMLocations_SNES : _static_ROMLocations_SNES_DEFAULT,
    _static_ROMLocations_GG : _static_ROMLocations_GG_DEFAULT,
    _static_ROMLocations_MD : _static_ROMLocations_MD_DEFAULT,
    }


    # [SaveLocations]
    _static_SaveLocations = "SaveLocations"
    


    name = ""
    mountpoint = ""

    def __init__(self, mountpoint):
        super().__init__()
        print(f"RetroManagerDevice~Init: Opening Device {mountpoint}")
        self.mountpoint = mountpoint
        self.configFilePath = os.path.join(mountpoint, self._static_ConfigFileName)
        self.config = configparser.ConfigParser()
        #Check if config file exists on the device
        if not os.path.exists(self.configFilePath):
            #Config file not found, create a default one
            self.createDefaultConfig()
            self.setDeviceName(mountpoint)
        #Double check that the config file now exists
        if not os.path.exists(self.configFilePath):
            #TODO replace this with a proper exception
            raise Exception       
        self.config.read(self.configFilePath)
    
    
    def isRetroManagerDrive(mountpoint):
        configFile= os.path.join(mountpoint, RetroManagerDevice._static_ConfigFileName)
        if os.path.exists(configFile):
            return True
        return False
    
    def scanForGames(self):
        print(f"Tryng to scan for games")
        gamesList = []
        for folder_name, sub_folders, file_names in os.walk(self.mountpoint):
                for filename in file_names:
                    # Filter for save files
                    if rm_util.check_is_game_file(filename):
                        #print(f"Found game: {folder_name} ; {filename}")
                        # Strip the extension to create a title
                        title = os.path.splitext(filename)[0]
                        # Rebuild the filepath
                        file_path = os.path.join(folder_name, filename)
                        # Create the rmGame Objects
                        gamesList.append(rmGame(-1, title, file_path, rm_util.detectConsoleFromROM(file_path)))
        return gamesList  
    
    def sendGameToDevice(self, game :rmGame):
        #if len(gameslist) == 0:
        #    print("RetroManagerDevice~sendGamestoDevice: Cant send an empty list of games mate")
        print(f"Sending ({game.title}) to ({self.name})")
        destination = self.getROMLocations_DEFAULT()
        if game.console.lower() == rm_util.console_gb.lower(): #Game Boy
            destination = self.getROMLocations_GameBoy()
            
        # Copy the game to the device    
        shutil.copy(game.filePath,os.path.join(self.mountpoint, destination))
        # Copy the thumbnail
        cover_path = os.path.splitext(game.filePath)[0]
        for ext_img in rm_util.supported_img_ext:
            imgFile = cover_path + ext_img
            if os.path.exists(imgFile):
                shutil.copy(imgFile, os.path.join(self.mountpoint, destination))
                continue
        # TODO Copy the saves
    

    """
    """
    def sendSavesToLibrary(self,game :rmGame):
        logging.info(f"RetroManagerDevice~sendSavesToLibrary: {game.title}")

    def sendSavesToDevice(self, game:rmGame):
        logging.info(f"RetroManagerDevice~sendSavesToDevice: {game.title}")


    def createDefaultConfig(self):
        """
        WARNING: Be careful when calling this function as it will overwrite the 
        configuration file in the provided path if one exists.
        """
        # Clear the running config
        self.config = configparser.ConfigParser()
        # We dont need to create the sections, error handling in setVariable will create those for us
        self.setDeviceName(self._static_general_devicename_DEFAULT)
        self.setDeviceType(self._static_general_deviceType_DEFAULT)
        self.setROMLocations_DEFAULT(self._static_ROMLocations_DEFAULT_DEFAULT)
        self.setROMLocations_GameBoy(self._static_ROMLocations_GB_DEFAULT)
        self.setROMLocations_GameBoyColor(self._static_ROMLocations_GBC_DEFAULT)
        self.setROMLocations_GameBoyAdvance(self._static_ROMLocations_GBA_DEFAULT)
        self.saveConfig()


    def saveConfig(self):
        with open(self.configFilePath, 'w') as newConfigFile:
            self.config.write(newConfigFile)

    def setVariable(self, section, option, value):
        try:
            #Check the section exists, if it doesnt then create it
            if not self.config.has_section(section):
                self.config[section] = {}
            self.config[section][option] = value
            self.saveConfig()
        except Exception as e:
            logging.error("RetroManagerDevice~setVariable {e}")

            
    def getVariable(self, section, option, default):
        if (self.config.has_option(section,option)):
            return self.config[section][option]
        logging.warn(f"Returning default for ({section})({option})")
        return default
    
    def setDeviceName(self, newName : str):
        logging.info(f"Setting DeviceName to ({newName})")
        self.setVariable(self._static_general, self._static_general_devicename, newName)

    def getDeviceName(self):
        return self.getVariable(self._static_general, self._static_general_devicename, self._static_general_devicename_DEFAULT)
    
    def setDeviceType(self, newType : str):
        logging.info(f"Setting DeviceName to ({newType})")
        self.setVariable(self._static_general, self._static_general_deviceType, newType)

    def getDeviceType(self):
        return self.getVariable(self._static_general, self._static_general_deviceType, self._static_general_deviceType_DEFAULT)

    def setROMLocations_DEFAULT(self, newLocation : str):
        logging.info(f"Setting ROM Location for DEFAULT to ({newLocation})")
        self.setVariable(self._static_ROMLocations, self._static_ROMLocations_DEFAULT, newLocation)

    def getROMLocations_DEFAULT(self):
        return self.getVariable(self._static_ROMLocations, self._static_ROMLocations_DEFAULT, self._static_ROMLocations_DEFAULT_DEFAULT)

    def setROMLocations_GameBoy(self, newLocation : str):
        logging.info(f"Setting ROM Location for Game Boy to ({newLocation})")
        self.setVariable(self._static_ROMLocations, self._static_ROMLocations_GB, newLocation)

    def getROMLocations_GameBoy(self):
        return self.getVariable(self._static_ROMLocations, self._static_ROMLocations_GB, self._static_ROMLocations_GB_DEFAULT)

    def setROMLocations_GameBoyColor(self, newLocation : str):
        logging.info(f"Setting ROM Location for Game Boy Color to ({newLocation})")
        self.setVariable(self._static_ROMLocations, self._static_ROMLocations_GBC, newLocation)

    def getROMLocations_GameBoyColor(self):
        return self.getVariable(self._static_ROMLocations, self._static_ROMLocations_GBC, self._static_ROMLocations_GBC_DEFAULT)

    def setROMLocations_GameBoyAdvance(self, newLocation : str):
        logging.info(f"Setting ROM Location for Game Boy Advance to ({newLocation})")
        self.setVariable(self._static_ROMLocations, self._static_ROMLocations_GBA, newLocation)

    def getROMLocations_GameBoyAdvance(self):
        return self.getVariable(self._static_ROMLocations, self._static_ROMLocations_GBA, self._static_ROMLocations_GBA_DEFAULT)


    # TODO Finish adding getters and setters for ROM Locations








