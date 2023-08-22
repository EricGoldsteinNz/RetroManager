#GUI imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from RetroManagerDatabase import *
from RetroManagerCore import *

import psutil

driveHistory = []
openDevices = []



RMCore = RetroManagerCore()


#SubClass QMainWindow to create a Tadpole general interface
class MainWindow (QMainWindow):

    library_columns_Title = "Title"
    library_columns_Console = "Console"
    library_columns_Rating = "Rating"
    library_columns_Series = "Series"
    library_columns_Publisher = "Publisher"
    
    library_columns = [
        "Title",
        "Console",
        "Rating",
        "Series",
        "Publisher"
    ]    
    
    gameslist = []
    
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
        
        # Right Click Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.loadRightClickMenu)
        
        self.layout = QGridLayout(widget)
        
        #Create the tabs widget and add it to the main layout
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        #Create Library Tab
        self.tab_library = QWidget()
        self.tabs.addTab(self.tab_library, "Library")
        
        self.tab_library.layout = QGridLayout(self.tab_library)

        #Game Table Widget
        self.tbl_gamelist = QTableWidget()
        self.tbl_gamelist.setColumnCount(5)
        self.tbl_gamelist.setHorizontalHeaderLabels(self.library_columns)
        self.tbl_gamelist.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.tbl_gamelist.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)       
        self.tab_library.layout.addWidget(self.tbl_gamelist)
        self.tbl_gamelist.itemChanged.connect(self.catchTableItemChanged)
        self.tbl_gamelist.show()
        
        """
        self.tblview_gamelist = QTableView()
        self.tblGameModel = rmGameTableModel()
        #TODO set gamemodel data
        self.tblview_gamelist.setModel(self.tblGameModel)
        self.tblview_gamelist.show();
        """
        #load All Game Data on Opening
        self.loadAllGamesToTable()
        
        
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
        action_openDevice = QAction("Open Device", self, triggered=self.openDevice)
        self.menu_file.addAction(action_openDevice)
        action_exit = QAction("E&xit", self, shortcut="Ctrl+Q",triggered=self.close)
        self.menu_file.addAction(action_exit)
        self.action_Test = QAction("Test Function", self,triggered=self.testFunction)
        self.menu_file.addAction(self.action_Test)
        
        
        #Library Menu     
        self.menu_library = self.menuBar().addMenu("&Library")
        self.action_AddGames = QAction("Add Games...", self, triggered=self.importGames)
        self.menu_library.addAction(self.action_AddGames)
        
        
        
    def loadRightClickMenu(self, pos):
        menu = QMenu()

        #Send to Device
        rightClick_sendToDevice = menu.addMenu('Send to Device')
        if len(openDevices) == 0:
            device_option = rightClick_sendToDevice.addAction("No Devices Connected")
            device_option.setEnabled(False)
        else:
            for device in openDevices:
                device_option = rightClick_sendToDevice.addAction(device)
                
                device_option.triggered.connect(lambda checked, device=device: self.sendGamesToDevice(device))


        # Position
        menu.exec_(self.mapToGlobal(pos))
        
    def sendGamesToDevice(self, device):
        print(f"Sending games to device {device}")
        
    
    def handle_TableEdit(self, tableWidget):
        print(f"table widget changed {tableWidget}")

    def about(self):
        QMessageBox.about(self, "About RetroManager","RetroManager was created by EricGoldstein because he got sick of losing all his saves")

    def testFunction(self):
        print("Running Test Function")
        RMCore.rmdb.fetchGames()
    
    
    def openDevice(self, mountpoint):
        print(f"Opening Device")
        openDevices.append(mountpoint)
        #Create Library Tab
        tab_openDevice = QWidget()
        self.tabs.addTab(tab_openDevice, mountpoint)
        tab_openDevice.layout = QGridLayout(tab_openDevice)

        #Game Table Widget
        tbl_gamelist = QTableWidget()
        tbl_gamelist.setColumnCount(5)
        tbl_gamelist.setHorizontalHeaderLabels(self.library_columns)
        tbl_gamelist.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        tbl_gamelist.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)       
        tab_openDevice.layout.addWidget(tbl_gamelist)
        tbl_gamelist.itemChanged.connect(self.catchTableItemChanged)
        tbl_gamelist.show()    

        #TODO: Retrieve the games from the device
        
        
    
    
    
    #tableData is a list of RetroManagerDatabase rmGame Objects
    def reloadTable(self, tableData):
        print(f"Reloading Table with {len(tableData)} items")
        #Disable cell change tracking to avoid infinite looping
        self.tbl_gamelist.itemChanged.disconnect()
        self.tbl_gamelist.setRowCount(len(tableData))
        for i,game in enumerate(tableData):            
            self.tbl_gamelist.setItem(i,0,QTableWidgetItem(f"{game.title}")) #Filename
            self.tbl_gamelist.setItem(i,1,QTableWidgetItem(f"{game.console}")) #Console
            self.tbl_gamelist.setItem(i,2,QTableWidgetItem(f"{game.rating}")) #Rating
            self.tbl_gamelist.setItem(i,3,QTableWidgetItem(f"{game.series}")) #Series
            self.tbl_gamelist.setItem(i,4,QTableWidgetItem(f"{game.publisher}")) #Publisher
        #Restore cell change tracking
        self.tbl_gamelist.itemChanged.connect(self.catchTableItemChanged)


    def loadAllGamesToTable(self):
        self.gameslist = RMCore.rmdb.fetchGames()
        print(f"gameslist contains {len(self.gameslist)}")
        self.reloadTable(self.gameslist)
    
    def importGames(self):
        try:
            #Use the multi file select dialog to allow bulk importing
            file_paths = QFileDialog.getOpenFileNames(self, 'Select one or more games to import', '',"All Files (*.*)")
            #Pass the games to the Core to handle parsing and storage
            return RMCore.importGames(file_paths)
        except Exception as e:
            print (f"{str(e)}")
        return False
        
    def catchTableItemChanged(self, item):
        print(f"Cell changed ({item.row()},{item.column()})")
        print(f"Changing linked game ({self.gameslist[item.row()].title})")
        columnType = self.library_columns[item.column()]     
        if columnType == self.library_columns_Title:
            self.gameslist[item.row()].title = item.text()
            rmdb.updateGame(self.gameslist[item.row()])            
        elif columnType == self.library_columns_Console:
            self.gameslist[item.row()].console = item.text()
            rmdb.updateGame(self.gameslist[item.row()])   
    
    
    def checkForNewDevices(self):
        #Get the list of drives and compare it to the past history
        for drive in psutil.disk_partitions():            
            if drive not in self.driveHistory:
                if self.checkIfDeviceIsRetroGames(drive):
                    print(f"NEWDRIVEDETECTED: {self.driveHistory}")
                    window.status_bar.showMessage(f"New Drive Detected - {drive.mountpoint}", 20000)
                    self.openDevice(drive.mountpoint)
        self.driveHistory = psutil.disk_partitions()
        #TODO: Should probably check that all the open devices are still actually connected.
    
    def checkIfDeviceIsRetroGames(self, drive):
        print(f"TODO: Implement drive check for {drive}")
        return True
        
    
    def testFunction(self):
        print("Using Test Function")

#Initialise the Application
app = QApplication(sys.argv)

# Build the Window
window = MainWindow()
window.show()


window.driveHistory = psutil.disk_partitions()
# Listen for Devices Time
timer = QTimer()
timer.timeout.connect(window.checkForNewDevices)
timer.start(1000)

app.exec()

