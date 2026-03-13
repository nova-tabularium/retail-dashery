#!/usr/bin/env python3
"""
build_dashboard.py — Nova Tabularium dashboard builder
=======================================================
Reads three CSV files, converts them to an embedded JSON payload, and
injects the data into template.html to produce a fully self-contained
single-file HTML dashboard.  No server needed — open the output file
directly in any modern browser.

Usage
-----
  python build_dashboard.py                         # defaults
  python build_dashboard.py --data-dir ./data --out dashboard.html
  python build_dashboard.py --fact my_sales.csv --store my_stores.csv \
                            --cotenant my_cotenants.csv --out report.html

Arguments
---------
  --data-dir   Folder containing the three CSVs (default: current dir)
  --fact       Path to fact CSV   (default: <data-dir>/fact_sales_daily.csv)
  --store      Path to store dim  (default: <data-dir>/dim_store.csv)
  --cotenant   Path to cotenant dim (default: <data-dir>/dim_cotenant.csv)
  --template   Path to template HTML (default: template.html next to this script)
  --out        Output HTML file path (default: nova_tabularium.html)

Column requirements
-------------------
fact_sales_daily.csv columns (all required):
  date, store_id, revenue, transactions, avg_order_value, units_sold,
  returns, is_promo, is_holiday, temp_c, snow, extreme_weather

dim_store.csv columns (all required):
  store_id, store_name, region, format, sq_ft, drive_thru, cotenant_count, city

dim_cotenant.csv columns (all required):
  store_id, cotenant

  The store_id values in all three files must match.
  region   must be one of: East, West, Central  (or edit RC dict in template.html)
  format   must be one of: Flagship, Mall, Standalone

Bringing your own data
----------------------
1. Export your POS data to match fact_sales_daily.csv schema above.
2. Create dim_store.csv with one row per location.
3. Create dim_cotenant.csv with one row per store × co-tenant.
4. Run this script pointing at your files.
5. Open the output HTML in a browser — no install required.
"""

import argparse, csv, json, os, sys
from pathlib import Path


# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-dir",  default=".",
                   help="Folder containing the three input CSVs")
    p.add_argument("--fact",      default=None,
                   help="Override path to fact_sales_daily.csv")
    p.add_argument("--store",     default=None,
                   help="Override path to dim_store.csv")
    p.add_argument("--cotenant",  default=None,
                   help="Override path to dim_cotenant.csv")
    p.add_argument("--template",  default=None,
                   help="Override path to template.html")
    p.add_argument("--out",       default="nova_tabularium.html",
                   help="Output HTML filename (default: nova_tabularium.html)")
    return p.parse_args()


# ── CSV helpers ───────────────────────────────────────────────────────────────
def load_csv(path: str) -> list[dict]:
    """Read a CSV and return a list of dicts, auto-casting numbers."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cast = {}
            for k, v in row.items():
                try:
                    cast[k] = int(v)
                except ValueError:
                    try:
                        cast[k] = float(v)
                    except ValueError:
                        cast[k] = v
            rows.append(cast)
    return rows


def validate_columns(rows: list[dict], required: list[str], label: str):
    """Raise a clear error if any required column is missing."""
    if not rows:
        sys.exit(f"ERROR: {label} is empty.")
    missing = [c for c in required if c not in rows[0]]
    if missing:
        sys.exit(f"ERROR: {label} is missing columns: {missing}\n"
                 f"  Found: {list(rows[0].keys())}")


# ── Main builder ──────────────────────────────────────────────────────────────
def build(fact_path: str, store_path: str, cotenant_path: str,
          template_path: str, out_path: str):

    print("\nNova Tabularium — Dashboard Builder")
    print("=" * 40)

    # Load CSVs
    print(f"  Loading {fact_path} …", end=" ", flush=True)
    fact = load_csv(fact_path)
    validate_columns(fact, [
        "date","store_id","revenue","transactions","avg_order_value",
        "units_sold","returns","is_promo","is_holiday",
        "temp_c","snow","extreme_weather"
    ], "fact_sales_daily.csv")
    print(f"{len(fact):,} rows")

    print(f"  Loading {store_path} …", end=" ", flush=True)
    stores = load_csv(store_path)
    validate_columns(stores, [
        "store_id","store_name","region","format",
        "sq_ft","drive_thru","cotenant_count","city"
    ], "dim_store.csv")
    print(f"{len(stores)} stores")

    print(f"  Loading {cotenant_path} …", end=" ", flush=True)
    cotenant = load_csv(cotenant_path)
    validate_columns(cotenant, ["store_id","cotenant"], "dim_cotenant.csv")
    print(f"{len(cotenant)} co-tenant records")

    # Cross-validation
    store_ids_dim   = {s["store_id"] for s in stores}
    store_ids_fact  = {r["store_id"] for r in fact}
    orphan_fact = store_ids_fact - store_ids_dim
    if orphan_fact:
        print(f"  ⚠  Warning: {len(orphan_fact)} store_id(s) in fact CSV not in "
              f"dim_store.csv: {orphan_fact}")

    # Pack into payload
    payload = json.dumps({"fact": fact, "stores": stores, "cotenant": cotenant},
                         separators=(",", ":"))
    print(f"  JSON payload: {len(payload)/1024/1024:.2f} MB")

    # Inject into template
    print(f"  Reading template {template_path} …", end=" ", flush=True)
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    if "%%NOVA_DATA%%" not in template:
        sys.exit("ERROR: template.html does not contain the %%NOVA_DATA%% placeholder.")
    print("OK")

    html = template.replace("%%NOVA_DATA%%", payload)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"\n  ✓  Saved {out_path}  ({size_mb:.2f} MB)")
    print("     Open this file in any modern browser — no server needed.\n")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = parse_args()
    script_dir = Path(__file__).parent

    fact_path     = args.fact     or os.path.join(args.data_dir, "fact_sales_daily.csv")
    store_path    = args.store    or os.path.join(args.data_dir, "dim_store.csv")
    cotenant_path = args.cotenant or os.path.join(args.data_dir, "dim_cotenant.csv")
    template_path = args.template or str(script_dir / "template.html")

    for p in [fact_path, store_path, cotenant_path, template_path]:
        if not os.path.exists(p):
            sys.exit(f"ERROR: File not found: {p}")

    build(fact_path, store_path, cotenant_path, template_path, args.out)
