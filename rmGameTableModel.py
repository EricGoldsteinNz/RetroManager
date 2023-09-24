from QtCore import QAbstractTableModel
from RetroManagerDatabase import rmGame

class rmGameTableModel(QAbstractTableModel):
    rmGame gameList = null
    displayedColumns = [
        "Title",
        "Console",
        "Rating",
        "Series",
        "Publisher"
    ]


    def __init__(self, parent = None):
        super().__init__()

    def rowCount(self, parent = None):
        if gameList == null:
            return 0
        else:
            return len(gameList)

    def columnCount(self, parent = None):
        return len(displayedColumns)
       
    def data(self, index, role = Qt.DisplayRole):
        if (role == Qt.DisplayRole):
            return gameList[index.row].title
        return ""