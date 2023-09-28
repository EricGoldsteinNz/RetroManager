#GUI imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

#RetroManager imports
from RetroManagerDatabase import *
from RetroManagerCore import *
from RetroManagerDevice import RetroManagerDevice

import psutil
import configparser
import os
import logging

# List of devices that we're detected on last scan, this is used to compare to find any new devices
driveHistory = []
# this is a list of the open devicetabs
openDevices = []

RMCore = RetroManagerCore()

static_LoggingPath = os.path.join(os.path.expanduser("~"), "RetroManager", "retromanager.log")  

#SubClass QMainWindow to create a Tadpole general interface
class MainWindow (QMainWindow):

    library_columns_Title = "Title"
    library_columns_Console = "Console"
    library_columns_Rating = "Rating"
    library_columns_Series = "Series"
    library_columns_Publisher = "Publisher"
    
    library_columns = [
        library_columns_Title,
        library_columns_Console,
        library_columns_Rating,
        library_columns_Series,
        library_columns_Publisher
    ]    
    
    
    def __init__(self):
        super().__init__()
        #General winow parameters
        self.setWindowTitle("RetroManager - Handheld ROM Manager")
        widget = QWidget()
        self.setCentralWidget(widget)
        self.setMinimumSize(800,600)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        #Load the ribbon Menus  
        self.loadMenus()     
        
       
        
        self.layout = QGridLayout(widget)
        
        #Create the tabs widget and add it to the main layout
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        #Create Library Tab
        self.tab_library = QWidget()
        self.tabs.addTab(self.tab_library, "Library")
        
        self.tab_library.layout = QGridLayout(self.tab_library)
        
        self.tab_library.gameslist = []

        #Game Table Widget
        self.tab_library.tbl_gamelist = QTableWidget()
        self.tab_library.tbl_gamelist.setColumnCount(5)
        self.tab_library.tbl_gamelist.setHorizontalHeaderLabels(self.library_columns)
        self.tab_library.tbl_gamelist.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.tab_library.tbl_gamelist.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)       
        self.tab_library.layout.addWidget(self.tab_library.tbl_gamelist)
        self.tab_library.tbl_gamelist.itemChanged.connect(self.catchTableItemChanged)
        self.tab_library.tbl_gamelist.show()
        
        # Right Click Menu
        self.tab_library.tbl_gamelist.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_library.tbl_gamelist.customContextMenuRequested.connect(self.loadRightClickMenu_LibraryTable)
        
        """
        self.tblview_gamelist = QTableView()
        self.tblGameModel = rmGameTableModel()
        #TODO set gamemodel data
        self.tblview_gamelist.setModel(self.tblGameModel)
        self.tblview_gamelist.show();
        """
        #load All Game Data on Opening
        self.loadAllGamesToLibraryTable()
        
        
    def toggle_features(enable: bool):
        """Toggles program features on or off"""
        features = []

        for feature in features:
            feature.setEnabled(enable)
        
        
    def loadMenus(self):
        #File Menu     
        self.menu_file = self.menuBar().addMenu("&File")
        action_about = QAction("&About", self, triggered=self.about)
        self.menu_file.addAction(action_about)
        action_openDevice = QAction("Open Device", self, triggered=self.menu_openDevice)
        self.menu_file.addAction(action_openDevice)
        action_exit = QAction("E&xit", self, shortcut="Ctrl+Q",triggered=self.close)
        self.menu_file.addAction(action_exit)
        self.action_Test = QAction("Test Function", self,triggered=self.testFunction)
        self.menu_file.addAction(self.action_Test)
        
        
        #Library Menu     
        self.menu_library = self.menuBar().addMenu("&Library")
        self.action_AddGames = QAction("Add Games...", self, triggered=self.importGames)
        self.menu_library.addAction(self.action_AddGames)
        
        #Library Menu 
        self.action_AddGamesIcon = QAction("Add Games...", self, triggered=self.importGames)    
        self.menu_addGame= self.menuBar().addAction(self.action_AddGamesIcon)
        
    def loadRightClickMenu_LibraryTable(self, pos):
        menu = QMenu()
        activeTab = self.tabs.currentWidget()
        
        #Send to Device
        rightClick_sendToDevice = menu.addMenu('Send to Device')
        if len(openDevices) == 0:
            device_option = rightClick_sendToDevice.addAction("No Devices Connected")
            device_option.setEnabled(False)
        else:
            for tab_device in openDevices:
                name = tab_device.device.name if tab_device.device.name!="" else tab_device.device.mountpoint
                device_option = rightClick_sendToDevice.addAction(f"{name}")
                device_option.triggered.connect(lambda checked, tab_device=tab_device: self.sendGamesToDevice(tab_device))
        # Position
        menu.exec_(activeTab.mapToGlobal(pos))
        
        
    def loadRightClickMenu_DeviceTable(self, pos):
        menu = QMenu()
        activeTab = self.tabs.currentWidget()
        rightClick_sendToLibrary = menu.addAction("Send to Library")
        rightClick_sendToLibrary.triggered.connect(self.sendGamesToLibrary)
        # Position
        menu.exec_(activeTab.mapToGlobal(pos)) 
        
    def sendGamesToDevice(self, tab_device):
        #TODO add the loading window
        activeTab = self.tabs.currentWidget()
        for item in activeTab.tbl_gamelist.selectedIndexes():
            rmgameitem = activeTab.gameslist[item.row()]
            logging.info(f"RetroManager~sendGamesToDevice: Selected Game - {rmgameitem.title}")
            tab_device.device.sendGameToDevice(rmgameitem)
        #Refresh the device table
        self.reloadTable(tab_device, tab_device.device.scanForGames())

        
      
 
    def sendGamesToLibrary(self):
        activeTab = self.tabs.currentWidget()
        gamesToAdd = []
        for item in activeTab.tbl_gamelist.selectedIndexes():
            rmgameitem = activeTab.gameslist[item.row()]
            print(f"RetroManager~sendGamesToLibrary: Selected Game - {rmgameitem.title}")
            RMCore.importGame(rmgameitem)
        #Refresh the library table
        self.loadAllGamesToLibraryTable()
        return True
    
    def handle_TableEdit(self, tableWidget):
        print(f"RetroManager~handle_TableEdit: table widget changed {tableWidget}")

    def about(self):
        QMessageBox.about(self, "About RetroManager","RetroManager was created by EricGoldstein because he got sick of losing all his saves")

    def testFunction(self):
        print("Running Test Function")
        print(f"trying to read {openDevices[0].device}")
        openDevices[0].device.scanForGames()
         
    
    def menu_openDevice(self):
        print("Opening device")
        directory = os.path.normpath(QFileDialog.getExistingDirectory()) # getExistingDirectory returns filepath slashes the wrong way around in some OS, lets fix that
        if directory == '': #Check that the user actually selected a directory and didnt just close the window
            return False

        self.openDevice(directory)
    
    def openDevice(self, mountpoint):
        print(f"RetroManager~OpenDevice:    Opening Device {mountpoint}")
        device = RetroManagerDevice(mountpoint)      
        #Create Library Tab
        tab_openDevice = QWidget()
        tab_openDevice.device = device
        openDevices.append(tab_openDevice)
        tabname = ""
        if device.name == "":
            tabname = device.mountpoint
        else:
            tabname = device.name
        self.tabs.addTab(tab_openDevice, tabname)
        tab_openDevice.layout = QGridLayout(tab_openDevice)

        #Game Table Widget
        tab_openDevice.tbl_gamelist = QTableWidget()
        tab_openDevice.tbl_gamelist.setColumnCount(5)
        tab_openDevice.tbl_gamelist.setHorizontalHeaderLabels(self.library_columns)
        tab_openDevice.tbl_gamelist.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        tab_openDevice.tbl_gamelist.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)       
        tab_openDevice.layout.addWidget(tab_openDevice.tbl_gamelist)
        #Disabled this as the catch function references the library table rather than pulling the details properly
        tab_openDevice.tbl_gamelist.itemChanged.connect(self.catchTableItemChanged)
        tab_openDevice.tbl_gamelist.show()    
        
        # Right Click Menu
        tab_openDevice.tbl_gamelist.setContextMenuPolicy(Qt.CustomContextMenu)
        tab_openDevice.tbl_gamelist.customContextMenuRequested.connect(self.loadRightClickMenu_DeviceTable)
        
        #Retrieve the games from the device
        self.reloadTable(tab_openDevice, device.scanForGames())
        
    
    
    
    #tableData is a list of RetroManagerDatabase rmGame Objects
    def reloadTable(self, tab, tableData):
        print(f"Reloading Table {tab} with {len(tableData)} items")
        #Disable cell change tracking to avoid infinite looping
        tab.tbl_gamelist.itemChanged.disconnect()
        tab.gameslist = tableData
        tab.tbl_gamelist.setRowCount(len(tableData))
        for i,game in enumerate(tableData):
            #Filename
            cell_filename = QTableWidgetItem(f"{game.title}")
            cell_filename.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)            
            tab.tbl_gamelist.setItem(i,0,cell_filename) #Filename
            tab.tbl_gamelist.setItem(i,1,QTableWidgetItem(f"{game.console}")) #Console
            tab.tbl_gamelist.setItem(i,2,QTableWidgetItem(f"{game.rating}")) #Rating
            tab.tbl_gamelist.setItem(i,3,QTableWidgetItem(f"{game.series}")) #Series
            tab.tbl_gamelist.setItem(i,4,QTableWidgetItem(f"{game.publisher}")) #Publisher
        #Restore cell change tracking
        tab.tbl_gamelist.itemChanged.connect(self.catchTableItemChanged)


    def loadAllGamesToLibraryTable(self):
        self.tab_library.gameslist = RMCore.rmdb.fetchGames()
        print(f"gameslist contains {len(self.tab_library.gameslist)}")
        self.reloadTable(self.tab_library, self.tab_library.gameslist)
    
    def importGames(self):
        try:
            #Use the multi file select dialog to allow bulk importing
            file_paths, _ = QFileDialog.getOpenFileNames(self, 'Select one or more games to import', '',"All Files (*.*)")
            #Pass the games to the Core to handle parsing and storage
            RMCore.importGames(file_paths)
            self.loadAllGamesToLibraryTable()
        except Exception as e:
            print (f"{str(e)}")
        return False
        
    def catchTableItemChanged(self, item):
        #TODO: update this function to make sure the change is made to the correct tab games list. Could use active tab? 
        #but that would mean that we can never make changes to a background tab 
        print(f"Cell changed ({item.row()},{item.column()})")
        print(f"Changing linked game ({self.tab_library.gameslist[item.row()].title})")
        columnType = self.library_columns[item.column()]     
        if columnType == self.library_columns_Title:
            self.tab_library.gameslist[item.row()].title = item.text()
            RMCore.rmdb.updateGame(self.tab_library.gameslist[item.row()])            
        elif columnType == self.library_columns_Console:
            self.tab_library.gameslist[item.row()].console = item.text()
            RMCore.rmdb.updateGame(self.tab_library.gameslist[item.row()])   
    
    
    def checkForNewDevices(self):
        #Get the list of drives and compare it to the past history
        for drive in psutil.disk_partitions():            
            if drive not in self.driveHistory:
                if self.checkIfDeviceIsRetroGames(drive.mountpoint):
                    print(f"RetroManager~checkForNewDevices: New drive detected {drive.mountpoint}")
                    window.status_bar.showMessage(f"New Drive Detected - {drive.mountpoint}", 20000)
                    self.openDevice(drive.mountpoint)
        self.driveHistory = psutil.disk_partitions()
        #TODO: Should probably check that all the open devices are still actually connected.
    
    def checkIfDeviceIsRetroGames(self, drive):
        print(f"RetroManager~checkIfDeviceIsRetroGames: Checking if drive is game device: {drive}")
        return RetroManagerDevice.isRetroManagerDrive(drive)


# Initialise logging
print(f"{static_LoggingPath}")
logging.basicConfig(filename=static_LoggingPath,
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
logging.info("RetroManager Started")

#Initialise the Application
app = QApplication(sys.argv)

# Build the Window
window = MainWindow()
window.show()




#window.driveHistory = psutil.disk_partitions()
window.driveHistory = []
# Listen for Devices Time
timer = QTimer()
timer.timeout.connect(window.checkForNewDevices)
timer.start(1000)

app.exec()