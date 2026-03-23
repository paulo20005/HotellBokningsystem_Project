from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

# Skapa FastAPI-appen
app = FastAPI()

# CORS-inställningar så att frontend kan prata med API:et
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# Välkomstmeddelande för att testa att API:et är igång
@app.get("/")
def root():
    return {"message": "Välkommen till BlueNight Hotell - boka rum enkelt!"}


# Hämta alla rum från databasen
@app.get("/api/rooms")
def get_rooms():
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms")
    rum = cursor.fetchall()
    conn.close()

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


# Kolla om ett rum är ledigt mellan datum
def is_room_available(rum_id: int, incheckning: str, utcheckning: str):
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()
    
    # Kolla om det finns någon bokning som överlappar
    cursor.execute("""
        SELECT * FROM bookings 
        WHERE rum_id = ? 
        AND (
            (incheckning BETWEEN ? AND ?) OR 
            (utcheckning BETWEEN ? AND ?) OR
            (incheckning <= ? AND utcheckning >= ?)
        )
    """, (rum_id, incheckning, utcheckning, incheckning, utcheckning, incheckning, utcheckning))
    
    bokningar = cursor.fetchall()
    conn.close()
    
    return len(bokningar) == 0


# Kolla om rum är ledigt (endpoint för frontend)
@app.get("/api/rooms/{rum_id}/available")
def check_room_available(rum_id: int, incheckning: str, utcheckning: str):
    ledig = is_room_available(rum_id, incheckning, utcheckning)
    return {"ledig": ledig}


# Registrera ny användare
@app.post("/api/register")
def register(data: dict = Body(...)):
    namn = data.get("namn")
    email = data.get("email")
    losenord = data.get("losenord")
    
    if not namn or not email or not losenord:
        return {"error": "Alla fält (namn, email, losenord) måste fyllas i"}
    
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return {"error": "Email finns redan"}

    cursor.execute(
        "INSERT INTO users (namn, email, losenord) VALUES (?, ?, ?)",
        (namn, email, losenord)
    )
    conn.commit()
    conn.close()

    return {"message": f"Välkommen {namn}! Registrering klar."}


# Logga in användare
@app.post("/api/login")
def login(data: dict = Body(...)):
    email = data.get("email")
    losenord = data.get("losenord")
    
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, namn, email, roll FROM users WHERE email = ? AND losenord = ?",
        (email, losenord)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "message": f"Välkommen tillbaka {user[1]}!",
            "status": "ok",
            "user_id": user[0],
            "namn": user[1],
            "email": user[2],
            "roll": user[3]
        }
    else:
        return {"error": "Fel email eller lösenord"}


# Boka ett rum (med ledighetskontroll)
@app.post("/api/book")
def book(data: dict = Body(...)):
    rum_id = data.get("rum_id")
    anvandare_id = data.get("anvandare_id")
    incheckning = data.get("incheckning")
    utcheckning = data.get("utcheckning")
    
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()

    # Hämta information om rummet som bokas
    cursor.execute("SELECT * FROM rooms WHERE id = ?", (rum_id,))
    rum = cursor.fetchone()

    if not rum:
        conn.close()
        return {"error": "Rummet finns inte"}
    
    # Validera datum
    if incheckning >= utcheckning:
        conn.close()
        return {"error": "Utcheckning måste vara efter incheckning"}
    
    # Kolla om rummet är ledigt
    if not is_room_available(rum_id, incheckning, utcheckning):
        conn.close()
        return {"error": "Rummet är inte ledigt under dessa datum. Välj andra datum."}

    # Spara bokningen i databasen
    cursor.execute("""
        INSERT INTO bookings (rum_id, anvandare_id, incheckning, utcheckning)
        VALUES (?, ?, ?, ?)
    """, (rum_id, anvandare_id, incheckning, utcheckning))
    
    conn.commit()
    conn.close()

    return {
        "message": f"Tack! Du har bokat rum {rum[1]} mellan {incheckning} och {utcheckning}",
        "rum_nr": rum[1],
        "pris": rum[2],
        "incheckning": incheckning,
        "utcheckning": utcheckning
    }


# Hämta alla bokningar
@app.get("/api/bookings")
def get_bookings():
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bookings.id, users.namn, rooms.nummer, rooms.pris,
               bookings.incheckning, bookings.utcheckning
        FROM bookings 
        JOIN users ON bookings.anvandare_id = users.id
        JOIN rooms ON bookings.rum_id = rooms.id
        ORDER BY bookings.incheckning ASC
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


# Hämta bokningar för en specifik användare
@app.get("/api/users/{user_id}/bookings")
def get_user_bookings(user_id: int):
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bookings.id, users.namn, rooms.nummer, rooms.pris,
               bookings.incheckning, bookings.utcheckning
        FROM bookings 
        JOIN users ON bookings.anvandare_id = users.id
        JOIN rooms ON bookings.rum_id = rooms.id
        WHERE users.id = ?
        ORDER BY bookings.incheckning ASC
    """, (user_id,))
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


# Avboka en bokning
@app.delete("/api/bookings/{boknings_id}")
def avboka_bokning(boknings_id: int):
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookings WHERE id = ?", (boknings_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        return {"error": "Bokningen finns inte"}
    
    conn.commit()
    conn.close()

    return {"message": "Bokningen har avbokats"}