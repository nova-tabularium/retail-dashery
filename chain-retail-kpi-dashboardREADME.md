# Retail Chain KPI Insights with Nova Tabularium 📊

> **A zero-dependency, single-file retail analytics dashboard.**  
> Generate sample data, point it at your own CSVs, and get a fully interactive dashboard — no server, no npm, no build step.

---

## ✨ What it looks like

A dark-mode, purple-accented analytics dashboard containing:

- Real-time KPI cards, auto-insights, and interactive charts
- Multi-granularity time-series (daily / weekly / monthly / quarterly)
- Store-level, region-level, and chain-level views
- Weather, promo, co-tenant, and format impact analysis
- A ranked store table with click-to-sort columns
- One-click white-background PDF export with active-filter summary

---

## 📁 Repository structure

```
retail-dashery/
│
├── README.md
├── generate_data.py       # Step 1 — generate sample CSV data
├── build_dashboard.py     # Step 2 — compile CSVs into a self-contained HTML
├── template.html          # The dashboard shell (HTML + CSS + Chart.js app)
│
├── data/
│   ├── fact_sales_daily.csv   # 18,240 rows — one row per store per day
│   ├── dim_store.csv          # 12 rows — store metadata
│   └── dim_cotenant.csv       # 28 rows — co-tenant pairings
│
└── demo_dashboard.html        # ✅ Final output — open this in a browser
```

---

## 🚀 Quick start (sample data)

```bash
# 1. Clone
git clone https://github.com/yourname/retail-dashery.git
cd retail-dashery

# 2. Open the pre-built dashboard immediately
open demo_dashboard.html        # macOS
start demo_dashboard.html       # Windows
xdg-open demo_dashboard.html    # Linux

# OR regenerate from scratch:
python generate_data.py --out-dir ./data
python build_dashboard.py --data-dir ./data --out demo_dashboard.html
```

That's it. No `pip install`, no Node, no webpack.

---

## 🔌 Using your own data

### 1 — Prepare three CSV files

#### `fact_sales_daily.csv`
One row per **store per day**. All columns required.

| Column | Type | Notes |
|--------|------|-------|
| `date` | YYYY-MM-DD | e.g. `2024-03-15` |
| `store_id` | string | Must match `dim_store.csv` |
| `revenue` | float | Total revenue for the day |
| `transactions` | int | Number of transactions |
| `avg_order_value` | float | Revenue ÷ transactions |
| `units_sold` | int | Total units sold |
| `returns` | int | Units returned |
| `is_promo` | 0 or 1 | Was a promotion running? |
| `is_holiday` | 0 or 1 | Is it a public holiday? |
| `temp_c` | float | Daily high temperature in °C |
| `snow` | 0 or 1 | Was there snowfall? |
| `extreme_weather` | 0 or 1 | Extreme weather event? |

#### `dim_store.csv`
One row per **location**.

| Column | Type | Notes |
|--------|------|-------|
| `store_id` | string | Primary key, e.g. `S01` |
| `store_name` | string | Display name |
| `region` | string | `East`, `West`, or `Central` |
| `format` | string | `Flagship`, `Mall`, or `Standalone` |
| `sq_ft` | int | Store floor area |
| `drive_thru` | 0 or 1 | Has a drive-through lane? |
| `cotenant_count` | int | Number of co-tenants in the property |
| `city` | string | City name (for display only) |

> **Custom regions/formats:** If your data uses different region or format names, edit the `RC` and `FC` colour maps near the top of `template.html`.

#### `dim_cotenant.csv`
One row per **store × co-tenant pairing** (long format).

| Column | Type | Notes |
|--------|------|-------|
| `store_id` | string | Foreign key to `dim_store.csv` |
| `cotenant` | string | Co-tenant name, e.g. `Cinema`, `Pharmacy` |

If a store has no co-tenants, simply omit it from this file.

---

### 2 — Build the dashboard

```bash
python build_dashboard.py \
  --fact     path/to/fact_sales_daily.csv \
  --store    path/to/dim_store.csv \
  --cotenant path/to/dim_cotenant.csv \
  --out      demo_dashboard.html
```

Open `demo_dashboard.html` in Chrome, Firefox, Edge, or Safari. Nothing else required.

---

## 🧩 Data generation script

`generate_data.py` produces realistic synthetic Canadian retail data for testing and demos.

```bash
# Defaults: 12 stores, 2022-01-01 to today
python generate_data.py

# Custom range and store count
python generate_data.py --start 2020-01-01 --end 2026-12-31 --stores 25

# Reproducible seed + custom output directory
python generate_data.py --seed 99 --out-dir ./data

# Full options
python generate_data.py --help
```

**Baked-in realism:**
- City-specific seasonal temperature curves (Vancouver mild/rainy; Edmonton harsh winters; etc.)
- YoY revenue growth of 4–15% per store
- Weekend lift ~35%; promo lift ~22%; extreme-weather drag ~32%
- Drive-thru stores recover ~8% of snow-day losses
- November–December seasonal peak (retail holiday pattern)
- Canadian statutory holidays modelled for 2022–2026

---

## 📊 Dashboard sections

| Section | Description |
|---------|-------------|
| **KPI Bar** | Total revenue, transactions, units sold, avg daily revenue, avg order value. All react to sidebar filters. |
| **Auto Insights** | 9 live insight cards: YoY %, MoM %, WoW %, top store, promo lift, weekend lift, snow impact, best region, store needing attention. |
| **Revenue Over Time** | Chain-total line chart. Granularity selector: Daily / Weekly / Monthly / Quarterly. |
| **Avg Order Value Over Time** | Monthly AOV trend across all filtered stores. |
| **Revenue by Store Over Time** | Each store as its own monthly line. Toggle individual stores via colour-coded chips. |
| **Year-over-Year Comparison** | Each calendar year as a line, indexed by Month / Week / Quarter. Works with a single year selected. |
| **Month-over-Month % Change** | Full-timeframe line chart; line turns red on negative months. |
| **Week-over-Week % Change** | Full-timeframe line chart; line turns red on negative weeks. |
| **Revenue by Store** | Horizontal bar chart, colour = region. Toggle: Total Revenue / Revenue per sq ft / Transactions. |
| **Day of Week Pattern** | Average daily revenue Mon–Sun. Weekends highlighted in pink. |
| **Revenue by Region** | Bar or pie chart toggle. East (purple) / West (cyan) / Central (amber). |
| **Store Format Breakdown** | Doughnut chart. Flagship / Mall / Standalone. |
| **Revenue vs Temperature** | Average daily revenue bucketed into 6 temperature ranges, one line per region. |
| **Promo Lift by Region** | Grouped bar: promo vs non-promo average daily revenue by region. |
| **Co-Tenant Impact** | Toggle between avg daily revenue with/without each co-tenant, or pure lift %. |
| **Store Ranking** | Auto-sorted table by revenue. Click any column header to re-sort. Rank badges, format pills, inline bar charts. |

---

## 🎛️ Sidebar filters

All charts and KPIs react instantly to any combination of:

- **Date range** — custom from/to or quick presets (2022 / 2023 / 2024 / 2025 / 2026 / All)
- **Region** — multi-select checkboxes
- **Store format** — Flagship / Mall / Standalone
- **Individual stores** — searchable list, select all / clear all
- **Promotion flag** — all days / promo only / non-promo only
- **Temperature range** — dual sliders for min/max °C
- **Exclude extreme weather** — checkbox
- **Exclude snow days** — checkbox

---

## 📄 PDF export

Click **⬇ Export PDF** in the top-right header.

The exporter:
1. Temporarily switches the entire dashboard to a white/light theme by swapping CSS custom properties on `:root`
2. Re-renders all Chart.js charts in light colours
3. Captures each section with `html2canvas` at 2× resolution
4. Assembles pages in `jsPDF` with a filter summary banner at the top
5. Restores the dark theme and downloads `nova-tabularium-report.pdf`

The PDF lists the active date range, regions, formats, store count, and row count at the top of the first page.

---

## 🛠 Technical notes

| Concern | Decision |
|---------|----------|
| **Zero server** | All data is embedded as a `<script type="application/json">` tag — the browser treats it as inert text, so parsing is non-blocking and the loading screen renders instantly |
| **No build step** | Vanilla JS ES6, Chart.js 4.4 via CDN, html2canvas 1.4, jsPDF 2.5 |
| **Performance** | 18,240 rows (4 years × 12 stores) load and filter sub-second on modern hardware; the enrichment loop (date parsing, week number, DOY) runs once on init |
| **Reproducibility** | `generate_data.py --seed 42` always produces identical CSVs |
| **Extensibility** | Add a new chart by writing a `drawXxx()` function and calling it inside `renderAll()`. All data is in the global `FD` array (filtered) and `RAW` (unfiltered) |
| **Colour palette** | 10-colour `PAL` array + named regional (`RC`) and format (`FC`) colour maps — swap hex codes to rebrand |
| **Browser support** | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ |

---

## 🗺 Roadmap ideas

- [ ] Forecast overlay on Revenue Over Time (simple linear or exponential smoothing)
- [ ] Cohort analysis by store opening year
- [ ] Basket-size distribution histogram
- [ ] Map view (Leaflet.js) — pin stores, colour by performance
- [ ] CSV export of any filtered table view
- [ ] Dark/light mode toggle without PDF-only workaround
- [ ] Multi-currency support

---

## 📜 License

MIT — use freely, modify openly, attribution appreciated.

---

*Built with Chart.js · html2canvas · jsPDF · zero dependencies*
