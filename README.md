# Home Value Tracker: 1766 Crestridge Cir, Princeton, TX 75407

Automated tracking, historical valuation records, and analytics dashboard for **1766 Crestridge Cir, Princeton, TX 75407** (Princeton Lakeside Estates, Collin County).

---

## Property Snapshot

- **Address:** 1766 Crestridge Cir, Princeton, TX 75407
- **County:** Collin County
- **Subdivision:** Princeton Lakeside Estates
- **Building Size:** 2,982 sq ft
- **Year Built:** 2023
- **Community Fees:** No HOA / No MUD / No PID
- **Current Valuation Range:** $565,000 – $675,000 (Consensus ~$605,000 | ~$202.88/sqft)

---

## Quick Usage

### 1. View Current Valuation & Summary
```bash
python tracker.py status
```

### 2. View Historical Valuation Log
```bash
python tracker.py history
```

### 3. Log a New Valuation Data Point
```bash
python tracker.py add --source "Zillow Zestimate" --value 612000 --low 575000 --high 640000 --notes "Fall market check"
```
*(Automatically computes price per square foot and updates the HTML dashboard).*

### 4. Open Interactive Dashboard
```bash
python tracker.py dashboard --open
```
Or open `dashboard.html` directly in any web browser.

---

## File Structure

- `tracker.py`: CLI tool for managing data, computing growth metrics, and regenerating the dashboard.
- `home_data.json`: Core property metadata and authoritative valuation portal URLs.
- `value_history.csv`: Historical time-series data of appraisal benchmarks and automated valuations.
- `dashboard.html`: Standalone, interactive HTML dashboard with Chart.js visualization.

---

## Authoritative Portals

- [Collin Central Appraisal District (CAD)](https://esearch.collincad.org/)
- [Realtor.com / Quantarium Listing](https://www.realtor.com/realestateandhomes-detail/1766-Crestridge-Cir_Princeton_TX_75407_M89849-01257)
- [Zillow Property Page](https://www.zillow.com/homes/1766-Crestridge-Cir-Princeton,-TX-75407_rb/)
- [Redfin](https://www.redfin.com)
