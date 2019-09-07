import time
import random
import datetime
import telepot
import emojis
from telepot.loop import MessageLoop

SEPERATOR = ' -|- '

atkEmoji = u'\U00002694'
defEmoji = u'\U0001F6E1'
goldEmoji = u'\U0001F4B0'
variationSelector = u'\uFE0F'

def isAllowed(requestingID):
    for user in allowedUsers:
        if user[0][0] == requestingID:
            return 1

    return 0

def loadToken():
    tokenFile = open('token', 'r')
    token = tokenFile.read()
    tokenFile.close()
    return token.rstrip()

def loadUsers():
    userFile = open('users', 'r')
    user = [[1234567890, 'Nick'], 'custom message']
    users = [user]

    fileData = userFile.read()

    lines = fileData.splitlines()

    for line in lines:
        data = line.split(SEPERATOR)
        user = [ [ int(data[0]), data[1] ], data[2] ]
        users.append(user)

    del users[0]
    userFile.close()
    return users

def addUser(ID, nick):
    user = [ [ID, nick], '####' ]
    allowedUsers.append(user)
    updateUsersFile()

def rmUser(ID):
    listID = findUser(ID)
    if listID != -1:
        del allowedUsers[listID]
        updateUsersFile()
        return 1
    else:
        return 0


def findUser(identifier):
    i = 0
    try:
        while i < len(allowedUsers):
            if allowedUsers[i][0][0] == int(identifier):
                return i
            i += 1

    except ValueError:
        while i < len(allowedUsers):
            if allowedUsers[i][0][1].lower() == identifier.lower():
                return i
            i += 1

    return -1


def showUser(ID, requestingID):
    listID = findUser(ID)
    if listID != -1:
        bot.sendMessage(requestingID, "TG ID: %d\nNick: %s\nCustom message: %s" % (allowedUsers[listID][0][0], allowedUsers[listID][0][1], allowedUsers[listID][1].encode('utf-8')) )
    else:
        bot.sendMessage(requestingID, "Couldn't find any user with that TG ID or nick!")

def updateUsersFile():
    userFile = open('users', 'r')
    backup = userFile.read()
    userFile.close()

    backupFile = open('users_backup', 'w')
    backupFile.write(backup)
    backupFile.close()


    userFile = open('users', 'w')
    for user in allowedUsers:
        userFile.write("%d%s%s%s%s\n" % (user[0][0], SEPERATOR, user[0][1], SEPERATOR, user[1]))

    userFile.close()

def addCustomMessage(ID, msg):
    listID = findUser(ID)
    if listID != -1:
        output = "Successfully added custom message!"
        if allowedUsers[listID][1] != '####':
            output += " Old message was: " + allowedUsers[listID][1]

        allowedUsers[listID][1] = msg
        updateUsersFile()
        return output

def rmCustomMessage(ID): 
    listID = findUser(ID)
    if listID != -1:
        output = "Successfully deleted custom message!"
        if allowedUsers[listID][1] != '####':
            output += " Old message was: " + allowedUsers[listID][1]

        allowedUsers[listID][1] = '####'
        updateUsersFile()
        return output

    return "Couldn't find any user with that TG ID or nick!"

def loadCustomMessage(ID):
    listID = findUser(ID)
    if listID != -1:
        if allowedUsers[listID][1] != '####':
            return allowedUsers[listID][1]
    else:
        return ''

def editSettings(requestingID, command):
    if requestingID == 2065442:
        parameter = command[1]

        if parameter == 'help':
            bot.sendMessage(requestingID, "adduser \nrmuser \nshowuser \nlistusers \naddcustom \nrmcustom")

        elif parameter == 'adduser':
            ID = int(command[2])
            nick = command[3]
            if findUser(ID) == -1:
                addUser(ID, nick)
                bot.sendMessage(requestingID, "User successfully added!")
            else:
                bot.sendMessage(requestingID, "User with this TG ID exists already!")

        elif parameter == 'rmuser':
            ID = command[2]        #can be ID or nick
            if rmUser(ID):
                bot.sendMessage(requestingID, "User successfully deleted!")
            else:
                bot.sendMessage(requestingID, "Couldn't find any user with that TG ID or nick!")

        elif parameter == 'showuser':
            ID = command[2]        #can be ID or nick
            showUser(ID, requestingID)

        elif parameter == 'listusers':
            output = ''
            for user in allowedUsers:
                output += "%d, %s\n" % (user[0][0], user[0][1])

            bot.sendMessage(requestingID, output)

        elif parameter == 'addcustom':
            ID = command[2]        #can be ID or nick
            i = 3
            msg = ''
            while i < len(command):
                msg += command[i] + " "
                i += 1
            bot.sendMessage(requestingID, addCustomMessage(ID, msg))

        elif parameter == 'rmcustom':
            ID = command[2]        #can be ID or nick
            bot.sendMessage(requestingID, rmCustomMessage(ID))

    else:
        bot.sendMessage(requestingID, "I'm sorry Dave, I'm afraid I can't do that.")

def parseReport(text, type, castleGold, chat_id):
    text = text.replace(variationSelector, '', 20)

    searchString = ""
    if type == 'atk':
        searchString = atkEmoji + ':'
    elif type == 'def':
        searchString = defEmoji + ':'
    else:
        searchString = atkEmoji + ':'
        #add some sort of error handling here that's not just settings "search for attack" as default (not super needed as this is only internal data passing)

    print text.encode('unicode-escape').decode('ascii')

    statBeginPos = text.find(searchString)
    statEndPos = 0
    paranthesesPos = text.find('(', statBeginPos)
    whitespacePos = text.find(' ', statBeginPos)

    if paranthesesPos < whitespacePos and paranthesesPos != - 1:
        statEndPos = paranthesesPos
    else:
        statEndPos = whitespacePos

    if paranthesesPos == -1 and whitespacePos == -1:
        bot.sendMessage(chat_id, "Error: Punctuation/Spaces are missing, can't discern values from text")
        #return

    if statBeginPos != -1:
        stat = text[statBeginPos + len(searchString) : statEndPos]
        stat = int(stat)
    else:
        bot.sendMessage(chat_id, "Error: Couldn't find any stats!")
        #further error handling so the bot doesn't crash later when trying to calc
        #return

    goldBeginPos = text.find(goldEmoji + "Gold: ")
    goldEndPos = 0
    newLinePos = text.find('\n', goldBeginPos + len(goldEmoji + "Gold: "))
    whitespacePos = text.find(' ', goldBeginPos + len(goldEmoji + "Gold: "))

    if newLinePos < whitespacePos and newLinePos != - 1:
        goldEndPos = newLinePos
    else:
        goldEndPos = whitespacePos
    
    if newLinePos == -1 and whitespacePos == -1:
        goldEndPos = len(text)

    if goldBeginPos != -1:
        gold = text[goldBeginPos + len(goldEmoji + "Gold: ") : goldEndPos]
        int(gold)
    else:
        bot.sendMessage(chat_id, "Error: Couldn't find gold!")
        #further error handling
        return

    bot.sendMessage(chat_id, calculate([0, castleGold, stat, gold]), parse_mode="html")
    return 

def calculate(parameters):
    stat = 0
    gold = 0
    castleGold = 0
    minCastlePower = 0
    maxCastlePower = 0
    minGoldRatio = 0.0
    maxGoldRatio = 0.0

    castleGold = int(parameters[1])
    stat = int(parameters[2])
    gold = int(parameters[3])

    if gold <= 0:
        return 'Error: Invalid value for Gold, Gold cannot be 0 or lower'

    else:
        minCastlePower = (stat * castleGold) / (gold + 1)
        maxCastlePower = (stat * castleGold) / gold

        minGoldRatio = gold / float(stat)
        maxGoldRatio = (gold + 1) / float(stat)

        return '<b>Entered:</b>\nCastle Total: %d\nStat: %d\nGold: %d\n\n<b>Calculated:</b>\nTotal Atk/Def: %d - %d\nGold per stat: %.3f - %.3f' % (castleGold, stat, gold, minCastlePower, maxCastlePower, minGoldRatio, maxGoldRatio)        

def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    nick = ""
    if findUser(chat_id) != -1:
        nick = " (" + allowedUsers[findUser(chat_id)][0][1] + ")"
    print 'Received command from %d%s: %s' % (chat_id, nick, command)

    if (isAllowed(chat_id)):
        if (command == '/start'):
            bot.sendMessage(chat_id, 'Type /help to find out more')

        elif (command[0:5] == '/help'):
            bot.sendMessage(chat_id, 'To calculate send /calc <CastleGold> <RelevantStat> <Gold>')

        elif command[0:9] == '/settings':
            editSettings(chat_id, command.split())

        elif (command[0:5] == '/calc'):
            parameters = command.split()

            try: 
                if (command[5:9] == '_atk' and msg['reply_to_message']['message_id']):
                    if len(parameters) < 2:
                        bot.sendMessage(chat_id, "Error: Too few parameters, needed are <CastleGold>")
                    parseReport(msg['reply_to_message']['text'], 'atk', int(parameters[1]), chat_id)
                    return

                elif (command[5:9] == '_def' and msg['reply_to_message']['message_id']):
                    if len(parameters) < 2:
                        bot.sendMessage(chat_id, "Error: Too few parameters, needed are <CastleGold>")
                    parseReport(msg['reply_to_message']['text'], 'def', int(parameters[1]), chat_id)
                    return
                
            except KeyError:
                bot.sendMessage(chat_id, "Error: You have to reply to a report for me to parse")
                return
            except ValueError:
                bot.sendMessage(chat_id, "Error: Value for castle gold is wrong, only enter numbers")
                return
                
            if len(parameters) < 4:
                bot.sendMessage(chat_id, "Error: Too few parameters, needed are <CastleGold> <RelevantStat> <Gold>")

            else:
                if len(parameters) > 4:
                    bot.sendMessage(chat_id, "Warning: Too many parameters defined, ignoring excess values")

                try:
                    bot.sendMessage(chat_id, calculate(parameters), parse_mode="html")

                except ValueError:
                    bot.sendMessage(chat_id, "Error: Entered incorrect values (Did you enter text instead of numbers?)")

                bot.sendMessage(chat_id, loadCustomMessage(chat_id).encode('utf-8'))

                if chat_id == 280993442:    #rinka
                    bot.sendMessage(chat_id, (u'\u0414\u043E\u0431\u0440\u044B\u0439 \u0434\u0435\u043D\u044C'.encode('utf-8') + ', Cat Queen! May your castle be strong and your Pina Colada tasty!'))
                elif chat_id == 26667968:    #arctic
                    a = random.randint(0,1)
                    if a == 0:
                        bot.sendMessage(chat_id, 'hi do u rp')
                    elif a == 1:
                        bot.sendMessage(chat_id, 'y u block my fren')
            
    else:
        bot.sendMessage(chat_id, '<b>YOU HAVE NO POWER OVER ME</b>', parse_mode="html")

bot = telepot.Bot(loadToken())
allowedUsers = loadUsers()

MessageLoop(bot, handle).run_as_thread()
print 'I am listening ...'

while 1:
    time.sleep(10)
