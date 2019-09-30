* Set up
Create a new sqlite3 database with the name "calcBot.db"
Then create 2 tables: users and report

* users
CREATE TABLE users (ID INT, nick TEXT, msg TEXT, subToReports INT DEFAULT 0, admin INT DEFAULT 0);

In the database you should also make an entry for you own account that includes admin privileges so you can continue with adding users in the bot:
INSERT INTO users (ID, nick, msg, subToReports, admin) VALUES (<your TG ID>, "<nickname you want>", "<custom msg you want>", <if you want to be subbed to reports (0 or 1)>, 1);

* report
CREATE TABLE report (castle TEXT, battleResult INT, battleCloseness INT, gold INT, points INT, aliases TEXT);

Then create entries for all castles:
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Wolfpack", 0, 0, 0, 0, "None");
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Moonlight", 0, 0, 0, 0, "None");
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Potato", 0, 0, 0, 0, "None");
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Sharkteeth", 0, 0, 0, 0, "None");
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Dragonscale", 0, 0, 0, 0, "None");
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Highnest", 0, 0, 0, 0, "None");
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Deerhorn", 0, 0, 0, 0, "None");

* Misc
In the code at the end of the handle function there's some custom code for custom messages for special people - those custom messages don't work with the generic code, but you won't need them yourself.
