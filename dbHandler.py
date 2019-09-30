import sqlite3

#to-do: this entire file will need error handling

class DataBaseHandler:
    def addUser(self, id, nick, msg = "None", subToReports = 0,  admin = 0):
        self.open("users.db")
        self.dbCursor.execute("SELECT ID FROM users WHERE ID = %d;" % (id))
        rows = self.dbCursor.fetchall()


        if (len(rows) == 0):
            print( ("INSERT INTO users (ID, nick, msg, subToReports, admin) VALUES (%d,\"%s\", \"%s\", %d, %d);" % (id, nick, msg, subToReports, admin)) )
            self.dbCursor.execute( ("INSERT INTO users (ID, nick, msg, subToReports, admin) VALUES (%d,\"%s\", \"%s\", %d, %d);" % (id, nick, msg, subToReports, admin)) )
            self.db.commit()
            self.close()
            return "User successfully added! SQLite"
        else:
            self.close()
            return "User with this TG ID exists already!"

    def showUsers(self):
        self.open("users.db")
        self.dbCursor.execute("SELECT * FROM users;")
        output = self.dbCursor.fetchall()
        self.close()
        return output

    def open(self, name):
        self.db = sqlite3.connect(name)
        self.dbCursor = self.db.cursor()

    def close(self):
        self.db.close()

    