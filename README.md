# retail-dashery 🛒📊

> **A growing collection of open-source, zero-dependency retail analytics dashboards.**  
> Each one ships with a data generator, a build script, sample CSVs, and a live demo — no server, no npm, no build step.

---

## 📦 Dashboards

### 01 · [chain-retail-kpi-dashboard](https://github.com/nova-tabularium/retail-dashery/tree/main/chain-retail-kpi-dashboard)

**Multi-store retail chain analytics — sales, weather, format & co-tenant analysis**

![demo](chain-retail-kpi-dashboard/demo.gif)

[![View Folder](https://img.shields.io/badge/View%20Folder-GitHub-333?style=for-the-badge&logo=github)](https://github.com/nova-tabularium/retail-dashery/tree/main/chain-retail-kpi-dashboard)

A full-featured operations dashboard for a multi-location retail chain covering 4+ years of daily sales across 12 stores in 3 regions. Explore revenue trends, weather correlation, promo lift, co-tenant impact, and store rankings — all filterable in real time.

---

## 🔜 Coming soon

| # | Dashboard | Description |
|---|-----------|-------------|
| 02 | `ecommerce-funnel-dashboard` | Conversion funnel, cart abandonment, channel attribution, cohort retention |
| 03 | `foodservice-throughput-dashboard` | Table turns, ticket times, daypart analysis, menu item performance |
| 04 | `inventory-health-dashboard` | Stock levels, days-on-hand, shrink, reorder triggers by SKU and location |
| 05 | `promo-effectiveness-dashboard` | Pre/during/post promo windows, halo effects, cannibalization, ROI by campaign |

> Have a dashboard type you'd like to see? [Open an issue](https://github.com/nova-tabularium/retail-dashery/issues) — requests welcome.

---

## 🚀 How it works

Every dashboard in this repo follows the same two-step pattern:

```bash
# 1. Generate sample data (or swap in your own CSVs)
python generate_data.py --out-dir ./data

# 2. Build the self-contained HTML
python build_dashboard.py --data-dir ./data --out demo_dashboard.html

# 3. Open in any browser — no server needed
open demo_dashboard.html
```

No `pip install`. No Node. Works fully offline.

---

## 🛠 Design principles

- **Single file output** — the finished dashboard is one `.html` file with all data embedded. Email it, host it, open it locally.
- **Bring your own data** — every dashboard documents its CSV schema. Match the columns, run the build script, done.
- **No framework lock-in** — vanilla JS ES6 + Chart.js. Easy to read, easy to fork.
- **Filterable by design** — every chart reacts live to sidebar filters. Aggregation runs in the browser at render time.
- **Reproducible samples** — `--seed 42` always produces identical data for demos and testing.

---

## 📜 License

MIT — free to use, modify, and distribute. Attribution appreciated.

---

*by [nova-tabularium](https://github.com/nova-tabularium)*
