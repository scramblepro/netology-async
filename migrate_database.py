import sqlite3

def migrate_database():
    conn = sqlite3.connect("starwars.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY,
        name TEXT,
        birth_year TEXT,
        eye_color TEXT,
        films TEXT,
        gender TEXT,
        hair_color TEXT,
        height TEXT,
        homeworld TEXT,
        mass TEXT,
        skin_color TEXT,
        species TEXT,
        starships TEXT,
        vehicles TEXT
    )
    """)
    conn.commit()
    conn.close()
    print("Database migrated successfully.")

if __name__ == "__main__":
    migrate_database()
