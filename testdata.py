import sqlite3

conn = sqlite3.connect('hotell.db')
cursor = conn.cursor()

# Kolla om det redan finns rum
cursor.execute("SELECT COUNT(*) FROM rooms")
antal_rum = cursor.fetchone()[0]

if antal_rum == 0:
    # Lägg till 5 rum
    rum = [
        (101, 1200, "Enkelrum med havsutsikt", 2),
        (102, 800, "Enkelrum, liten men mysig", 1),
        (103, 1500, "Dubbelrum med balkong", 2),
        (104, 2000, "Familjerum, 4 bäddar", 4),
        (105, 2500, "Suite med jacuzzi", 2)
    ]
    
    cursor.executemany('''
    INSERT INTO rooms (nummer, pris, beskrivning, max_gaster)
    VALUES (?, ?, ?, ?)
    ''', rum)
    print("5 rum inlagda")
else:
    print("Rum finns redan, hoppar över")

# Kolla om det redan finns användare
cursor.execute("SELECT COUNT(*) FROM users")
antal_users = cursor.fetchone()[0]

if antal_users == 0:
    # Lägg till hela teamet + admin + gäst
    anvandare = [
        ("Paulo", "paulo@hotell.se", "paulo123", "personal"),
        ("Kristian", "kristian@hotell.se", "kristian123", "personal"),
        ("Patrick", "patrick@hotell.se", "patrick123", "personal"),
        ("Yousef", "yousef@hotell.se", "yousef123", "personal"),
        ("Kalle Anka", "kalle@email.com", "123", "gäst"),
        ("Admin", "admin@hotell.se", "admin123", "personal")
    ]
    
    cursor.executemany('''
    INSERT INTO users (namn, email, losenord, roll)
    VALUES (?, ?, ?, ?)
    ''', anvandare)
    print("6 användare inlagda")
else:
    print("Användare finns redan, hoppar över")

conn.commit()
conn.close()
print("Testdata klar")