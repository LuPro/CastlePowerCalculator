import time
import random
import datetime
import telepot
import emojis
import copy
from telepot.loop import MessageLoop

import dbHandler
import castleReportParser

atkEmoji = u'\U00002694'
defEmoji = u'\U0001F6E1'
goldEmoji = u'\U0001F4B0'
variationSelector = u'\uFE0F'

def loadToken():
    tokenFile = open('token', 'r')
    token = tokenFile.read()
    tokenFile.close()
    return token.rstrip()

def editSettings(requestingID, command):
    if db.isAdmin(requestingID):
        parameter = command[1]

        if parameter == 'help':
            bot.sendMessage(requestingID, "adduser \nrmuser \nshowuser \nlistusers \naddcustom \nrmcustom \nsetsql \nloadsql")

        elif parameter == 'adduser':
            ID = int(command[2])
            nick = command[3]
            bot.sendMessage(requestingID, db.addUser(ID, nick))

        elif parameter == 'rmuser':
            ID = command[2]        #can be ID or nick
            bot.sendMessage(requestingID, db.rmUser(ID))

        elif parameter == 'showuser':
            ID = command[2]        #can be ID or nick
            bot.sendMessage(requestingID, db.showUser(ID), parse_mode="html")

        elif parameter == 'listusers':
            output = ''
            bot.sendMessage(requestingID, db.showUser(), parse_mode="html")

        elif parameter == 'addcustom':
            ID = command[2]        #can be ID or nick
            i = 3
            msg = ''
            while i < len(command):
                msg += command[i] + " "
                i += 1

            bot.sendMessage(requestingID, db.updateUserData(ID, ["msg"], [msg]), parse_mode = "html")

        elif parameter == 'rmcustom':
            ID = command[2]        #can be ID or nick
            bot.sendMessage(requestingID, db.updateUserData(ID, ["msg"], ["None"]), parse_mode = "html")

        elif parameter == 'setsql':
            ID = command[2]
            param = command[3]
            value = command[4]
            db.updateUserData(ID, [param], [value])
            bot.sendMessage(requestingID, "Updated database values!")
        
        elif parameter == 'loadsql':
            ID = command[2]
            param = command[3]
            bot.sendMessage(requestingID, db.loadUserData(ID, [param]))

    else:
        bot.sendMessage(requestingID, "I'm sorry Dave, I'm afraid I can't do that.")

def isCastle(string):
    castles = db.loadList("castle", "report")

    string = string.lower()
    for castle in castles:
        if castle.lower() == string:
            return castle;
        else:
            aliases = db.loadCastleData(castle, "aliases")[0].lower()
            aliases = aliases.split()
            for alias in aliases:
                if alias == string:
                    return castle

    return ""

def sortPoints(val):
    return val[1]

def generateCastleReport():
    castles = db.loadList("castle", "report")
    
    scoreText = emojis.encode(":trophy:") + "<b>Scores</b>\nNormal:\n"
    adjustedText = "\nAdjusted:\n"
    scores = []
    adjustedScores = []
    for castle in castles:
        points = db.loadCastleData(castle, "points")[0]
        castleTuple = (castle, points)
        scores.append(castleTuple)

        if db.loadCastleData(castle, "battleResult")[0] == 1:
            castleTuple = (castle, points * 5)
            adjustedScores.append(copy.deepcopy(castleTuple))
        else:
            castleTuple = (castle, points)
            adjustedScores.append(copy.deepcopy(castleTuple))
        
    scores.sort(key = sortPoints, reverse = True)
    for score in scores:
        scoreText += emojis.encode(":" + str(db.loadCastleData(score[0], "emoji")[0]) + ":") + ": +" + str(score[1]) + "\n"

    adjustedScores.sort(key = sortPoints, reverse = True)
    for score in adjustedScores:
        if db.loadCastleData(score[0], "battleResult")[0] == 1:
            adjustedText += emojis.encode(":" + str(db.loadCastleData(score[0], "emoji")[0]) + ":") + ": +" + str(score[1]) + "-" + str(score[1] + 4) + "\n"
        else:
            adjustedText += emojis.encode(":" + str(db.loadCastleData(score[0], "emoji")[0]) + ":") + ": +" + str(score[1]) + "\n"
    
    return scoreText + adjustedText

def pushCastleReport():
    users = db.loadList("ID", "users")
    subbedUsers = []
    for user in users:
        if db.loadUserData(user, ["subToReports"])[0][0] == 1:
            subbedUsers.append(user)

    castleReport = generateCastleReport()
    for subbedUser in subbedUsers:
        bot.sendMessage(subbedUser, castleReport, parse_mode="html")

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

    #print text.encode('unicode-escape').decode('ascii')

    statBeginPos = text.find(searchString)
    statEndPos = 0
    paranthesesPos = text.find('(', statBeginPos)
    whitespacePos = text.find(' ', statBeginPos)
    newLinePos = text.find('\n', statBeginPos)

    if newLinePos < whitespacePos and newLinePos != -1:
        whitespacePos = newLinePos

    if paranthesesPos < whitespacePos and paranthesesPos != - 1:
        statEndPos = paranthesesPos
    else:
        statEndPos = whitespacePos

    if paranthesesPos == -1 and whitespacePos == -1 and newLinePos == -1:
        bot.sendMessage(chat_id, "Error: Punctuation/Spaces are missing, can't discern values from text")
        return

    if statBeginPos != -1:
        stat = text[statBeginPos + len(searchString) : statEndPos]
        stat = int(stat)
    else:
        bot.sendMessage(chat_id, "Error: Couldn't find any stats!")
        #further error handling so the bot doesn't crash later when trying to calc
        return

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

    db.open("calcBot.db")

    if castleParser.validate(msg, db):
        bot.sendMessage(chat_id, castleParser.parseReport(msg, db))
        pushCastleReport()

    nick = db.loadUserData(chat_id, ["nick"])
    try:
        username = msg['chat']['username']
    except KeyError:
        username = "Group"
    print ('Received command from %d (%s / @%s): %s' % (chat_id, nick[0][0], username, command)).encode('unicode-escape').decode('ascii')

    if (db.findUser(chat_id).empty):
        pass
        #bot.sendMessage(chat_id, '<b>YOU HAVE NO POWER OVER ME</b>', parse_mode="html")
    else:
        lowerCmd = command.lower()   #this makes it impossible to enter capitalized nicks and capitalization into custom messages, fix this later
        if (lowerCmd == '/start'):
            bot.sendMessage(chat_id, 'Type /help to find out more')

        elif (lowerCmd[0:5] == '/help'):
            bot.sendMessage(chat_id, 'To calculate send /calc <CastleGold> <RelevantStat> <Gold>')

        elif lowerCmd[0:9] == '/settings':
            editSettings(chat_id, command.split())

        elif lowerCmd[0:4] == '/sub':
            if db.loadUserData(chat_id, ["subToReports"])[0][0] == 0:
                db.updateUserData(chat_id, ["subToReports"], [1])
                bot.sendMessage(chat_id, "Successfully subscribed to castle point reports")
            else:
                bot.sendMessage(chat_id, "You are already subscribed to castle point reports")

        elif lowerCmd[0:6] == '/unsub':
            if db.loadUserData(chat_id, ["subToReports"])[0][0] == 1:
                db.updateUserData(chat_id, ["subToReports"], [0])
                bot.sendMessage(chat_id, "Successfully unsubscribed from castle point reports")
            else:
                bot.sendMessage(chat_id, "You are not subscribed to castle point reports")

        elif lowerCmd[0:7] == '/report':
            bot.sendMessage(chat_id, generateCastleReport(), parse_mode="html")

        elif (lowerCmd[0:5] == '/calc'):
            parameters = command.split()
            castleGold = 0

            try: 
                if (lowerCmd[5:9] == '_atk' and msg['reply_to_message']['message_id']):
                    if len(parameters) < 2:
                        bot.sendMessage(chat_id, "Error: Too few parameters, needed are <CastleGold> or <CastleName>")
                    
                    try:
                        castleGold = int(parameters[1])
                    except:
                        if isinstance(parameters[1], basestring):
                            castleName = isCastle(parameters[1])
                            if castleName != "":
                                if db.loadCastleData(castleName, "battleResult")[0] == 0:
                                    bot.sendMessage(chat_id, "This castle didn't get breached last battle, you cannot calculate attack power to it!")
                                    return
                                castleGold = int(db.loadCastleData(castleName, "gold")[0])
                            else:
                                bot.sendMessage(chat_id, "Error: Value for castle gold is wrong, only enter numbers or valid aliases for castle names")
                                return

                    parseReport(msg['reply_to_message']['text'], 'atk', castleGold, chat_id)
                    if db.loadUserData(chat_id, ["msg"])[0][0] != "":
                        bot.sendMessage(chat_id, db.loadUserData(chat_id, ["msg"])[0][0])
                    return

                elif (lowerCmd[5:9] == '_def' and msg['reply_to_message']['message_id']):
                    if len(parameters) < 2:
                        bot.sendMessage(chat_id, "Error: Too few parameters, needed are <CastleGold> or <CastleName>")

                    try:
                        castleGold = int(parameters[1])
                    except:
                        if isinstance(parameters[1], basestring):
                            castleName = isCastle(parameters[1])
                            if castleName != "":
                                if db.loadCastleData(castleName, "battleResult")[0] == 1:
                                    bot.sendMessage(chat_id, "This castle got breached last battle, you cannot calculate defense power of it!")
                                    return
                                castleGold = int(db.loadCastleData(castleName, "gold")[0])
                            else:
                                bot.sendMessage(chat_id, "Error: Value for castle gold is wrong, only enter numbers or valid aliases for castle names")
                                return

                    parseReport(msg['reply_to_message']['text'], 'def', castleGold, chat_id)
                    if db.loadUserData(chat_id, ["msg"])[0][0] != "":
                        bot.sendMessage(chat_id, db.loadUserData(chat_id, ["msg"])[0][0])
                    return
                
            except KeyError:
                bot.sendMessage(chat_id, "Error: You have to reply to a report for me to parse")
                return
                
            if len(parameters) < 4:
                bot.sendMessage(chat_id, "Error: Too few parameters, needed are <CastleGold> <RelevantStat> <Gold>")
                return

            else:
                if len(parameters) > 4:
                    bot.sendMessage(chat_id, "Warning: Too many parameters defined, ignoring excess values")

                try:
                    bot.sendMessage(chat_id, calculate(parameters), parse_mode="html")

                except ValueError:
                    bot.sendMessage(chat_id, "Error: Entered incorrect values (Did you enter text instead of numbers?)")
                    return

            if db.loadUserData(chat_id, ["msg"])[0][0] != "":
                bot.sendMessage(chat_id, db.loadUserData(chat_id, ["msg"])[0][0])

            if chat_id == 280993442:    #rinka
                bot.sendMessage(chat_id, (u'\u0414\u043E\u0431\u0440\u044B\u0439 \u0434\u0435\u043D\u044C'.encode('utf-8') + ', Cat Queen! May your castle be strong and your Pina Colada tasty!'))
            elif chat_id == 26667968:    #arctic
                a = random.randint(0,1)
                if a == 0:
                    bot.sendMessage(chat_id, 'hi do u rp')
                elif a == 1:
                    bot.sendMessage(chat_id, 'y u block my fren')
    db.close()


bot = telepot.Bot(loadToken())
db = dbHandler.DataBaseHandler()
castleParser = castleReportParser.CastleReportParser()

MessageLoop(bot, handle).run_as_thread()
print 'I am listening ...'

while 1:
    time.sleep(10)
