import sqlite3

conn = sqlite3.connect('users_data.db')
cursor = conn.cursor()

# Check if the table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Favorites';")
result = cursor.fetchone()

if result:
    print("Favorites table exists.")
else:
    print("Favorites table does not exist.")

conn.close()
