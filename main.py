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