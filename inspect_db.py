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
    #get all the column names of the table
    cr.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'players'")
    #build dict of column names -> key = column_name, value = actual column name | ex : {"column_name : "goals}
    cols = [row['column_name'] for row in cr.fetchall()]
    print("Columns:", cols)
    conn.close()

if __name__ == "__main__":
    check()
