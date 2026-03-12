import sqlite3

# Skapa anslutning
conn = sqlite3.connect('hotell.db')
cursor = conn.cursor()

# Skapa tabell: users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    namn TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    losenord TEXT NOT NULL,
    roll TEXT DEFAULT 'gäst'
)
''')

# Skapa tabell: rooms
cursor.execute('''
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nummer INTEGER UNIQUE NOT NULL,
    pris INTEGER NOT NULL,
    beskrivning TEXT,
    max_gaster INTEGER DEFAULT 2
)
''')

print("Databas och tabeller skapade!")

conn.close()