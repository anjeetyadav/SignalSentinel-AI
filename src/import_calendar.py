import os
from pathlib import Path
from getpass import getpass

import psycopg
from psycopg import sql

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "calendar.csv"

if not CSV_PATH.exists():
    raise FileNotFoundError(f"Calendar CSV not found: {CSV_PATH}")

password = os.getenv("PGPASSWORD") or getpass(
    "PostgreSQL password for user postgres: "
)

print("Connecting to PostgreSQL...")

with psycopg.connect(
    host="localhost",
    port=5432,
    dbname="signalsentinel",
    user="postgres",
    password=password,
) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM public.calendar")
        existing_rows = cur.fetchone()[0]

        if existing_rows > 0:
            print(
                f"Import skipped: calendar already contains "
                f"{existing_rows:,} rows."
            )
        else:
            print("Importing calendar.csv...")

            with CSV_PATH.open(
                "r", encoding="utf-8-sig", newline=""
            ) as csv_file:
                header = csv_file.readline().strip()

                columns = [
                    column.strip().lower()
                    for column in header.split(",")
                ]

                copy_query = sql.SQL(
                    "COPY public.calendar ({}) FROM STDIN "
                    "WITH (FORMAT CSV, HEADER FALSE, NULL '')"
                ).format(
                    sql.SQL(", ").join(
                        sql.Identifier(column) for column in columns
                    )
                )

with cur.copy(copy_query) as copy:
    for line in csv_file:
        copy.write(line)

        print("Calendar data imported successfully.")

        cur.execute("SELECT COUNT(*) FROM public.calendar")
        final_count = cur.fetchone()[0]

        print(f"Rows now in calendar table: {final_count:,}")

print("Calendar import step finished.")