#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV Data Loader for SharedData Database
========================================
Prerequisites:
1. Run create_schema.sql first to create the database and tables
2. Ensure CSV files exist in ./data/ folder
3. Update connection settings below if needed

This script loads all CSV files into the database in the correct order.
"""

import csv
from pathlib import Path
import pyodbc

# =============================================
# Configuration
# =============================================
DB_NAME = "SharedData"
DRIVER = "ODBC Driver 17 for SQL Server"
SERVER = r"(localdb)\Library"

ROOT = Path(".").resolve()
DATA = ROOT / "data"

# Table loading order (respects foreign key dependencies)
TABLE_FILES = {
    "Author": DATA / "Author.csv",
    "Genre": DATA / "Genre.csv",
    "BookCopyCondition": DATA / "BookCopyCondition.csv",
    "Book": DATA / "Book.csv",
    "BookCopy": DATA / "BookCopy.csv",
    "Customer": DATA / "Customer.csv",
    "LibraryCard": DATA / "LibraryCard.csv",
    "Checkout": DATA / "Checkout.csv",
}

# =============================================
# Helper Functions
# =============================================

def q(name: str) -> str:
    """Quote identifier for SQL Server."""
    return "[" + name.replace("]", "]]") + "]"

def connect(db: str = DB_NAME):
    """Connect to SQL Server database."""
    return pyodbc.connect(
        f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={db};Trusted_Connection=Yes;",
        autocommit=True
    )

def load_csv_into_table(table: str, csv_path: Path) -> None:
    """Load CSV file into database table."""
    with connect(DB_NAME) as cx:
        cur = cx.cursor()

        # Enable IDENTITY_INSERT to allow inserting explicit IDs
        cur.execute(f"SET IDENTITY_INSERT dbo.{q(table)} ON")

        with csv_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cols = [c for c in (reader.fieldnames or [])]
            placeholders = ",".join("?" for _ in cols)
            sql = f"INSERT INTO dbo.{q(table)} ({','.join(q(c) for c in cols)}) VALUES ({placeholders})"

            batch = []
            n = 0
            for row in reader:
                vals = [row.get(c) for c in cols]
                # Convert empty strings to NULL for nullable columns
                vals = [None if (v is not None and str(v).strip() == "") else v for v in vals]
                batch.append(vals)

                if len(batch) >= 1000:
                    cur.executemany(sql, batch)
                    n += len(batch)
                    batch.clear()

            if batch:
                cur.executemany(sql, batch)
                n += len(batch)

        # Disable IDENTITY_INSERT after loading
        cur.execute(f"SET IDENTITY_INSERT dbo.{q(table)} OFF")
        cx.commit()

    print(f"[OK] Loaded {n} rows into {table}")

def load_all() -> None:
    """Load all CSV files in dependency order."""
    order = ["Author", "Genre", "BookCopyCondition", "Book", "BookCopy", "Customer", "LibraryCard", "Checkout"]

    for table in order:
        csv_path = TABLE_FILES[table]
        if not csv_path.exists():
            raise SystemExit(f"ERROR: Missing CSV file for {table}: {csv_path}")
        load_csv_into_table(table, csv_path)

def verify_connection() -> bool:
    """Verify database connection and schema exists."""
    try:
        with connect(DB_NAME) as cx:
            cur = cx.cursor()
            cur.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo'")
            table_count = cur.fetchone()[0]
            if table_count < 8:
                print(f"ERROR: Expected 8 tables, found {table_count}")
                print("Please run create_schema.sql first!")
                return False
            return True
    except Exception as e:
        print(f"ERROR: Cannot connect to database: {e}")
        print(f"Make sure SQL Server is running and database '{DB_NAME}' exists.")
        print("Run create_schema.sql first!")
        return False

# =============================================
# Main
# =============================================

def main() -> None:
    print("=" * 50)
    print("CSV Data Loader for SharedData Database")
    print("=" * 50)

    # Verify connection
    print("\n1. Verifying database connection...")
    if not verify_connection():
        return
    print("[OK] Database connection verified")

    # Check CSV files
    print("\n2. Checking CSV files...")
    missing = [name for name, path in TABLE_FILES.items() if not path.exists()]
    if missing:
        print(f"ERROR: Missing CSV files: {', '.join(missing)}")
        return
    print(f"[OK] All {len(TABLE_FILES)} CSV files found")

    # Load data
    print("\n3. Loading data...")
    load_all()

    print("\n" + "=" * 50)
    print("[SUCCESS] All data loaded successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()
