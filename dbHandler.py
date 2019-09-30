import sqlite3
import pandas

#to-do: this entire file will need error handling

class DataBaseHandler:
    def updateData(self, identifier, params, values):  #params and values have to be same length
        if (self.findUser(identifier).empty):
            return "Couldn't find any user with that TG ID or nick!"

        query = ""
        sqlParams = ""
        if (len(params) == len(values) and (len(params)) > 0):
            for i in range(len(params)):
                query += params[i] + " = "
                sqlParams += params[i]

                if (type(values[i]) is int):
                    query += values[i]
                elif (isinstance(values[i], basestring)):
                    query += '"' + values[i] + '"'
                else:
                    print("Error: Can't update data, value is of unexpected type")

                if i < (len(params) - 1):
                    query += ", "
                    sqlParams += ", "
        else:
            print "Error while updating SQL Data, parameters and values are not of equal length (or of length 0)"

        sql = ""
        sqlSearch = ""
        if type(identifier) is int:
            sql = "UPDATE users SET %s WHERE ID = %d" % (query, identifier)
            sqlSearch = "SELECT %s FROM users WHERE ID = %d;" % (sqlParams, identifier)
        elif isinstance(identifier, basestring):
            sql = "UPDATE users SET %s WHERE nick = \"%s\"" % (query, identifier)
            sqlSearch = "SELECT %s FROM users WHERE nick = \"%s\";" % (sqlParams, identifier)
        
        rows = pandas.read_sql_query(sqlSearch, self.db)

        output = ""
        if (len(rows) != 0):
            output = "\nOld data was: \n<code>" + str(rows) + "</code>"

        self.dbCursor.execute(sql)
        self.db.commit()
        return "Successfully updated data!" + output

    def loadData(self, identifier, params):
        if (self.findUser(identifier).empty):
            return "Couldn't find any user with that TG ID or nick!"

        query = ""
        if len(params) > 0:
            for i in range(len(params)):
                query += params[i]
                if i < (len(params) - 1):
                    query += ", "
        else:
            print "Error while reading SQL Data, list of search parameters is empty"

        if type(identifier) is int:
            sqlSearch = "SELECT %s FROM users WHERE ID = %d;" % (query, identifier)
        elif isinstance(identifier, basestring):
            sqlSearch = "SELECT %s FROM users WHERE nick = \"%s\";" % (query, identifier)
        
        self.dbCursor.execute(sqlSearch)
        results = self.dbCursor.fetchall()
        return results

    def addUser(self, id, nick, msg = "None", subToReports = 0,  admin = 0):
        if (self.findUser(id).empty):
            self.dbCursor.execute("INSERT INTO users (ID, nick, msg, subToReports, admin) VALUES (?, ?, ?, ?, ?);", [id, nick, msg, subToReports, admin])
            self.db.commit()
            return "User successfully added!"
        else:
            return "User with this TG ID exists already!"

    def rmUser(self, identifier):
        if (self.findUser(identifier).empty):
            return "Couldn't find any user with that TG ID or nick!"

        if type(identifier) is int:
            self.dbCursor.execute("DELETE FROM users WHERE ID = %d;" % (identifier))
        elif isinstance(identifier, basestring):
            self.dbCursor.execute("DELETE FROM users WHERE nick = \"%s\";" % (identifier))

        self.db.commit()
        return "User successfully deleted!"

    def isAdmin(self, ID):
        results = self.dbCursor.execute("SELECT ID FROM users WHERE admin = 1;")    #is a list of tuples, has to be accessed with [0] later
        for result in results:
            if (ID == int(result[0])):
                return True
        return False

    def findUser(self, identifier):
        result = None
        if type(identifier) is int:
            result = pandas.read_sql_query("SELECT ID FROM users WHERE ID = %d;" % (identifier), self.db)
        elif isinstance(identifier, basestring):
            result = pandas.read_sql_query("SELECT ID FROM users WHERE nick = \"%s\";" % (identifier), self.db)
        return result

    def showUser(self, identifier = 0):
        if (type(identifier) is int):
            if (identifier == 0):
                output = "<code>" + str(pandas.read_sql_query("SELECT ID, nick, subToReports, admin FROM users;", self.db)) + "</code>"
                return output
            else:
                output = "<code>" + str(pandas.read_sql_query("SELECT ID, nick, subToReports, admin FROM users WHERE ID = %d;"  % (identifier), self.db)) + "</code>"
                output += "\nCustom Message:<i>" + pandas.read_sql_query("SELECT msg FROM users WHERE ID = %d;" % (identifier), self.db).to_string(header=False, index=False) + "</i>"
                if (self.findUser(identifier).empty):
                    return "Couldn't find any user with that TG ID or nick!"
                return output
        elif (isinstance(identifier, basestring)):
            output = "<code>" + str(pandas.read_sql_query("SELECT ID, nick, subToReports, admin FROM users WHERE nick = \"%s\";"  % (identifier), self.db)) + "</code>"
            output += "\nCustom Message:<i>" + pandas.read_sql_query("SELECT msg FROM users WHERE nick = \"%s\";" % (identifier), self.db).to_string(header=False, index=False) + "</i>"
            if (self.findUser(identifier).empty):
                return "Couldn't find any user with that TG ID or nick!"
            return output

        return "Error: Can't show user, identifier is of unexpected type"

    def open(self, name):
        self.db = sqlite3.connect(name)
        self.dbCursor = self.db.cursor()

    def close(self):
        self.db.close()