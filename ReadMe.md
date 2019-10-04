# Set up

### token file

The bot needs a file called <code>token</code> containing *just* the bot token as shown in Botfather in the working directory

### Database

Create a new sqlite3 database with the name "calcBot.db"
Then create 3 tables: users, report and metadata

* users

<code>CREATE TABLE users (ID INT, nick TEXT, msg TEXT, subToReports INT DEFAULT 0, admin INT DEFAULT 0);</code>

In the database you should also make an entry for you own account that includes admin privileges so you can continue with adding users in the bot:

<code>INSERT INTO users (ID, nick, msg, subToReports, admin) VALUES ($your_TG_ID, "$nickname_you_want", "$custom_msg_you_want", $if_you_want_to_be_subbed_to_reports (0 or 1), 1);</code>

* report

<code>CREATE TABLE report (castle TEXT, battleResult INT, battleCloseness INT, gold INT, points INT, aliases TEXT, emoji TEXT);</code>

Then create entries for all castles (in the order they are in the cwreports channel report):

```INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases, emoji) VALUES ("Highnest", 0, 0, 0, 0, "None", eagle);
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Wolfpack", 0, 0, 0, 0, "None", wolf);
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Deerhorn", 0, 0, 0, 0, "None", deer);
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Sharkteeth", 0, 0, 0, 0, "None", shark);
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Dragonscale", 0, 0, 0, 0, "None", dragon);
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Moonlight", 0, 0, 0, 0, "None", new_moon);
INSERT INTO report (castle, battleResult, battleCloseness, gold, points, aliases) VALUES ("Potato", 0, 0, 0, 0, "None", potato);
```

* metadata 

<code>CREATE TABLE metadata (dateReport INT, cwReportID INT);</code>

Then enter the data, first should be set to 0 (unix time stamp), the second is the ID of the cw reports channel (can be adjusted to grab from other channels/cw3 channel) - parser is not guaranteed to work with other channels though (it will most likely not work)

<code>INSERT INTO metadata (dateReport, cwReportID) VALUES (0, -1001108112459);</code>

# Misc

In the code at the end of the handle function there's some custom code for custom messages for special people - those custom messages don't work with the generic code, but you won't need them yourself so you can just delete them.
