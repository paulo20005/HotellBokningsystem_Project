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


# Skapa tabell reviews 
# det kommer att finnas en relation mellan reviews och både rooms, users och bookings.
cursor.execute('''
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rum_id INTEGER NOT NULL,
    anvandare_id INTEGER NOT NULL,
    bokning_id INTEGER NOT NULL,
    betyg INTEGER NOT NULL CHECK (betyg >= 1 AND betyg <= 5), 
    kommentar TEXT,
    skapad TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rum_id) REFERENCES rooms (id),
    FOREIGN KEY (anvandare_id) REFERENCES users (id),
    FOREIGN KEY (bokning_id) REFERENCES bookings (id)
)
''')
print(" Tabell 'reviews' skapad!")
conn.close()