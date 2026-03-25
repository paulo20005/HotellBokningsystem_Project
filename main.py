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

# Skapa en recension
@app.post("/api/reviews")
def create_review(data: dict = Body(...)):
    rum_id = data.get("rum_id")
    anvandare_id = data.get("anvandare_id")
    bokning_id = data.get("bokning_id")
    betyg = data.get("betyg")
    kommentar = data.get("kommentar")

    if betyg < 1 or betyg > 5:
        return {"error": "Betyg måste vara 1-5"}

    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()

    # Kolla att användaren faktiskt har gjort denna bokning
    cursor.execute("""
        SELECT * FROM bookings 
        WHERE id = ? AND anvandare_id = ? AND utcheckning < date('now')
    """, (bokning_id, anvandare_id))

    bokning = cursor.fetchone()
    if not bokning:
        conn.close()
        return {"error": "Du kan bara recensera rum du har bott i"}

    # Kolla om recension redan finns för denna bokning
    cursor.execute("SELECT * FROM reviews WHERE bokning_id = ?", (bokning_id,))
    if cursor.fetchone():
        conn.close()
        return {"error": "Du har redan recenserat detta rum"}

    # Spara recension
    cursor.execute("""
        INSERT INTO reviews (rum_id, anvandare_id, bokning_id, betyg, kommentar)
        VALUES (?, ?, ?, ?, ?)
    """, (rum_id, anvandare_id, bokning_id, betyg, kommentar))

    conn.commit()
    conn.close()

    return {"message": "Tack för din recension!"}

    # Hämta recensioner för ett rum
@app.get("/api/rooms/{rum_id}/reviews")
def get_reviews(rum_id: int):
    try:
        conn = sqlite3.connect('hotell.db')
        cursor = conn.cursor()

        # Först kolla om rummet finns
        cursor.execute("SELECT * FROM rooms WHERE id = ?", (rum_id,))
        rum = cursor.fetchone()
        if not rum:
            conn.close()
            return {"error": "Rummet finns inte"}

        # Hämta recensioner för rummet
        cursor.execute("""
            SELECT reviews.id, users.namn, reviews.betyg, reviews.kommentar, reviews.skapad
            FROM reviews 
            JOIN users ON reviews.anvandare_id = users.id
            WHERE reviews.rum_id = ?
            ORDER BY reviews.skapad DESC
        """, (rum_id,))

        recensioner = cursor.fetchall()
        conn.close()
        resultat = []
        for r in recensioner:
            resultat.append({
                "id": r[0],
                "anvandare": r[1],
                "betyg": r[2],
                "kommentar": r[3],
                "datum": r[4]
            })

        return {"rum_id": rum_id, "recensioner": resultat}

    except Exception as e:
        return {"error": str(e)}
# ========== ADMIN - CRUD FÖR RUM ==========

# Lägg till nytt rum
@app.post("/api/admin/rooms")
def create_room(data: dict = Body(...)):
    nummer = data.get("nummer")
    pris = data.get("pris")
    beskrivning = data.get("beskrivning")
    max_gaster = data.get("max_gaster", 2)
    
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO rooms (nummer, pris, beskrivning, max_gaster)
            VALUES (?, ?, ?, ?)
        """, (nummer, pris, beskrivning, max_gaster))
        conn.commit()
        return {"message": f"Rum {nummer} har lagts till"}
    except sqlite3.IntegrityError:
        return {"error": "Rumsnumret finns redan"}
    finally:
        conn.close()

# Uppdatera rum
@app.put("/api/admin/rooms/{rum_id}")
def update_room(rum_id: int, data: dict = Body(...)):
    pris = data.get("pris")
    beskrivning = data.get("beskrivning")
    max_gaster = data.get("max_gaster")
    
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM rooms WHERE id = ?", (rum_id,))
    if not cursor.fetchone():
        conn.close()
        return {"error": "Rummet finns inte"}
    
    cursor.execute("""
        UPDATE rooms 
        SET pris = COALESCE(?, pris),
            beskrivning = COALESCE(?, beskrivning),
            max_gaster = COALESCE(?, max_gaster)
        WHERE id = ?
    """, (pris, beskrivning, max_gaster, rum_id))
    
    conn.commit()
    conn.close()
    return {"message": f"Rum {rum_id} har uppdaterats"}

# Ta bort rum 
@app.delete("/api/admin/rooms/{rum_id}")
def delete_room(rum_id: int):
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM rooms WHERE id = ?", (rum_id,))
    if not cursor.fetchone():
        conn.close()
        return {"error": "Rummet finns inte"}
    
    cursor.execute("DELETE FROM rooms WHERE id = ?", (rum_id,))
    conn.commit()
    conn.close()
    return {"message": f"Rum {rum_id} har tagits bort"}

# Admin - se alla bokningar
@app.get("/api/admin/bookings")
def get_all_bookings():
    conn = sqlite3.connect('hotell.db')
    cursor = conn.cursor()
    #
    cursor.execute("""
        SELECT bookings.id, users.namn, rooms.nummer, rooms.pris,
               bookings.incheckning, bookings.utcheckning
        FROM bookings 
        JOIN users ON bookings.anvandare_id = users.id
        JOIN rooms ON bookings.rum_id = rooms.id
        ORDER BY bookings.incheckning DESC
    """)
    bokningar = cursor.fetchall()
    conn.close()
    # Skapa en lista med bokningar för att returnera som JSON
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
