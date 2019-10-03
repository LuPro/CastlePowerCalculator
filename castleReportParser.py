trophyEmoji = u'\U0001F3C6'

class CastleReportParser:
    def parseReport(self, msg, db):
        text = msg["text"]

        castles = db.loadCastles()

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

                attPillagedPos = text.find("Attackers have pillaged the castle for", castlePos, castleGoldPos)
                attLostPos = text.find("Attackers have lost", castlePos, castleGoldPos)
                if attPillagedPos != -1 and attLostPos == -1:
                    result = 1
                    attPillagedPos += len("Attackers have pillaged the castle for")
                    gold = int(text[attPillagedPos + 1 : castleGoldPos - 1])
                elif attPillagedPos == -1 and attLostPos != -1:
                    result = 0
                    attLostPos += len("Attackers have lost")
                    gold = int(text[attLostPos + 1 : castleGoldPos - 1])
                else:
                    return "Error in parsing report, couldn't find out result of castle %s" % (castle)

            scoresPos = text.find("Scores:")
            if scoresPos != -1:
                castleScorePos = text.find((castle + " Castle"), scoresPos)
                castleScorePos += len((castle + " Castle"))
                
                trophyEndPos = text.find(trophyEmoji, castleScorePos)

                if trophyEndPos != -1:
                    points = int(text[castleScorePos + 2 : trophyEndPos - 1])
                else:
                    return "Error while searching for trophy emoji to parse castle points for castle %s" % (castle)

            db.updateCastleData(castle, result, closeness, gold, points)
            castleEndPos = castleGoldPos
            
        db.updateReportTimeStamp(msg["forward_date"])
        return "Thank you for sending in the report"

    def validate(self, msg, db):
        #checks if message is forwarded from cwreports channel and if it is actually a battle report and not guild report
        if "Battle reports:" in msg["text"] and msg["forward_from_chat"]["id"] == db.loadMetaData("cwReportID"):
            #checks if the report that was sent is newer than the report already stored
            if db.loadMetaData("dateReport") <= msg["forward_date"]:   #remove the = in <= after testing
                return True

        return False