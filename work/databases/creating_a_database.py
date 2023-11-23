import sqlite3

conn = sqlite3.connect('movies.db')
cur = conn.cursor()

sql = """
    CREATE TABLE MOVIES (
        MovieID TEXT,
        Title TEXT,
        Description TEXT,
        Actors TEXT,
        Directors TEXT,
        yearReleased INTEGER,
        Duration INTEGER,
        Genre TEXT,
        Image TEXT,
        topRate INTEGER,
        Classic INTEGER,
        newMovie INTEGER,
        PRIMARY KEY(MovieID)
    )"""

cur.execute(sql)
print("movie table has been created")

conn.commit()
conn.close()

