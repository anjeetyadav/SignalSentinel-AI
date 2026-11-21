from pathlib import Path
from getpass import getpass
from io import StringIO
import shutil
import math

import pandas as pd
import psycopg


# ==================================================
# CONFIGURATION
# ==================================================

ROOT = Path(__file__).resolve().parent.parent
SALES_FILE = ROOT / "data" / "raw" / "sales_train_validation.csv"

DB_NAME = "signalsentinel"
DB_USER = "postgres"

CHUNK_SIZE = 100
EXPECTED_SERIES = 30_490
EXPECTED_DAYS = 1_913
EXPECTED_RECORDS = EXPECTED_SERIES * EXPECTED_DAYS
EXPECTED_BATCHES = math.ceil(EXPECTED_SERIES / CHUNK_SIZE)

MIN_FREE_GB = 15

ID_COLUMNS = [
    "id", "item_id", "dept_id",
    "cat_id", "store_id", "state_id"
]

COPY_SQL = """
COPY public.sales (
    id, item_id, dept_id, cat_id,
    store_id, state_id, d, units_sold
)
FROM STDIN WITH (FORMAT CSV)
"""


# ==================================================
# SAFETY
# ==================================================

def check_disk_space():
    free_gb = shutil.disk_usage(ROOT).free / (1024 ** 3)
    print(f"Free disk space: {free_gb:.2f} GB")

    if free_gb < MIN_FREE_GB:
        raise RuntimeError(
            "Disk space is below the 15 GB safety threshold. "
            "Import stopped."
        )


def validate_checkpoints(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(series_count), 0),
                COALESCE(SUM(records_count), 0),
                COALESCE(MIN(batch_number), 0),
                COALESCE(MAX(batch_number), 0)
            FROM public.sales_import_batches
        """)
        count, series, records, minimum, maximum = cur.fetchone()

        cur.execute("SELECT COUNT(*) FROM public.sales")
        sales_rows = cur.fetchone()[0]

        cur.execute("""
            SELECT batch_number, series_count, records_count
            FROM public.sales_import_batches
            ORDER BY batch_number
        """)
        batches = cur.fetchall()

    if count > EXPECTED_BATCHES:
        raise RuntimeError("Unexpected number of checkpoints.")

    if sales_rows != records:
        raise RuntimeError(
            "Sales row count does not match checkpoints. "
            "Import stopped to protect the existing data."
        )

    if [b[0] for b in batches] != list(range(1, count + 1)):
        raise RuntimeError(
            "Checkpoints are not consecutive. Import stopped."
        )

    for batch_number, series_count, records_count in batches:
        first_series = (batch_number - 1) * CHUNK_SIZE
        expected_series = min(
            CHUNK_SIZE,
            EXPECTED_SERIES - first_series
        )

        if series_count != expected_series:
            raise RuntimeError(
                f"Unexpected series count in batch {batch_number}."
            )

        if records_count != series_count * EXPECTED_DAYS:
            raise RuntimeError(
                f"Unexpected record count in batch {batch_number}."
            )

    print(f"Verified checkpoints: {count}")
    print(f"Existing sales rows: {sales_rows:,}")

    return count


# ==================================================
# IMPORT
# ==================================================

def main():
    print("=" * 60)
    print("SignalSentinel AI - Full Sales Import")
    print("=" * 60)

    if not SALES_FILE.exists():
        raise FileNotFoundError(f"Missing dataset: {SALES_FILE}")

    header = pd.read_csv(SALES_FILE, nrows=0).columns.tolist()
    day_columns = [c for c in header if c.startswith("d_")]

    if len(day_columns) != EXPECTED_DAYS:
        raise ValueError(
            f"Expected {EXPECTED_DAYS} daily columns; "
            f"found {len(day_columns)}."
        )

    if header != ID_COLUMNS + day_columns:
        raise ValueError("Unexpected dataset structure.")

    check_disk_space()
    password = getpass("Enter your PostgreSQL password: ")

    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname=DB_NAME,
        user=DB_USER,
        password=password,
        autocommit=True,
    ) as conn:

        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS public.sales_import_batches (
                    batch_number INTEGER PRIMARY KEY,
                    series_count INTEGER NOT NULL,
                    records_count INTEGER NOT NULL,
                    completed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)

        completed = validate_checkpoints(conn)
        imported_this_run = 0

        for batch_number, chunk in enumerate(
            pd.read_csv(SALES_FILE, chunksize=CHUNK_SIZE),
            start=1,
        ):
            if batch_number <= completed:
                continue

            check_disk_space()

            if chunk[ID_COLUMNS].isna().any().any():
                raise ValueError(
                    f"Missing identifier in batch {batch_number}."
                )

            if chunk[day_columns].isna().any().any():
                raise ValueError(
                    f"Missing sales values in batch {batch_number}."
                )

            if (chunk[day_columns] < 0).any().any():
                raise ValueError(
                    f"Negative sales values in batch {batch_number}."
                )

            long_data = chunk.melt(
                id_vars=ID_COLUMNS,
                value_vars=day_columns,
                var_name="d",
                value_name="units_sold",
            )

            long_data["units_sold"] = (
                long_data["units_sold"].astype("int32")
            )

            series_count = len(chunk)
            records_count = len(long_data)

            if records_count != series_count * EXPECTED_DAYS:
                raise RuntimeError(
                    f"Unexpected record count in batch {batch_number}."
                )

            buffer = StringIO()
            long_data.to_csv(
                buffer,
                index=False,
                header=False,
            )

            # Sales records and checkpoint are committed together.
            with conn.transaction():
                with conn.cursor() as cur:
                    with cur.copy(COPY_SQL) as copy:
                        copy.write(buffer.getvalue())

                    cur.execute("""
                        INSERT INTO public.sales_import_batches (
                            batch_number, series_count, records_count
                        )
                        VALUES (%s, %s, %s)
                    """, (
                        batch_number,
                        series_count,
                        records_count,
                    ))

            completed = batch_number
            imported_this_run += 1

            print(
                f"Batch {batch_number}/{EXPECTED_BATCHES} committed | "
                f"Series: {series_count} | "
                f"Records: {records_count:,}"
            )

            del long_data, buffer, chunk

            if imported_this_run % 10 == 0:
                check_disk_space()
                print(
                    f"Progress: {completed}/{EXPECTED_BATCHES} batches"
                )

        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(*),
                    COUNT(DISTINCT id),
                    COUNT(DISTINCT d)
                FROM public.sales
            """)
            actual_rows, actual_series, actual_days = cur.fetchone()

        print("\nImport summary")
        print(f"Sales rows: {actual_rows:,}")
        print(f"Unique series: {actual_series:,}")
        print(f"Unique days: {actual_days:,}")

        if (
            actual_rows != EXPECTED_RECORDS
            or actual_series != EXPECTED_SERIES
            or actual_days != EXPECTED_DAYS
        ):
            raise RuntimeError(
                "Final totals do not match expectations. "
                "Review the database before proceeding."
            )

        print("\nFULL IMPORT COMPLETED AND VERIFIED.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nIMPORT STOPPED: {exc}")
        raise