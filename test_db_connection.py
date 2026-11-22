import psycopg
from getpass import getpass

try:
    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname="signalsentinel",
        user="postgres",
        password=getpass("Enter your PostgreSQL password: ")
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user;")
            result = cur.fetchone()

            print("\nConnection successful!")
            print("Database:", result[0])
            print("User:", result[1])

except Exception as error:
    print("\nConnection failed:", error)