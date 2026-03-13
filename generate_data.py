#!/usr/bin/env python3
"""
generate_data.py — Nova Tabularium sample data generator
=========================================================
Generates three CSV files that feed the Nova Tabularium retail dashboard:

  fact_sales_daily.csv  — one row per store per day (sales + weather)
  dim_store.csv         — one row per store (metadata)
  dim_cotenant.csv      — one row per store × co-tenant pairing

Usage
-----
  python generate_data.py                         # defaults: 2022-01-01 → today
  python generate_data.py --start 2023-01-01 --end 2025-12-31
  python generate_data.py --stores 20 --seed 99
  python generate_data.py --out-dir ./my_data/

Arguments
---------
  --start     First date to generate (YYYY-MM-DD, default: 2022-01-01)
  --end       Last date to generate  (YYYY-MM-DD, default: today)
  --stores    Number of stores to simulate (default: 12, max: 50)
  --seed      Random seed for reproducibility (default: 42)
  --out-dir   Output directory for CSVs (default: current directory)
"""

import argparse, csv, math, os, random
from datetime import date, timedelta

# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start",   default="2022-01-01", help="Start date YYYY-MM-DD")
    p.add_argument("--end",     default=str(date.today()), help="End date YYYY-MM-DD")
    p.add_argument("--stores",  type=int, default=12,  help="Number of stores (max 50)")
    p.add_argument("--seed",    type=int, default=42,  help="Random seed")
    p.add_argument("--out-dir", default=".",           help="Output directory")
    return p.parse_args()

# ── Store catalogue (up to 50 stores across Canada) ──────────────────────────
STORE_CATALOGUE = [
    ("S01","Toronto Flagship",   "East",    "Flagship",   4200, True,  "Toronto"),
    ("S02","Toronto Eaton Centre","East",   "Mall",       2100, False, "Toronto"),
    ("S03","Scarborough Town",   "East",    "Standalone", 1800, True,  "Scarborough"),
    ("S04","Mississauga Square", "East",    "Mall",       2400, False, "Mississauga"),
    ("S05","Ottawa Rideau",      "East",    "Standalone", 1600, True,  "Ottawa"),
    ("S06","Montreal Centre",    "East",    "Flagship",   3800, False, "Montreal"),
    ("S07","Halifax Spring Garden","East",  "Standalone", 1400, True,  "Halifax"),
    ("S08","Vancouver Robson",   "West",    "Flagship",   4000, False, "Vancouver"),
    ("S09","Vancouver Metrotown","West",    "Mall",       2200, True,  "Vancouver"),
    ("S10","Surrey Power Centre","West",    "Standalone", 1900, True,  "Surrey"),
    ("S11","Calgary Chinook",    "Central", "Mall",       2600, True,  "Calgary"),
    ("S12","Winnipeg Polo Park", "Central", "Mall",       2000, False, "Winnipeg"),
    ("S13","Edmonton West Ed",   "Central", "Flagship",   3600, True,  "Edmonton"),
    ("S14","Regina Cornwall",    "Central", "Standalone", 1500, True,  "Regina"),
    ("S15","Hamilton Jackson",   "East",    "Standalone", 1700, False, "Hamilton"),
    ("S16","Quebec City Laurier","East",    "Mall",       2300, True,  "Quebec City"),
    ("S17","Kitchener Fairview", "East",    "Mall",       2100, False, "Kitchener"),
    ("S18","London White Oaks",  "East",    "Standalone", 1600, True,  "London"),
    ("S19","Victoria Bay Centre","West",    "Mall",       2200, True,  "Victoria"),
    ("S20","Kelowna Orchard",    "West",    "Standalone", 1500, False, "Kelowna"),
    ("S21","Burnaby Metropolis", "West",    "Mall",       2800, True,  "Burnaby"),
    ("S22","Richmond Centre",    "West",    "Mall",       2400, False, "Richmond"),
    ("S23","Abbotsford Sevenoaks","West",   "Standalone", 1600, True,  "Abbotsford"),
    ("S24","Saskatoon Market Mall","Central","Mall",      2100, True,  "Saskatoon"),
    ("S25","Lethbridge Park Place","Central","Standalone",1400, False, "Lethbridge"),
] + [
    (f"S{26+i:02d}", f"Store Extra {26+i}", 
     random.choice(["East","West","Central"]),
     random.choice(["Flagship","Mall","Standalone"]),
     random.randint(1200,4000), random.choice([True,False]),
     random.choice(["Toronto","Vancouver","Calgary","Ottawa","Montreal"]))
    for i in range(25)
]

COTENANTS_POOL = [
    "Food Court","Cinema","Pharmacy","Gym","Grocery","Coffee Shop",
    "Bank Branch","Electronics","Bookstore","Fitness Studio",
    "Department Store","Pet Store","Hardware","Optical","Bakery"
]

CITY_TEMPS = {
    "Toronto":     [-5,-4,0,8,15,21,24,23,18,11,4,-3],
    "Scarborough": [-5,-4,0,8,15,21,24,23,18,11,4,-3],
    "Mississauga": [-5,-4,0,8,15,21,24,23,18,11,4,-3],
    "Ottawa":      [-10,-9,-3,6,14,20,23,22,16,9,1,-7],
    "Montreal":    [-10,-9,-3,6,14,20,23,22,16,9,1,-7],
    "Halifax":     [-6,-6,-1,5,12,18,21,21,16,10,4,-3],
    "Hamilton":    [-5,-4,0,8,15,21,24,23,18,11,4,-3],
    "Quebec City": [-12,-10,-4,5,13,19,22,21,15,8,1,-8],
    "Kitchener":   [-6,-5,-1,7,14,20,23,22,17,11,3,-4],
    "London":      [-5,-4,0,8,15,21,24,23,18,11,4,-3],
    "Calgary":     [-9,-6,-1,7,13,17,20,19,13,7,-1,-7],
    "Edmonton":    [-12,-9,-3,6,12,17,20,19,13,6,-3,-10],
    "Winnipeg":    [-16,-13,-5,5,13,19,22,21,14,7,-3,-13],
    "Regina":      [-14,-12,-4,6,13,18,21,20,13,6,-3,-11],
    "Saskatoon":   [-15,-12,-4,6,12,18,21,20,13,6,-3,-12],
    "Lethbridge":  [-7,-5,0,8,13,17,20,19,13,7,-1,-6],
    "Vancouver":   [4,5,7,11,15,18,21,21,17,12,7,4],
    "Surrey":      [4,5,7,11,15,18,21,21,17,12,7,4],
    "Burnaby":     [4,5,7,11,15,18,21,21,17,12,7,4],
    "Richmond":    [4,5,7,11,15,18,21,21,17,12,7,4],
    "Abbotsford":  [3,4,6,10,14,17,20,20,16,11,6,3],
    "Victoria":    [5,6,8,11,14,17,19,19,17,12,8,5],
    "Kelowna":     [-3,-1,3,9,15,20,24,23,17,10,2,-2],
}

# Revenue profile: (base_daily_mean, base_daily_std) by format
FORMAT_PROFILE = {
    "Flagship":   (18000, 5000),
    "Mall":       (11000, 3200),
    "Standalone": (7500,  2200),
}

# Canadian stat holidays (YYYY-MM-DD) — add more as needed
CA_HOLIDAYS = {
    "2022-01-01","2022-02-21","2022-05-23","2022-07-01","2022-08-01",
    "2022-09-05","2022-10-10","2022-11-11","2022-12-25","2022-12-26",
    "2023-01-01","2023-02-20","2023-05-22","2023-07-01","2023-08-07",
    "2023-09-04","2023-10-09","2023-11-11","2023-12-25","2023-12-26",
    "2024-01-01","2024-02-19","2024-05-20","2024-07-01","2024-08-05",
    "2024-09-02","2024-10-14","2024-11-11","2024-12-25","2024-12-26",
    "2025-01-01","2025-02-17","2025-05-19","2025-07-01","2025-08-04",
    "2025-09-01","2025-10-13","2025-11-11","2025-12-25","2025-12-26",
    "2026-01-01","2026-02-16","2026-05-18","2026-07-01","2026-08-03",
}

# ── Promo calendar (store-agnostic weeks) ─────────────────────────────────────
# Every ~5–6 weeks a 7–10 day promo window fires for a random subset of stores
def build_promo_set(start, end, store_ids, rng):
    promo = set()
    d = start
    while d <= end:
        if rng.random() < 0.18:  # ~18% of days are promo somewhere
            promo.add(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)
    return promo

# ── Main generation ───────────────────────────────────────────────────────────
def generate(start_date, end_date, n_stores, seed, out_dir):
    rng = random.Random(seed)
    os.makedirs(out_dir, exist_ok=True)

    stores = STORE_CATALOGUE[:n_stores]

    # Assign co-tenants: 1–4 per store, drawn from pool
    cotenant_rows = []
    store_cotenants = {}
    for sid, sname, region, fmt, sqft, dt, city in stores:
        pool_copy = COTENANTS_POOL[:]
        rng.shuffle(pool_copy)
        n_ct = rng.randint(1, 4) if fmt != "Standalone" else rng.randint(0, 2)
        chosen = pool_copy[:n_ct]
        store_cotenants[sid] = chosen
        for ct in chosen:
            cotenant_rows.append({"store_id": sid, "cotenant": ct})

    # dim_store.csv
    store_rows = []
    for sid, sname, region, fmt, sqft, dt, city in stores:
        store_rows.append({
            "store_id":       sid,
            "store_name":     sname,
            "region":         region,
            "format":         fmt,
            "sq_ft":          sqft,
            "drive_thru":     int(dt),
            "cotenant_count": len(store_cotenants[sid]),
            "city":           city,
        })

    # YoY growth rates per store (slight variation for realism)
    yoy_growth = {s[0]: rng.uniform(0.04, 0.15) for s in stores}

    # Baseline revenue per store (vary around format mean)
    base_rev = {}
    for sid, _, _, fmt, _, _, _ in stores:
        mu, sig = FORMAT_PROFILE[fmt]
        base_rev[sid] = {"mu": rng.gauss(mu, mu*0.12), "sig": sig}

    # fact_sales_daily.csv
    promo_days = build_promo_set(start_date, end_date, [s[0] for s in stores], rng)
    fact_rows = []
    year_zero = start_date.year

    d = start_date
    while d <= end_date:
        ds = d.strftime("%Y-%m-%d")
        is_hol = 1 if ds in CA_HOLIDAYS else 0
        is_promo_global = 1 if ds in promo_days else 0
        yrs_elapsed = (d.year - year_zero) + (d.month - 1) / 12

        for sid, _, _, fmt, sqft, drive_thru, city in stores:
            temps = CITY_TEMPS.get(city, [-5,0,5,10,15,20,22,22,17,10,3,-3])
            temp_mu = temps[d.month - 1]
            temp_c  = round(temp_mu + rng.gauss(0, 3.5), 1)
            snow    = 1 if temp_c < 2 and rng.random() < 0.28 else 0
            extreme = 1 if abs(temp_c) > 18 and rng.random() < 0.22 else 0

            dow  = d.weekday()
            mu   = base_rev[sid]["mu"]
            sig  = base_rev[sid]["sig"]

            # Multipliers
            mult = 1.0
            mult *= (1.0 + yoy_growth[sid]) ** yrs_elapsed   # YoY trend
            if dow >= 5:      mult *= 1.35                    # weekend lift
            if is_promo_global: mult *= 1.22                  # promo lift
            if extreme:       mult *= 0.68                    # extreme weather drag
            elif snow:        mult *= 0.87
            if drive_thru and snow: mult *= 1.08              # drive-thru resilience
            if is_hol:        mult *= 0.76                    # holiday drag
            if temp_c > 22:   mult *= 1.04                    # warm weather boost

            # Seasonal pattern (retail peak Nov–Dec)
            seasonal = 1.0 + 0.12 * math.cos((d.month - 12) * 2 * math.pi / 12)
            mult *= seasonal

            rev  = max(300, rng.gauss(mu * mult, sig * 0.38))
            rev  = round(rev, 2)
            txn  = max(20, int(rev / rng.uniform(26, 42)))
            aov  = round(rev / txn, 2)
            units = max(30, int(txn * rng.uniform(1.3, 2.3)))
            rets  = max(0, int(units * rng.uniform(0.003, 0.048)))

            fact_rows.append({
                "date":            ds,
                "store_id":        sid,
                "revenue":         rev,
                "transactions":    txn,
                "avg_order_value": aov,
                "units_sold":      units,
                "returns":         rets,
                "is_promo":        is_promo_global,
                "is_holiday":      is_hol,
                "temp_c":          temp_c,
                "snow":            snow,
                "extreme_weather": extreme,
            })
        d += timedelta(days=1)

    # ── Write CSVs ─────────────────────────────────────────────────────────────
    def write_csv(path, rows):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
        print(f"  ✓ {path}  ({len(rows):,} rows)")

    write_csv(os.path.join(out_dir, "fact_sales_daily.csv"), fact_rows)
    write_csv(os.path.join(out_dir, "dim_store.csv"),        store_rows)
    write_csv(os.path.join(out_dir, "dim_cotenant.csv"),     cotenant_rows)
    print(f"\nDone. {len(fact_rows):,} fact rows · {n_stores} stores · "
          f"{start_date} → {end_date}")

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = parse_args()
    generate(
        start_date = date.fromisoformat(args.start),
        end_date   = date.fromisoformat(args.end),
        n_stores   = min(args.stores, 50),
        seed       = args.seed,
        out_dir    = args.out_dir,
    )
