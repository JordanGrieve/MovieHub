import sqlite3
import csv

connection = sqlite3.connect("movies.db")
cursor = connection.cursor()

with open('values.csv', 'r') as file:
    no_records = 0
    for row in file:
        row_data = [item.strip() for item in row.split(",")]  # Strip leading/trailing spaces
        placeholders = ",".join(["?" for _ in row_data])  # Create placeholders based on the number of values
        query = f"INSERT OR IGNORE INTO Movies VALUES ({placeholders})"
        
        print("Query:", query)
        print("Row Data:", row_data)
        
        try:
            cursor.execute(query, row_data)
            connection.commit()
            no_records += 1
        except sqlite3.Error as e:
            print(f"Error inserting row: {e}")

connection.close()
print('\n{} Record Transferred'.format(no_records))


