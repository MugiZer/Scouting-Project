import psycopg2
from psycopg2.extras import RealDictCursor

def check():
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="hamza158",
        dbname="mountakhab",
        port="5432"
    )
    cr = conn.cursor(cursor_factory=RealDictCursor)
    cr.execute("SELECT name, league_name FROM players WHERE name = 'Achraf Hakimi'")
    rows = cr.fetchall()
    for row in rows:
        print(f"{row['name']} - {row['league_name']}")
    conn.close()

if __name__ == "__main__":
    check()
