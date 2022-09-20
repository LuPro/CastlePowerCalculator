trophyEmoji = u'\U0001F3C6'

class CastleReportParser:
    def parseReport(self, msg, db):
        text = msg["text"]
        returnErrors = ""

        castles = db.loadList("castle", "report")

        castleEndPos = 0
        castleGoldPos = 0
        for castle in castles:
            result = 0      #0 for defended, 1 for breached
            closeness = 0   #currently not parsed
            gold = 0
            points = 0

            castlePos = text.find(castle, castleEndPos)

            if castlePos != -1:
                castleGoldPos = text.find("gold", castlePos)

                attPillagedStr = "Attackers have pillaged the castle for"
                attPillagedPos = text.find(attPillagedStr, castlePos, castleGoldPos)
                attLostStr = "Attackers have lost"
                attLostPos = text.find(attLostStr, castlePos, castleGoldPos)
                defBoredStr = "were bored - no one has attacked them."
                defBoredPos = text.find(defBoredStr, castlePos, castleGoldPos)
                if defBoredPos != -1:
                    result = 0
                    gold = 0
                    castleGoldPos = defBoredPos + len(defBoredStr)  #isn't gold pos but is end of this castle's section
                elif attPillagedPos != -1 and attLostPos == -1:
                    result = 1
                    attPillagedPos += len(attPillagedStr)
                    gold = int(text[attPillagedPos + 1 : castleGoldPos - 1])
                elif attPillagedPos == -1 and attLostPos != -1:
                    result = 0
                    attLostPos += len(attLostStr)
                    gold = int(text[attLostPos + 1 : castleGoldPos - 1]) 
                else:
                    result = 0
                    returnErrors += "\nError in parsing report, couldn't find out result of castle %s" % (castle)


            scoresPos = text.find("Scores:")
            if scoresPos != -1:
                castleScorePos = text.find((castle + " Castle"), scoresPos)
                castleScorePos += len((castle + " Castle"))
                
                trophyEndPos = text.find(trophyEmoji, castleScorePos)

                if trophyEndPos != -1:
                    points = int(text[castleScorePos + 2 : trophyEndPos - 1])
                else:
                    returnErrors += "\nError while searching for trophy emoji to parse castle points for castle %s" % (castle)

            db.updateCastleData(castle, result, closeness, gold, points)
            castleEndPos = castleGoldPos
            
        db.updateReportTimeStamp(msg["forward_date"])
        return "Thank you for sending in the report" + returnErrors

    def validate(self, msg, db):
        #checks if message is forwarded from cwreports channel and if it is actually a battle report and not guild report
        if "Battle reports:" in msg["text"] and "forward_from_chat" in msg and msg["forward_from_chat"]["id"] == db.loadMetaData("cwReportID"):
            #checks if the report that was sent is newer than the report already stored
            if db.loadMetaData("dateReport") < msg["forward_date"]:
                return "valid"
            else:
                return "old"

        return "invalid"
