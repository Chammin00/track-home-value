#!/usr/bin/env python3
"""
Home Value Tracker for 1766 Crestridge Cir, Princeton, TX 75407
Tracks valuation trends, calculates $/sqft, logs new appraisals/estimates,
and generates an interactive visual dashboard.
"""

import sys
import os
import json
import csv
import argparse
import webbrowser
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_JSON = BASE_DIR / "home_data.json"
HISTORY_CSV = BASE_DIR / "value_history.csv"
DASHBOARD_HTML = BASE_DIR / "dashboard.html"

def load_property_info():
    if not DATA_JSON.exists():
        return {"property": {"building_sqft": 2982, "address": "1766 Crestridge Cir, Princeton, TX 75407"}}
    with open(DATA_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def load_history():
    records = []
    if not HISTORY_CSV.exists():
        return records
    with open(HISTORY_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["estimate_value"] = float(row.get("estimate_value", 0) or 0)
                row["low_range"] = float(row.get("low_range", 0) or 0)
                row["high_range"] = float(row.get("high_range", 0) or 0)
                row["price_per_sqft"] = float(row.get("price_per_sqft", 0) or 0)
            except ValueError:
                pass
            records.append(row)
    return records

def add_entry(source, value, low=None, high=None, date_str=None, notes=""):
    info = load_property_info()
    sqft = info.get("property", {}).get("building_sqft", 2982)
    
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        
    low = low if low is not None else value
    high = high if high is not None else value
    price_sqft = round(value / sqft, 2) if sqft else 0.0

    fieldnames = ["date", "source", "estimate_value", "low_range", "high_range", "price_per_sqft", "notes"]
    file_exists = HISTORY_CSV.exists()
    
    with open(HISTORY_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "date": date_str,
            "source": source,
            "estimate_value": int(value) if value == int(value) else round(value, 2),
            "low_range": int(low) if low == int(low) else round(low, 2),
            "high_range": int(high) if high == int(high) else round(high, 2),
            "price_per_sqft": price_sqft,
            "notes": notes
        })
    print(f"Logged entry: {date_str} | {source} | ${value:,.0f} (${price_sqft:.2f}/sqft)")
    generate_dashboard()

def print_status():
    info = load_property_info()
    prop = info.get("property", {})
    records = load_history()
    
    print("=" * 65)
    print(f"  HOME VALUE TRACKER - {prop.get('address', '1766 Crestridge Cir')}")
    print(f"  {prop.get('city')}, {prop.get('state')} {prop.get('zip')} ({prop.get('county')})")
    print(f"  Subdivision: {prop.get('subdivision')} | Size: {prop.get('building_sqft'):,} sq ft | Built: {prop.get('year_built')}")
    print("=" * 65)
    
    if not records:
        print("No historical entries found.")
        return

    latest = records[-1]
    first = records[0]
    
    diff_val = latest["estimate_value"] - first["estimate_value"]
    pct_val = (diff_val / first["estimate_value"]) * 100 if first["estimate_value"] else 0

    print(f"  Latest Estimate:      ${latest['estimate_value']:,.0f} ({latest['source']})")
    print(f"  As of Date:           {latest['date']}")
    print(f"  Estimated Range:      ${latest['low_range']:,.0f} - ${latest['high_range']:,.0f}")
    print(f"  Price Per Sq Ft:      ${latest['price_per_sqft']:.2f} / sq ft")
    print("-" * 65)
    print(f"  Tracking Baseline:    ${first['estimate_value']:,.0f} ({first['date']})")
    print(f"  Total Tracked Growth: {'+' if diff_val >= 0 else ''}${diff_val:,.0f} ({pct_val:+.2f}%)")
    print("=" * 65)
    print("\nQuick Links:")
    for key, src in info.get("sources", {}).items():
        print(f"  * {src.get('name')}: {src.get('url')}")
    print("\nRun 'python tracker.py --dashboard' to open the interactive chart in your browser.")

def print_history():
    records = load_history()
    if not records:
        print("No history found.")
        return
    print(f"{'Date':<12} | {'Source':<26} | {'Estimate':<12} | {'Range':<22} | {'$/SqFt':<8}")
    print("-" * 88)
    for r in records:
        range_str = f"${r['low_range']:,.0f} - ${r['high_range']:,.0f}"
        print(f"{r['date']:<12} | {r['source']:<26} | ${r['estimate_value']:<11,.0f} | {range_str:<22} | ${r['price_per_sqft']:<7.2f}")

def generate_dashboard():
    info = load_property_info()
    prop = info.get("property", {})
    records = load_history()
    
    dates = [r["date"] for r in records]
    values = [r["estimate_value"] for r in records]
    sources = [r["source"] for r in records]
    sqft_prices = [r["price_per_sqft"] for r in records]

    latest_val = records[-1]["estimate_value"] if records else 605000
    first_val = records[0]["estimate_value"] if records else latest_val
    gain = latest_val - first_val
    gain_pct = (gain / first_val * 100) if first_val else 0.0

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Home Value Tracker - {prop.get('address')}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen p-4 md:p-8">
  <div class="max-w-6xl mx-auto space-y-6">
    <!-- Header -->
    <header class="flex flex-col md:flex-row justify-between items-start md:items-center bg-slate-800/80 backdrop-blur border border-slate-700/60 p-6 rounded-2xl shadow-xl gap-4">
      <div>
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Active Property Tracker
        </div>
        <h1 class="text-3xl font-extrabold text-white tracking-tight">{prop.get('address')}</h1>
        <p class="text-slate-400 text-sm mt-1">{prop.get('city')}, {prop.get('state')} {prop.get('zip')} • {prop.get('county')} • {prop.get('subdivision')}</p>
      </div>
      <div class="text-right flex flex-col md:items-end">
        <span class="text-xs text-slate-400 uppercase font-semibold">Current Value Estimate</span>
        <span class="text-3xl md:text-4xl font-extrabold text-emerald-400">${latest_val:,.0f}</span>
        <span class="text-xs text-emerald-300 font-medium mt-1">Growth: +${gain:,.0f} ({gain_pct:+.1f}%)</span>
      </div>
    </header>

    <!-- KPI Grid -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-slate-800/60 border border-slate-700/50 p-5 rounded-xl">
        <span class="text-xs text-slate-400 font-medium">Estimated Sq. Footage</span>
        <p class="text-2xl font-bold text-white mt-1">{prop.get('building_sqft'):,} <span class="text-xs text-slate-400 font-normal">sq ft</span></p>
        <span class="text-xs text-slate-400 mt-2 block">Built in {prop.get('year_built')}</span>
      </div>
      <div class="bg-slate-800/60 border border-slate-700/50 p-5 rounded-xl">
        <span class="text-xs text-slate-400 font-medium">Price Per Square Foot</span>
        <p class="text-2xl font-bold text-sky-400 mt-1">${latest_val / prop.get('building_sqft', 2982):.2f} <span class="text-xs text-slate-400 font-normal">/ sqft</span></p>
        <span class="text-xs text-sky-300/80 mt-2 block">Competitive Lakeside rate</span>
      </div>
      <div class="bg-slate-800/60 border border-slate-700/50 p-5 rounded-xl">
        <span class="text-xs text-slate-400 font-medium">Estimated Value Range</span>
        <p class="text-xl font-bold text-white mt-1">${records[-1]['low_range']:,.0f} - ${records[-1]['high_range']:,.0f}</p>
        <span class="text-xs text-slate-400 mt-2 block">Spread: ${(records[-1]['high_range'] - records[-1]['low_range']):,.0f}</span>
      </div>
      <div class="bg-slate-800/60 border border-slate-700/50 p-5 rounded-xl">
        <span class="text-xs text-slate-400 font-medium">Community Fees</span>
        <p class="text-lg font-bold text-emerald-400 mt-1">{prop.get('hoa')}</p>
        <span class="text-xs text-slate-400 mt-2 block">District: {prop.get('school_district')}</span>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="bg-slate-800/80 border border-slate-700/60 p-6 rounded-2xl shadow-xl">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h2 class="text-lg font-bold text-white">Valuation Trend Over Time</h2>
          <p class="text-xs text-slate-400">Time-series tracking historical CAD appraisals and automated valuation estimates</p>
        </div>
        <div class="flex items-center gap-2 text-xs text-slate-400 bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-700/40">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Estimated Value
        </div>
      </div>
      <div class="h-80 w-full">
        <canvas id="trendChart"></canvas>
      </div>
    </div>

    <!-- History Table & Live Links -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Valuation Log -->
      <div class="lg:col-span-2 bg-slate-800/80 border border-slate-700/60 p-6 rounded-2xl shadow-xl">
        <h2 class="text-lg font-bold text-white mb-4">Historical Valuation Log</h2>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="text-xs text-slate-400 uppercase bg-slate-900/50 border-b border-slate-700/60">
              <tr>
                <th class="py-3 px-3">Date</th>
                <th class="py-3 px-3">Source</th>
                <th class="py-3 px-3">Valuation</th>
                <th class="py-3 px-3">$/Sq Ft</th>
                <th class="py-3 px-3">Notes</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/40">
              {"".join([f'''
              <tr class="hover:bg-slate-700/30 transition">
                <td class="py-3 px-3 font-mono text-xs text-slate-400">{r['date']}</td>
                <td class="py-3 px-3 font-medium text-white">{r['source']}</td>
                <td class="py-3 px-3 font-semibold text-emerald-400">${r['estimate_value']:,.0f}</td>
                <td class="py-3 px-3 text-sky-300">${r['price_per_sqft']:.2f}</td>
                <td class="py-3 px-3 text-xs text-slate-400">{r['notes']}</td>
              </tr>''' for r in reversed(records)])}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Reference Portals -->
      <div class="bg-slate-800/80 border border-slate-700/60 p-6 rounded-2xl shadow-xl flex flex-col justify-between">
        <div>
          <h2 class="text-lg font-bold text-white mb-2">Live Valuation Portals</h2>
          <p class="text-xs text-slate-400 mb-4">Check live real-time values directly at the primary data providers:</p>
          <div class="space-y-3">
            <a href="https://esearch.collincad.org/" target="_blank" class="block p-3.5 rounded-xl bg-slate-900/70 border border-slate-700 hover:border-emerald-500/50 hover:bg-slate-700/40 transition group">
              <div class="flex items-center justify-between">
                <span class="font-semibold text-white group-hover:text-emerald-400 text-sm">Collin CAD Portal</span>
                <span class="text-xs text-emerald-400">↗</span>
              </div>
              <p class="text-xs text-slate-400 mt-1">Certified county tax appraisal and tax rate info</p>
            </a>
            <a href="https://www.realtor.com/realestateandhomes-detail/1766-Crestridge-Cir_Princeton_TX_75407_M89849-01257" target="_blank" class="block p-3.5 rounded-xl bg-slate-900/70 border border-slate-700 hover:border-emerald-500/50 hover:bg-slate-700/40 transition group">
              <div class="flex items-center justify-between">
                <span class="font-semibold text-white group-hover:text-emerald-400 text-sm">Realtor.com / Quantarium</span>
                <span class="text-xs text-emerald-400">↗</span>
              </div>
              <p class="text-xs text-slate-400 mt-1">Quantarium automated valuation model & range</p>
            </a>
            <a href="https://www.zillow.com/homes/1766-Crestridge-Cir-Princeton,-TX-75407_rb/" target="_blank" class="block p-3.5 rounded-xl bg-slate-900/70 border border-slate-700 hover:border-emerald-500/50 hover:bg-slate-700/40 transition group">
              <div class="flex items-center justify-between">
                <span class="font-semibold text-white group-hover:text-emerald-400 text-sm">Zillow Zestimate</span>
                <span class="text-xs text-emerald-400">↗</span>
              </div>
              <p class="text-xs text-slate-400 mt-1">Zestimate and regional Princeton median trends</p>
            </a>
            <a href="https://www.redfin.com" target="_blank" class="block p-3.5 rounded-xl bg-slate-900/70 border border-slate-700 hover:border-emerald-500/50 hover:bg-slate-700/40 transition group">
              <div class="flex items-center justify-between">
                <span class="font-semibold text-white group-hover:text-emerald-400 text-sm">Redfin Estimate</span>
                <span class="text-xs text-emerald-400">↗</span>
              </div>
              <p class="text-xs text-slate-400 mt-1">Neighborhood comps and recent Collin County sales</p>
            </a>
          </div>
        </div>

        <div class="mt-6 pt-4 border-t border-slate-700/50 text-xs text-slate-400">
          <p>💡 <b>Quick CLI Command:</b></p>
          <code class="block mt-1 p-2 bg-slate-950 rounded border border-slate-800 font-mono text-[11px] text-emerald-400">
            python tracker.py add --source "Zillow" --value 612000
          </code>
        </div>
      </div>
    </div>
  </div>

  <script>
    const ctx = document.getElementById('trendChart').getContext('2d');
    const chartData = {{
      labels: {json.dumps(dates)},
      datasets: [
        {{
          label: 'Estimated Valuation ($)',
          data: {json.dumps(values)},
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.12)',
          fill: true,
          tension: 0.35,
          borderWidth: 3,
          pointBackgroundColor: '#34d399',
          pointBorderColor: '#064e3b',
          pointBorderWidth: 2,
          pointRadius: 6,
          pointHoverRadius: 8
        }}
      ]
    }};

    new Chart(ctx, {{
      type: 'line',
      data: chartData,
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            callbacks: {{
              label: function(context) {{
                return ' ' + context.dataset.label + ': $' + Number(context.parsed.y).toLocaleString();
              }}
            }}
          }}
        }},
        scales: {{
          x: {{
            grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
            ticks: {{ color: '#94a3b8' }}
          }},
          y: {{
            grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
            ticks: {{
              color: '#94a3b8',
              callback: function(value) {{
                return '$' + (value / 1000) + 'k';
              }}
            }}
          }}
        }}
      }}
    }});
  </script>
</body>
</html>"""
    with open(DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated dashboard at {DASHBOARD_HTML}")

def main():
    parser = argparse.ArgumentParser(description="Home Value Tracker for 1766 Crestridge Cir, Princeton, TX")
    subparsers = parser.add_subparsers(dest="command")

    # Status
    subparsers.add_parser("status", help="Show current property status and valuation summary")

    # History
    subparsers.add_parser("history", help="List all recorded valuation data points")

    # Add
    add_parser = subparsers.add_parser("add", help="Add a new valuation record")
    add_parser.add_argument("--source", required=True, help="Valuation source (e.g. Zillow, Realtor, Collin CAD)")
    add_parser.add_argument("--value", required=True, type=float, help="Estimated value in dollars")
    add_parser.add_argument("--low", type=float, default=None, help="Lower bound of estimate")
    add_parser.add_argument("--high", type=float, default=None, help="Upper bound of estimate")
    add_parser.add_argument("--date", default=None, help="Date format YYYY-MM-DD (defaults to today)")
    add_parser.add_argument("--notes", default="", help="Optional notes")

    # Dashboard
    dash_parser = subparsers.add_parser("dashboard", help="Rebuild and optionally open the HTML dashboard")
    dash_parser.add_argument("--open", action="store_true", help="Open the dashboard directly in default browser")

    args = parser.parse_args()

    if args.command == "add":
        add_entry(args.source, args.value, args.low, args.high, args.date, args.notes)
    elif args.command == "history":
        print_history()
    elif args.command == "dashboard":
        generate_dashboard()
        if args.open:
            webbrowser.open(f"file://{DASHBOARD_HTML.resolve()}")
    else:
        print_status()

if __name__ == "__main__":
    main()
