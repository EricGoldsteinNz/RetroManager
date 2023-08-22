import sqlite3

class RetroManagerDatabase():


    def __init__(self, location):
        super().__init__()
        # Connect to the database, if it doesnt exist this call will instantiate one
        print(f"Creating or opening {location}")
        self.db = sqlite3.connect(location)
        
        self.dbcursor = self.db.cursor()
        
        #Validate the required tables exist
        res = self.dbcursor.execute("SELECT name FROM sqlite_master where name = 'developer'")
        if (res.fetchone() is None):
            self.dbcursor.execute("CREATE TABLE developer(id INTEGER PRIMARY KEY, name TEXT)")
        
        res = self.dbcursor.execute("SELECT name FROM sqlite_master where name = 'series'")
        if (res.fetchone() is None):
            self.dbcursor.execute("CREATE TABLE series(id INTEGER PRIMARY KEY, name TEXT)")
        
        res = self.dbcursor.execute("SELECT name FROM sqlite_master where name = 'games'")
        if (res.fetchone() is None):
            self.dbcursor.execute("""
            CREATE TABLE games( id INTEGER PRIMARY KEY, 
                                title TEXT, 
                                filepath TEXT, 
                                console, 
                                developerid, 
                                seriesid, 
                                rating INTEGER CHECK(rating >=0 AND rating <=100), 
                                date TIMESTAMP,
                                FOREIGN KEY(developerid) REFERENCES developer(id), 
                                FOREIGN KEY(seriesid) REFERENCES series(id)
                                )""")
                                
    """
    This function retrieves a list of games from the RetroManagerDatabase.
    A filter string can be supplied, which currently does nothing.
    If no filter is supplied then all games are returned.
    
    Returns: a list of rmGame objects representing the games in the database
    """
    def fetchGames(self, filter=""):
        print(f"pulling games using filter ({filter})")
        result = self.dbcursor.execute("SELECT id, title, filepath, console FROM games ORDER BY title")
        resultsList = []
        
        for row in result:
            print(row)
            game = rmGame(row[0], row[1], row[2], row[3])
            resultsList.append(game)
        print(f"Found {len(resultsList)} game")
        return resultsList
        
        
    def addGame(self, title="", filepath="", console="", rating=-1):
        try:
            print(f"RMDB~Adding game: {title}")
            self.dbcursor.execute("INSERT INTO games(title, filepath, console) values (?,?,?)",(title, filepath, console))
            self.db.commit()
            return True
        except Exception as e:
            print(f"error while adding game: {(e)}")
        return False
    
    def updateGame(self, game):
        try:
            if game.dbID == -1:
                print(f"RMDB~updateGame invalid databaseID passed in")
                return False
            print(f"RMDB~Updating game: {game.title}")
            self.dbcursor.execute("UPDATE games SET title = ?, filepath = ?, console = ? WHERE id = ?",(game.title, game.filePath, game.console, game.dbID))
            self.db.commit()
            return True
        except Exception as e:
            print(f"error while updating game: {(e)}")
        return False
    
    
    def addSeries(self, name):
        print(f"Adding series: {name}")
        
    def createFavouritesList(self, title : str): 
        print(f"Creating new Favourites list: {title}")
        
class rmGame():
    dbID = -1
    title = ""
    filePath = ""
    console = ""
    series = ""
    publisher = ""
    rating = ""


    def __init__(self, gameID, gameTitle, gameFilePath, gameConsole):
        super().__init__()
        self.dbID = gameID
        self.title = gameTitle
        self.filePath = gameFilePath
        self.console = gameConsole
        