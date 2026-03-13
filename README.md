# retail-dashery 🛒📊

> **A growing collection of open-source, zero-dependency retail analytics dashboards.**  
> Each one ships with a data generator, a build script, sample CSVs, and a pre-built HTML demo — no server, no npm, no build step. Clone, run, open in browser.

---

## Why retail-dashery?

Retail data is rich, messy, and deeply contextual — but most off-the-shelf dashboards are either locked behind SaaS paywalls or require a full data engineering stack to run. This repo is the opposite: every dashboard here is a **single self-contained HTML file** you can email, host on GitHub Pages, drop in a shared drive, or open locally. The templates are designed to be adapted to real data with minimal friction.

---

## 📦 Dashboards

### 01 · [chain-retail-kpi-dashboard](https://github.com/nova-tabularium/retail-dashery/tree/main/chain-retail-kpi-dashboard)

**Multi-store retail chain analytics — sales, weather, format, and co-tenant analysis**

A full-featured operations dashboard for a multi-location retail chain. Covers 4+ years of daily sales data across 12 stores in 3 regions, with weather correlation, promotional lift analysis, and store format benchmarking.

**Highlights:**
- KPI cards (revenue, transactions, AOV, units, return rate)
- Revenue over time at daily / weekly / monthly / quarterly granularity
- YoY comparison (each year as a line, indexed by month/week/quarter)
- MoM and WoW % change line charts — full timeframe, colour-coded positive/negative
- Per-store revenue lines with toggle chips
- Revenue by store (horizontal, sorted, region-coloured) · Day-of-week pattern
- Revenue vs temperature (bucketed avg by region) · Promo lift by region
- Co-tenant impact — avg sales with/without each neighbour, plus lift %
- Store Ranking table — auto-sorted, click-to-re-sort, inline bar charts
- Auto-insights panel (9 live cards: YoY, MoM, WoW, top store, promo lift, weekend lift, snow impact, best region, laggard store)
- Sidebar with 8 independent filter dimensions (date, region, format, store, promo, temp range, weather flags)
- One-click PDF export — white background, filter summary header, full chart fidelity

| | |
|---|---|
| **Stores** | 12 (configurable up to 50) |
| **Date range** | 2022-01-01 → 2026-02-28 |
| **Sample rows** | 18,240 |
| **Dependencies** | Chart.js · html2canvas · jsPDF (all CDN) |
| **Build time** | ~3 seconds |

---

## 🔜 Coming soon

> Have a dashboard type you'd like to see? [Open an issue](https://github.com/nova-tabularium/retail-dashery/issues) — requests welcome.

| # | Name | Description | Status |
|---|------|-------------|--------|
| 02 | `ecommerce-funnel-dashboard` | Conversion funnel, cart abandonment, channel attribution, cohort retention | 🔧 Planned |
| 03 | `foodservice-throughput-dashboard` | Table turns, ticket times, daypart analysis, menu item performance | 🔧 Planned |
| 04 | `inventory-health-dashboard` | Stock levels, days-on-hand, shrink rate, reorder triggers by SKU and location | 🔧 Planned |
| 05 | `promo-effectiveness-dashboard` | Pre/during/post promo windows, halo effects, cannibalization, ROI by campaign | 🔧 Planned |

---

## 🚀 How every dashboard in this repo works

Each subfolder is self-contained and follows the same pattern:

```
<dashboard-name>/
├── README.md              ← dashboard-specific docs
├── generate_data.py       ← generates realistic sample CSVs
├── build_dashboard.py     ← injects CSVs into template → single HTML file
├── template.html          ← HTML + CSS + JS with %%NOVA_DATA%% placeholder
├── demo_dashboard.html    ← pre-built, open directly in any browser
└── data/
    ├── fact_*.csv
    ├── dim_*.csv
    └── ...
```

**The two-step workflow:**

```bash
# Step 1 — generate sample data (or swap in your own CSVs)
python generate_data.py --out-dir ./data

# Step 2 — build the dashboard
python build_dashboard.py --data-dir ./data --out demo_dashboard.html

# Step 3 — open in browser
open demo_dashboard.html
```

No `pip install`. No Node. No Docker. Works offline.

---

## 🛠 Design principles

- **Single file output** — the finished dashboard is one `.html` file with all data embedded. Email it, host it on GitHub Pages, open it locally. No CDN required at runtime for the data.
- **Bring your own data** — every dashboard documents its CSV schema clearly. Match the columns, run `build_dashboard.py`, done.
- **No framework lock-in** — vanilla JS ES6, Chart.js for charts, html2canvas + jsPDF for export. Easy to read, easy to fork.
- **Reproducible samples** — `generate_data.py --seed 42` always produces identical data for demos and testing.
- **Filterable by design** — every chart reacts to sidebar filters. All aggregation happens in the browser at render time, not pre-baked.

---

## 📜 License

MIT — free to use, modify, and distribute. Attribution appreciated but not required.

---

*by [nova-tabularium](https://github.com/nova-tabularium)*
