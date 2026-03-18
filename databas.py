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



# Skapa tabell: bookings (bokningar)
cursor.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rum_id INTEGER NOT NULL,
    anvandare_id INTEGER NOT NULL,
    incheckning DATE NOT NULL,
    utcheckning DATE NOT NULL,
    status TEXT DEFAULT 'bokad',
    FOREIGN KEY (rum_id) REFERENCES rooms (id),
    FOREIGN KEY (anvandare_id) REFERENCES users (id)
)
''')
print(" Tabell 'bookings' skapade")

conn.close()