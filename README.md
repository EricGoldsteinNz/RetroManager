# RetroManager

RetroManager is a ROM library manager. It helps store, edit, organise, and catalog your ROMs. It maintains a local library of your ROMs, cover art, metadata, and saves to make having multiple Retro handhelds (or other devices) easier. It is a cross-platform solution that works on Windows, Mac, and Linux.


## Installation Guide
If you are running on Windows you should download the pre-built exe from https://github.com/EricGoldsteinNz/RetroManager/releases

However if you are running on a different platform or would like to build from source the only pre-requisite is that you have python3 installed. 

1. From your terminal of choice, install the required libraries by running:
    python -m pip install -r ..\..\requirements.txt

2. You can then run RetroManager in the local python environment by running:
    python RetroManager.py

3. If you are on a Windows PC and would like to build your own executable you can run:
    .\build.bat
    This will create an exe file inside .\dist\

## Using RetroManager
When you first open RetroManager it will automatically create a database and library inside your home directory.
On Windows this will be in C:\Users\<Username>\RetroManager

You can add games through the menu or toolbar.