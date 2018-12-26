import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.executescript(open('initdb.sql').read())
