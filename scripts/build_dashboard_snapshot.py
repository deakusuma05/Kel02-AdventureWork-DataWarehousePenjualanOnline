"""Build the dashboard from actual INSERT rows; never execute dump DDL.

Money uses integer units of 1/10000 so JavaScript aggregation preserves the
DECIMAL(19,4) source exactly for this dataset. Decimal dimension attributes are
strings. The parser accepts phpMyAdmin literal INSERTs and rejects expressions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from decimal import Decimal
from datetime import date as calendar_date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sql/adventureworks_dw (2).sql"
OUTPUT = ROOT / "dashboard/assets/data/snapshot.json"
DIM_KEYS = {
    "dim_tanggal": "tanggal_key", "dim_product": "product_key",
    "dim_customer": "customer_key", "dim_territory": "territory_key",
    "dim_promotion": "promotion_key", "dim_currency": "currency_key",
    "dim_ship_method": "ship_method_key",
}
FACT_COLUMNS = ["sales_detail_key", "sales_order_id", "tanggal_key", "product_key",
                "customer_key", "territory_key", "promotion_key", "currency_key",
                "ship_method_key", "order_qty", "unit_price_scaled",
                "unit_price_discount_scaled", "line_total_scaled"]


def split_sql(text):
    """Yield statements without splitting on semicolons inside quoted strings."""
    start = 0
    quote = None
    i = 0
    while i < len(text):
        c = text[i]
        if quote:
            if c == "\\":
                i += 2
                continue
            if c == quote:
                if i + 1 < len(text) and text[i + 1] == quote:
                    i += 2
                    continue
                quote = None
        elif c in "'\"`":
            quote = c
        elif text.startswith("--", i) and (i + 2 == len(text) or text[i + 2].isspace()):
            end = text.find("\n", i)
            i = len(text) if end < 0 else end
            continue
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            if end < 0:
                raise ValueError("Unterminated SQL comment")
            i = end + 2
            continue
        elif c == ";":
            yield text[start:i + 1]
            start = i + 1
        i += 1
    if quote:
        raise ValueError("Unterminated SQL string")
    if text[start:].strip():
        yield text[start:]


def literal_rows(values):
    """Parse literal tuples, including escaped quotes/backslashes and NULL."""
    i = 0
    n = len(values)
    escapes = {"0": "\0", "n": "\n", "r": "\r", "t": "\t", "b": "\b", "Z": "\x1a"}
    while i < n:
        while i < n and (values[i].isspace() or values[i] in ",;"):
            i += 1
        if i == n:
            return
        if values[i] != "(":
            raise ValueError("Expected literal tuple")
        i += 1
        row = []
        while True:
            while i < n and values[i].isspace():
                i += 1
            if i == n:
                raise ValueError("Unterminated tuple")
            if values[i] == "'":
                i += 1
                chars = []
                while i < n:
                    c = values[i]
                    if c == "\\":
                        i += 1
                        if i == n:
                            raise ValueError("Unterminated escape")
                        chars.append(escapes.get(values[i], values[i]))
                    elif c == "'":
                        if i + 1 < n and values[i + 1] == "'":
                            chars.append("'")
                            i += 1
                        else:
                            i += 1
                            break
                    else:
                        chars.append(c)
                    i += 1
                else:
                    raise ValueError("Unterminated string")
                row.append("".join(chars))
            else:
                start = i
                while i < n and values[i] not in ",)":
                    i += 1
                token = values[start:i].strip()
                if token.upper() == "NULL":
                    row.append(None)
                elif re.fullmatch(r"[-+]?\d+", token):
                    row.append(int(token))
                elif re.fullmatch(r"[-+]?\d+\.\d+", token):
                    row.append(Decimal(token))
                else:
                    raise ValueError(f"Unsupported SQL literal: {token[:40]!r}")
            while i < n and values[i].isspace():
                i += 1
            if i >= n or values[i] not in ",)":
                raise ValueError("Expected tuple delimiter")
            delim = values[i]
            i += 1
            if delim == ")":
                yield row
                break


def read_dump(path):
    tables = {}
    for statement in split_sql(path.read_text(encoding="utf-8-sig")):
        match = re.search(r"\bINSERT\s+INTO\s+`([^`]+)`\s*\((.*?)\)\s+VALUES\s*(.*);\s*$",
                          statement, re.S | re.I)
        if not match:
            continue
        table, column_text, values = match.groups()
        columns = re.findall(r"`([^`]+)`", column_text)
        target = tables.setdefault(table, [])
        for row in literal_rows(values):
            if len(row) != len(columns):
                raise ValueError(f"{table}: column/value count mismatch")
            target.append(dict(zip(columns, row)))
    if not tables.get("fact_online_sales"):
        raise ValueError("No fact rows found")
    return tables


def scaled(value):
    if value is None:
        raise ValueError("NULL mandatory measure")
    number = Decimal(value) * 10000
    if number != number.to_integral_value():
        raise ValueError("Source has more than four decimal places")
    result = int(number)
    if abs(result) > 2**53 - 1:
        raise ValueError("Amount exceeds exact JavaScript integer range")
    return result


def build_snapshot(path=SOURCE):
    tables = read_dump(path)
    if "dim_tanggal" not in tables and "dim_date" in tables:
        tables["dim_tanggal"] = tables.pop("dim_date")
    if "tanggal_key" not in tables["dim_tanggal"][0]:
        raise ValueError("Selected source must implement the current tanggal_key contract")
    dimensions = {}
    duplicate_natural_ids = {}
    natural_keys = {"dim_product": "product_id", "dim_customer": "customer_id",
                    "dim_territory": "territory_id", "dim_promotion": "special_offer_id",
                    "dim_currency": "currency_rate_id", "dim_ship_method": "ship_method_id"}
    for table, key in DIM_KEYS.items():
        rows = tables[table]
        dimensions[table] = {str(row[key]): row for row in rows}
        if len(dimensions[table]) != len(rows):
            raise ValueError(f"Duplicate surrogate key in {table}")
        if table in natural_keys:
            counts = Counter(row[natural_keys[table]] for row in rows)
            duplicate_natural_ids[table] = sum(n - 1 for n in counts.values() if n > 1)
    facts = []
    detail_ids, orders, customers, months, unknown_orders = set(), set(), set(), set(), set()
    revenue = units = actual_discount = 0
    estimated_promo = Decimal(0)
    missing = {table: 0 for table in DIM_KEYS}
    unknown_details = {table: 0 for table in DIM_KEYS}
    order_contexts = {}
    for source in sorted(tables["fact_online_sales"], key=lambda row: row["sales_detail_key"]):
        detail_id = source["sales_detail_key"]
        if detail_id in detail_ids:
            raise ValueError("Duplicate fact detail key")
        detail_ids.add(detail_id)
        for table, key in DIM_KEYS.items():
            if str(source[key]) not in dimensions[table]:
                missing[table] += 1
            if source[key] == -1:
                unknown_details[table] += 1
        if any(missing.values()):
            raise ValueError(f"Missing dimension reference: {missing}")
        order_id = source["sales_order_id"]
        orders.add(order_id)
        customer = dimensions["dim_customer"][str(source["customer_key"])]["customer_id"]
        if customer not in (-1, None):
            customers.add(customer)
        date = dimensions["dim_tanggal"][str(source["tanggal_key"])]["tanggal"]
        months.add(date[:7])
        currency = dimensions["dim_currency"][str(source["currency_key"])]
        if currency["currency_rate_id"] == -1:
            unknown_orders.add(order_id)
        context = (date, customer, source["territory_key"], source["ship_method_key"], source["currency_key"])
        if order_id in order_contexts and order_contexts[order_id] != context:
            raise ValueError(f"Conflicting order context for {order_id}")
        order_contexts[order_id] = context
        line = scaled(source["line_total"])
        price = scaled(source["unit_price"])
        revenue += line
        units += source["order_qty"]
        actual_discount += source["order_qty"] * price - line
        promo = dimensions["dim_promotion"][str(source["promotion_key"])]["discount_pct"]
        estimated_promo += source["line_total"] * (promo or Decimal(0))
        facts.append([source[column] if not column.endswith("_scaled") else scaled(source[column[:-7]])
                      for column in FACT_COLUMNS])
    if abs(revenue) > 2**53 - 1:
        raise ValueError("Aggregate exceeds exact JavaScript integer range")
    all_dimension_counts = {table: len(rows) for table, rows in dimensions.items()}
    dates = {calendar_date.fromisoformat(row["tanggal"]) for row in dimensions["dim_tanggal"].values()
             if row["tanggal_key"] != -1}
    expected_days = (max(dates) - min(dates)).days + 1
    missing_dates = [(min(dates) + timedelta(days=i)).isoformat() for i in range(expected_days)
                     if min(dates) + timedelta(days=i) not in dates]
    unknown_present = {table: "-1" in rows for table, rows in dimensions.items()}
    # All fact rows stay intact. Unreferenced dimension copies are redundant for
    # analysis; retain source-wide quality counts to make this projection explicit.
    for table, key in DIM_KEYS.items():
        referenced = {str(row[FACT_COLUMNS.index(key)]) for row in facts} | {"-1"}
        dimensions[table] = {k: row for k, row in dimensions[table].items() if k in referenced}
    relative = path.resolve().relative_to(ROOT).as_posix() if path.resolve().is_relative_to(ROOT) else path.name
    return {
        "schema_version": 1,
        "source_table_aliases": {"dim_date": "dim_tanggal"},
        "meta": {
            "source_file": relative, "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "money_scale": 10000, "currency_label": "Nilai sumber (tanpa konversi)",
            "source_selection": "Dump 9 November 2026 memakai tanggal_key dan 12 atribut kalender; dump 2 November masih date_key/full_date.",
            "metrics": {"details": len(facts), "orders": len(orders), "units": units,
                        "active_customers": len(customers), "revenue_scaled": revenue,
                        "months": len(months), "orders_without_rate": len(unknown_orders),
                        "actual_discount_scaled": actual_discount,
                        "estimated_promo_discount": str(estimated_promo),
                        "first_date": min(row[0] for row in order_contexts.values()),
                        "last_date": max(row[0] for row in order_contexts.values())},
            "quality": {"missing_references": missing, "unknown_key_details": unknown_details,
                        "duplicate_fact_keys": 0, "duplicate_surrogate_keys": 0,
                        "duplicate_natural_id_rows": duplicate_natural_ids,
                        "dimension_rows": all_dimension_counts,
                        "snapshot_dimension_rows": {table: len(rows) for table, rows in dimensions.items()},
                        "unknown_member_present": unknown_present,
                        "calendar_missing_dates": missing_dates,
                        "source_constraints_runtime": "Validasi DB dicatat terpisah; generator hanya memeriksa isi dump."},
        },
        "dimension_projection": "Semua fakta disertakan; dimensi hanya memuat key yang dipakai fakta dan -1 jika ada. Statistik kualitas tetap mengaudit seluruh dump.",
        "dimensions": dimensions, "fact_columns": FACT_COLUMNS, "facts": facts,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true", help="Compare generated bytes to committed snapshot")
    args = parser.parse_args()
    snapshot = build_snapshot(args.source)
    payload = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"), default=str) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != payload:
            raise SystemExit("FAIL: snapshot differs from source; regenerate")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS", "source": snapshot["meta"]["source_file"],
                      "metrics": snapshot["meta"]["metrics"], "bytes": len(payload.encode("utf-8"))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
