import os

# Console Titles
console_gb = "Game Boy"
console_megadrive = "Sega Mega Drive"
console_nes = "NES"
console_snes = "SNES"


# Dictionary that includes supported ROM extensions. 
# If an extension is used by multiple devices it is set to a blank string ""
supported_rom_ext = {
    ".bin"  : "",
    ".bkp"  : "",
    ".dx2"  : "",
    ".fds"  : console_nes,
    ".fig"  : console_snes,
    ".gb"   : console_gb,
    ".gba"  : "GBA",
    ".gbc"  : "GBC",
    ".gcm"  : "GameCube",
    ".gd3"  : console_snes,
    ".gd7"  : console_snes,
    ".gen"  : console_snes,
    ".md"   : console_megadrive,
    ".nes"  : console_nes,
    ".nez"  : console_nes,
    ".sfc"  : console_snes,
    ".smc"  : console_snes,
    ".smd"  : console_megadrive,
    ".sms"  : "Sega Master System",
    ".zfb"  : "Arcade (Final Burn)",
    ".zfc"  : console_nes,
    ".zgb"  : "", # Used by SF2000 for Game Boy, Game Boy Color, and Game Boy Advance
    ".zip"  : "",
    ".zmd"  : console_megadrive,
    ".zsf"  : console_snes
}


supported_img_ext = [
    ".gif",
    ".jpg",
    ".jpeg",
    ".png"
]

supported_sav_ext = [
    ".sav", # Generic save ext used almost everywhere
    ".sa0",
    ".sa1",
    ".sa2",
    ".sa3",
]

def detectConsoleFromROM(romPath):
    # Check for single use filenames first  
    ext = os.path.splitext(romPath)[1].lower()
    console = supported_rom_ext.get(ext,"")
    if console != "":
        return console
    # TODO for zgb check the file size?
    # TODO if the extension is a zip or zip subtype then peek inside 
    return ""

def convertToHumanReadableFilesize(filesize : int) -> str:
    humanReadableFileSize = "ERROR"
    if filesize is None:
        humanReadableFileSize = ""
    elif filesize > 1024*1024: #More than 1 Megabyte
        humanReadableFileSize = f"{round(filesize/(1024*1024),2)} MB"
    elif filesize > 1024: #More than 1 Kilobyte
        humanReadableFileSize = f"{round(filesize/1024,2)} KB"
    else: #Less than 1 Kilobyte
        humanReadableFileSize = f"{filesize} Bytes"

def check_is_game_file(filename):
    for ext in supported_rom_ext:
        if filename.lower().endswith(ext):
            return True
    return False