from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def root():
    return {"message": "Välkommen till BlueNight Hotell - boka rum enkelt!"}

@app.get("/api/rooms")
def get_rooms():
    # Koppla upp mot databasen
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()

    # Hämta alla rum
    cursor.execute("SELECT * FROM rooms")
    rum = cursor.fetchall()

    # Stäng anslutningen
    conn.close()

    # Konvertera till lista med dictionaries
    resultat = []
    for r in rum:
        resultat.append({
            "id": r[0],
            "nummer": r[1],
            "pris": r[2],
            "beskrivning": r[3],
            "max_gaster": r[4]
        })

    return resultat

# REGISTRERA NY ANVÄNDARE
@app.post("/api/register")
def register(email: str, losenord: str, namn: str):
    """Skapar en ny användare i databasen"""
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()

    # Kolla om användaren redan finns (unikt email)
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return {"error": "Email finns redan"}

    # Skapa ny användare (roll sätts automatiskt till 'gäst' via DEFAULT)
    cursor.execute(
        "INSERT INTO users (namn, email, losenord) VALUES (?, ?, ?)",
        (namn, email, losenord)
    )
    conn.commit()
    conn.close()

    return {"message": f"Välkommen {namn}! Registrering klar."}


# LOGGA IN
@app.post("/api/login")
def login(email: str, losenord: str):
    """Loggar in användare genom att kontrollera email och lösenord"""
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()

    # Hämta användare med matchande email och lösenord
    cursor.execute(
        "SELECT id, namn, email, roll FROM users WHERE email = ? AND losenord = ?",
        (email, losenord)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        # Inloggning lyckades
        return {
            "message": f"Välkommen tillbaka {user[1]}!",
            "status": "ok",
            "user_id": user[0],
            "namn": user[1],
            "email": user[2],
            "roll": user[3]
        }
    else:
        # Inloggning misslyckades
        return {"error": "Fel email eller lösenord"}


# BOKA RUM
@app.post("/api/book")
def book(rum_id: int, anvandare_id: int, incheckning: str, utcheckning: str):
    """Skapar en ny bokning för ett rum"""
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()

    # Hämta information om rummet som bokas
    cursor.execute("SELECT * FROM rooms WHERE id = ?", (rum_id,))
    rum = cursor.fetchone()

    if not rum:
        conn.close()
        return {"error": "Rummet finns inte"}

    # Spara bokningen i databasen
    cursor.execute("""
        INSERT INTO bookings (rum_id, anvandare_id, incheckning, utcheckning)
        VALUES (?, ?, ?, ?)
    """, (rum_id, anvandare_id, incheckning, utcheckning))
    
    conn.commit()
    conn.close()

    return {
        "message": f"Tack! Du har bokat rum {rum[1]}",
        "rum_nr": rum[1],
        "pris": rum[2]
    }


# HÄMTA ALLA BOKNINGAR
@app.get("/api/bookings")
def get_bookings():
    """Hämtar alla bokningar med information om gäst och rum"""
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()

    # Hämta bokningar med join mot users och rooms
    cursor.execute("""
        SELECT bookings.id, users.namn, rooms.nummer, rooms.pris,
               bookings.incheckning, bookings.utcheckning
        FROM bookings 
        JOIN users ON bookings.anvandare_id = users.id
        JOIN rooms ON bookings.rum_id = rooms.id
    """)
    bokningar = cursor.fetchall()
    conn.close()

    resultat = []
    for b in bokningar:
        resultat.append({
            "boknings_id": b[0],
            "gast": b[1],
            "rum_nr": b[2],
            "pris": b[3],
            "incheckning": b[4],
            "utcheckning": b[5]
        })

    return resultat
