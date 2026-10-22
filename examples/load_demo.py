"""Create synthetic local inputs only: uv run python examples/load_demo.py PATH.

This file contains data, not expected results or converter translation rules.
"""
from pathlib import Path
import sys
import duckdb

CUSTOMERS = [("c1", "Aster"), ("c1", "Aster"), ("c2", "Birch"), ("idle", "No orders"), (None, "Null key"), ("", ""), ("space", "   ")]
ORDERS = [
    ("o1", "c1", "1998-01-02 15:30:00", "l1", 125, 25, "150.50"),
    ("o2", "c1", "2000-02-29 23:59:59", "l1", -5, -1, "-6.50"),
    ("o2", "c1", "2000-02-29 23:59:59", "l1", -5, -1, "-6.50"),
    ("o3", "missing", "2024-05-06 08:10:12", "l2", None, None, None),
    (None, None, None, "", 0, 0, "0.00"),
    ("o4", "c2", "2025-12-31 11:10:12", "l2", 1, -1, "0.50"),
]
PRODUCTS = [
    ("p1", "Jaffle", " jaffle ", 125, ""),
    ("p1", "Jaffle duplicate", "BEVERAGE", -5, "cold"),
    ("p2", "No type", None, None, "   "),
    (None, "No SKU", "", 1, None),
]
SUPPLIES = [
    ("s1", "Flour", 250, "Y", "p1"),
    ("s2", "Null cost", None, "1", "p1"),
    ("s3", "Unknown", -5, None, "missing"),
    ("s4", "No key", 1, "y", None),
    ("s5", "Spaces", -5, " ", "p2"),
]


def load(path: str | Path) -> None:
    path = Path(path)
    if path.exists():
        raise ValueError(f"Refuse to overwrite existing data: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as db:
        db.execute('CREATE SCHEMA RAW')
        db.execute('CREATE TABLE RAW.RAW_CUSTOMERS (ID VARCHAR, NAME VARCHAR)')
        db.executemany('INSERT INTO RAW.RAW_CUSTOMERS VALUES (?, ?)', CUSTOMERS)
        db.execute('CREATE TABLE RAW.RAW_ORDERS (ID VARCHAR, CUSTOMER VARCHAR, ORDERED_AT TIMESTAMP, STORE_ID VARCHAR, SUBTOTAL DOUBLE, TAX_PAID DOUBLE, ORDER_TOTAL DECIMAL(12,2))')
        db.executemany('INSERT INTO RAW.RAW_ORDERS VALUES (?, ?, ?, ?, ?, ?, ?)', ORDERS)
        db.execute('CREATE TABLE RAW.RAW_PRODUCTS (SKU VARCHAR, NAME VARCHAR, TYPE VARCHAR, PRICE DOUBLE, DESCRIPTION VARCHAR)')
        db.executemany('INSERT INTO RAW.RAW_PRODUCTS VALUES (?, ?, ?, ?, ?)', PRODUCTS)
        db.execute('CREATE TABLE RAW.RAW_SUPPLIES (ID VARCHAR, NAME VARCHAR, COST DOUBLE, PERISHABLE VARCHAR, SKU VARCHAR)')
        db.executemany('INSERT INTO RAW.RAW_SUPPLIES VALUES (?, ?, ?, ?, ?)', SUPPLIES)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: uv run python examples/load_demo.py PATH.duckdb')
    load(sys.argv[1])
