import sqlite3

conn = sqlite3.connect('users_data.db')
cursor = conn.cursor()

try:
    cursor.execute('''
        CREATE TABLE Reviews (
            ReviewID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID TEXT,
            MovieID INTEGER,
            ReviewText TEXT,  -- Add this line for the ReviewText column
            FOREIGN KEY (UserID) REFERENCES Users(UserID),
            FOREIGN KEY (MovieID) REFERENCES Movies(MovieID)
        );
    ''')
    print("Reviews table created successfully")
except sqlite3.Error as e:
    print("Error creating Reviews table:", e)

conn.commit()
conn.close()
