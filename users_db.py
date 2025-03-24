import sqlite3

local_db = "users_db.db"
connection = sqlite3.connect(local_db)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE users_table
(user_name TEXT PRIMARY KEY,
firstname TEXT,
surname TEXT,
password TEXT
)
""")

connection.commit()
connection.close()
