import psycopg2

class Connection():
    def __init__(self):
        if hasattr(self, 'conn') == False or self.conn != 0:
            print("Connecting to database...")
            self.conn = psycopg2.connect(database="caoa2018", user = "cristianomartinsm", password = "cristiano", host = "localhost", port = "5432")
