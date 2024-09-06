import sqlite3

con = sqlite3.connect('database.db')
cur = con.cursor()

cur.execute('CREATE TABLE Players (ID PRIMARY KEY INT, tgid INT, username TEXT, firstname TEXT, lastname TEXT, clicks INT, Banned TEXT, query_id TEXT, awaiting_query INT, time INT, ref TEXT, is_reffed INT)')
cur.execute('CREATE TABLE Params (ID PRIMARY KEY INT, Key TEXT, Value TEXT)')
cur.execute('COMMIT')
con.close()
