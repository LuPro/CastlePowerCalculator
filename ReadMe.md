* Set up
Create a new sqlite3 database with the name "calcBot.db"
Then create 3 tables: users, report and metadata

* users
CREATE TABLE users (ID INT, nick TEXT, msg TEXT, subToReports INT DEFAULT 0, admin INT DEFAULT 0);

In the database you should also make an entry for you own account that includes admin privileges so you can continue with adding users in the bot:
INSERT INTO users (ID, nick, msg, subToReports, admin) VALUES (<your TG ID>, "<nickname you want>", "<custom msg you want>", <if you want to be subbed to reports (0 or 1)>, 1);

* report
CREATE TABLE report (castle TEXT, battleResult INT, battleCloseness INT, gold INT, points INT, aliases TEXT);

Then create entries for all castles (in the order they are in the cwreports channel report):
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Highnest", 0, 0, 0, 0, "None");
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Wolfpack", 0, 0, 0, 0, "None");
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Deerhorn", 0, 0, 0, 0, "None");
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Sharkteeth", 0, 0, 0, 0, "None");
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Dragonscale", 0, 0, 0, 0, "None");
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Moonlight", 0, 0, 0, 0, "None");
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Potato", 0, 0, 0, 0, "None");

* metadata 
CREATE TABLE metadata (dateReport INT, cwReportID INT);

Then enter the data, first should be set to 0 (unix time stamp), the second is the ID of the cw reports channel (can be adjusted to grab from other channels/cw3 channel) - parser is not guaranteed to work with other channels though (it will most likely not work)
INSERT INTO metadata (dateReport, cwReportID) VALUES (0, -1001108112459);

* Misc
In the code at the end of the handle function there's some custom code for custom messages for special people - those custom messages don't work with the generic code, but you won't need them yourself so you can just delete them.
