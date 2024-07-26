import sqlite3

con = sqlite3.connect('database.db')
cur = con.cursor()
cur.execute('DELETE FROM Players WHERE tgid = 1')
cur.execute('COMMIT')
con.close()

print('Cleared db!')