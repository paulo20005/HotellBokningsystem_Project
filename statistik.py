import sqlite3
import pandas as pd

# Anslut till databasen
conn = sqlite3.connect('hotell.db')

# Hämta bokningar med användare och rum
query = """
    SELECT users.namn, rooms.nummer, bookings.incheckning, bookings.utcheckning
    FROM bookings
    JOIN users ON bookings.anvandare_id = users.id
    JOIN rooms ON bookings.rum_id = rooms.id
"""
df = pd.read_sql_query(query, conn)
conn.close()

# Visa alla bokningar
print("Alla bokningar")
print(df)
print()

# Antal bokningar per rum
print("Antal bokningar per rum")
print(df.groupby('nummer').size())
print()

# Mest bokade rum
print("Mest bokade rum")
print(df['nummer'].value_counts().head(3))
print()

# Antal unika gäster
print(f"Totalt antal gäster som bokat: {df['namn'].nunique()}")
print()

# Totalt antal bokningar
print(f"Totalt antal bokningar: {len(df)}")