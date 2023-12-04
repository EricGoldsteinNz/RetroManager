from RetroManagerDatabase import rmGame 

class rmTableWidget(QTableWidgetItem):
    game  = null

    def __init__(self, game : rmGame):
        super().__init__()
        self.game = game
        
    def setData(self):
        print("todo")
        
    