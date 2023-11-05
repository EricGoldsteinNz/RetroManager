import sqlite3
import logging
import hashlib

class RetroManagerDatabase():


    def __init__(self, location):
        super().__init__()
        # Connect to the database, if it doesnt exist this call will instantiate one
        logging.info(f"Creating or opening {location}")
        self.db = sqlite3.connect(location)      
        self.dbcursor = self.db.cursor()
        
        #Validate the required tables exist
        # TODO need to validate that the tables have the correct columns as well.
        res = self.dbcursor.execute("SELECT name FROM sqlite_master where name = 'developer'")
        if (res.fetchone() is None):
            logging.info("RMDB: (developer) table not found, creating one")
            self.dbcursor.execute("CREATE TABLE developer(id INTEGER PRIMARY KEY, name TEXT)")
        
        res = self.dbcursor.execute("SELECT name FROM sqlite_master where name = 'series'")
        if (res.fetchone() is None):
            logging.info("RMDB: series table not found, creating one")
            self.dbcursor.execute("CREATE TABLE series(id INTEGER PRIMARY KEY, name TEXT)")
        
        res = self.dbcursor.execute("SELECT name FROM sqlite_master where name = 'games'")
        if (res.fetchone() is None):
            logging.info("RMDB: (games) table not found, creating one")
            self.dbcursor.execute("""
            CREATE TABLE games( id INTEGER PRIMARY KEY, 
                                title TEXT, 
                                filepath TEXT, 
                                console, 
                                developerid, 
                                seriesid, 
                                rating INTEGER CHECK(rating >=0 AND rating <=100), 
                                date TIMESTAMP,
                                sha256hash TEXT,
                                FOREIGN KEY(developerid) REFERENCES developer(id), 
                                FOREIGN KEY(seriesid) REFERENCES series(id)
                                )""")        

        res = self.dbcursor.execute("SELECT name FROM sqlite_master where name = 'saves'")
        if (res.fetchone() is None):
            logging.info("RMDB: (saves) table not found, creating one")
            self.dbcursor.execute("""
            CREATE TABLE saves( id INTEGER PRIMARY KEY,
                                gameid, 
                                title TEXT, 
                                filepath TEXT, 
                                notes TEXT, 
                                date TIMESTAMP,
                                sha256hash TEXT,
                                FOREIGN KEY(gameid) REFERENCES games(id)
                                )""")

    def validateTableGames(self):
        self.ensureColumnIsInTable("games","sha256hash","TEXT")


    def ensureColumnIsInTable(self, table, column, data_type):
        # TODO check table exists
        # TODO check if column already exists rather than assuming ALTER wont break anything
        try:
            self.dbcursor.execute(f"ALTER TABLE {table} ADD {column} {data_type}")
        except Exception as e:
            logging.info(f"RMDB~ValidateTableGames: not adding column ({column}) to ({table})")



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
            #print(row)
            game = rmGame(row[0], row[1], row[2], row[3])
            resultsList.append(game)
        print(f"Found {len(resultsList)} games")
        return resultsList

    def fetchGameByTitle(self, title :str):
        print(f"Searching for game by title ({title})")
        result = self.dbcursor.execute("SELECT id, title, filepath, console FROM games WHERE title=?", title)
        result = result.fetchone()
        if not result is None: 
            game = rmGame(result[0], result[1], result[2], result[3])
            return game    
        else:
            return None
        
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
    
    """
    Delete Games
    """


    """
    Create Save
    """


    """
    Get Save
    """


    """
    Update Save
    """
    

    """
    Delete Save
    """
    
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
        
class rmSave():

    def __init__(self, gameID, saveFilePath, saveFormat):
        super().__init__()
        self.gameDBID = gameID
        self.filePath = saveFilePath
        self.saveFormat = saveFormat
        self.hash = ""
        try:
            BUF_SIZE = 4194304  # Reading in chunks of 4MB. There is no reason that this has to be this value, we can change it to anything.
            sha256 = hashlib.sha256()
            with open(saveFilePath, 'rb') as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    sha256.update(data)
            self.hash = sha256.hexdigest()
        except Exception as e:
            logging.error(f"RetroManageDatabase~rmSave: {str(e)}")