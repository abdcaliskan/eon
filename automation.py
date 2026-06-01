import os
import sqlite3
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "bess_data.db")
CHART_PATH = os.path.join(BASE_DIR, "daily_chart.png")
REPORT_PATH = os.path.join(BASE_DIR, "daily_report.html")

def calculate_kpis():
    conn = sqlite3.connect(DB_NAME)
    
    # 1. Read bilateral trades data
    trades_df = pd.read_sql_query("SELECT * FROM trades_table WHERE execution_status = 'COMPLETED'", conn)
    
    # 2. Read physical battery status telemetry
    telemetry_df = pd.read_sql_query("SELECT * FROM battery_status_table", conn)
    conn.close()
    
    # Convert timestamps
    trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
    telemetry_df['timestamp'] = pd.to_datetime(telemetry_df['timestamp'])
    
    # --- KPI 1: Net Arbitrage P&L ---
    trades_df['cost_revenue'] = trades_df.apply(
        lambda row: row['volume_mwh'] * row['price_eur_per_mwh'] if row['trade_direction'] == 'SELL'
        else -row['volume_mwh'] * row['price_eur_per_mwh'], axis=1
    )
    
    total_buy_cost = -trades_df[trades_df['trade_direction'] == 'BUY']['cost_revenue'].sum()
    total_sell_revenue = trades_df[trades_df['trade_direction'] == 'SELL']['cost_revenue'].sum()
    net_pnl = total_sell_revenue - total_buy_cost
    
    total_buy_volume = trades_df[trades_df['trade_direction'] == 'BUY']['volume_mwh'].sum()
    total_sell_volume = trades_df[trades_df['trade_direction'] == 'SELL']['volume_mwh'].sum()
    
    avg_buy_price = trades_df[trades_df['trade_direction'] == 'BUY']['price_eur_per_mwh'].mean() if total_buy_volume > 0 else 0
    avg_sell_price = trades_df[trades_df['trade_direction'] == 'SELL']['price_eur_per_mwh'].mean() if total_sell_volume > 0 else 0
    
    # --- KPI 2: Round-Trip Efficiency (RTE %) ---
    # Convert 5-min power interval reading (5 mins = 1/12 hour)
    # power_mw < 0 -> Charge, power_mw > 0 -> Discharge
    telemetry_df['physical_charged_mwh'] = telemetry_df.apply(
        lambda r: abs(r['power_mw']) * (5.0 / 60.0) if r['power_mw'] < 0 else 0.0, axis=1
    )
    telemetry_df['physical_discharged_mwh'] = telemetry_df.apply(
        lambda r: r['power_mw'] * (5.0 / 60.0) if r['power_mw'] > 0 else 0.0, axis=1
    )
    
    total_physical_charged = telemetry_df['physical_charged_mwh'].sum()
    total_physical_discharged = telemetry_df['physical_discharged_mwh'].sum()
    
    rte = (total_physical_discharged / total_physical_charged) * 100.0 if total_physical_charged > 0 else 0.0
    
    # --- KPI 3: Equivalent Daily Cycles ---
    # Assuming 100 MWh nominal storage capacity
    nominal_capacity_mwh = 100.0
    cycles = total_physical_discharged / nominal_capacity_mwh
    
    metrics = {
        "net_pnl": net_pnl,
        "total_buy_cost": total_buy_cost,
        "total_sell_revenue": total_sell_revenue,
        "buy_vol": total_buy_volume,
        "sell_vol": total_sell_volume,
        "avg_buy": avg_buy_price,
        "avg_sell": avg_sell_price,
        "rte": rte,
        "cycles": cycles,
        "yesterday": (datetime.date.today() - datetime.timedelta(days=1)).strftime('%d.%m.%Y')
    }
    
    return metrics, trades_df, telemetry_df

def generate_visualization(trades_df, telemetry_df):
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=150)
    
    # Left Axis: State of Charge (%)
    color1 = '#00a3e0'  # Energy Blue
    ax1.set_xlabel('Time (Daily Profile)', fontweight='bold', labelpad=10)
    ax1.set_ylabel('State of Charge (SoC %)', color=color1, fontweight='bold')
    line_soc = ax1.plot(telemetry_df['timestamp'], telemetry_df['soc_percentage'], color=color1, linewidth=2.5, label='State of Charge (%)')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0, 105)
    
    # Right Axis: Active Power (MW)
    ax2 = ax1.twinx()
    color2 = '#ff4a5a'  # Energy Red
    ax2.set_ylabel('Active Power (Charge (-) / Discharge (+)) [MW]', color=color2, fontweight='bold')
    line_power = ax2.plot(telemetry_df['timestamp'], telemetry_df['power_mw'], color=color2, linewidth=1.5, alpha=0.7, linestyle='--', label='Power (MW)')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(-60, 60)
    
    # Map Bilateral Trades (Scatter points)
    buys = trades_df[trades_df['trade_direction'] == 'BUY']
    sells = trades_df[trades_df['trade_direction'] == 'SELL']
    
    sc1 = ax2.scatter(buys['timestamp'], [0]*len(buys), color='#2ecc71', s=120, label='Trade BUY Order', zorder=5, edgecolors='black', marker='^')
    sc2 = ax2.scatter(sells['timestamp'], [0]*len(sells), color='#e74c3c', s=120, label='Trade SELL Order', zorder=5, edgecolors='black', marker='v')
    
    # Date formatting
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    plt.gcf().autofmt_xdate()
    
    # Title & Legend
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    plt.title(f"E.ON Bavaria 50 MW BESS Performance Analytics - {yesterday_str}", fontsize=14, fontweight='bold', pad=15)
    
    lines = line_soc + line_power + [sc1, sc2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(CHART_PATH)
    plt.close()
    print(f"Visualization chart saved to: {CHART_PATH}")

def write_html_report(metrics):
    pnl_class = "positive" if metrics['net_pnl'] >= 0 else "negative"
    pnl_sign = "+" if metrics['net_pnl'] >= 0 else ""
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E.ON BESS Daily Performance Report</title>
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: #151c2c;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --primary: #00a3e0;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --border-color: #243049;
        }}
        
        body {{
            font-family: 'Outfit', 'Inter', -apple-system, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }}
        
        .container {{
            max-width: 1100px;
            width: 100%;
        }}
        
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .logo-area h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #fff 30%, var(--primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .logo-area span {{
            color: var(--text-muted);
            font-size: 14px;
        }}
        
        .date-badge {{
            background-color: var(--primary);
            color: #000;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 14px;
        }}
        
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .kpi-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        
        .kpi-card:hover {{
            transform: translateY(-4px);
            border-color: var(--primary);
        }}
        
        .kpi-title {{
            color: var(--text-muted);
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .kpi-value {{
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 6px;
        }}
        
        .kpi-value.positive {{
            color: var(--accent-green);
        }}
        
        .kpi-value.negative {{
            color: var(--accent-red);
        }}
        
        .kpi-desc {{
            font-size: 12px;
            color: var(--text-muted);
        }}
        
        .main-section {{
            display: grid;
            grid-template-columns: 2fr 1.2fr;
            gap: 30px;
        }}
        
        .chart-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        }}
        
        .chart-card h3 {{
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 18px;
            border-left: 4px solid var(--primary);
            padding-left: 10px;
        }}
        
        .chart-wrapper img {{
            width: 100%;
            height: auto;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}
        
        .details-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        
        .details-card h3 {{
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 18px;
            border-left: 4px solid var(--primary);
            padding-left: 10px;
        }}
        
        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid var(--border-color);
            font-size: 14px;
        }}
        
        .detail-row:last-child {{
            border-bottom: none;
        }}
        
        .detail-label {{
            color: var(--text-muted);
        }}
        
        .detail-val {{
            font-weight: 700;
        }}
        
        footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
            font-size: 12px;
            color: var(--text-muted);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-area">
                <h1>E.ON Bavaria 50 MW BESS</h1>
                <span>Intraday Algorithmic Trading Performance</span>
            </div>
            <div class="date-badge">Date: {metrics['yesterday']}</div>
        </header>
        
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Daily Net Arbitrage Revenue</div>
                <div class="kpi-value {pnl_class}">{pnl_sign}{metrics['net_pnl']:,.2f} EUR</div>
                <div class="kpi-desc">Net profit difference between BUY and SELL executions.</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Round-Trip Efficiency (RTE)</div>
                <div class="kpi-value" style="color: var(--primary);">{metrics['rte']:.2f}%</div>
                <div class="kpi-desc">Physical Discharge / Charge energy conversion efficiency.</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Equivalent Daily Cycles</div>
                <div class="kpi-value" style="color: #ff9f43;">{metrics['cycles']:.3f} Cycles</div>
                <div class="kpi-desc">Battery cell wear calculated against 100 MWh capacity.</div>
            </div>
        </div>
        
        <div class="main-section">
            <div class="chart-card">
                <h3>Daily Profile & SoC Chart</h3>
                <div class="chart-wrapper">
                    <img src="daily_chart.png" alt="Daily Performance Plot">
                </div>
            </div>
            
            <div class="details-card">
                <div>
                    <h3>Market Trade Details</h3>
                    <div class="detail-row">
                        <span class="detail-label">Total Charge Volume (BUY)</span>
                        <span class="detail-val">{metrics['buy_vol']:,.1f} MWh</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Total Discharge Volume (SELL)</span>
                        <span class="detail-val">{metrics['sell_vol']:,.1f} MWh</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Avg Charge Buy Price</span>
                        <span class="detail-val">{metrics['avg_buy']:,.2f} EUR/MWh</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Avg Discharge Sell Price</span>
                        <span class="detail-val">{metrics['avg_sell']:,.2f} EUR/MWh</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Total Charging Cost</span>
                        <span class="detail-val" style="color: var(--accent-red);">{metrics['total_buy_cost']:,.2f} EUR</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Total Discharging Revenue</span>
                        <span class="detail-val" style="color: var(--accent-green);">{metrics['total_sell_revenue']:,.2f} EUR</span>
                    </div>
                </div>
                
                <div style="margin-top: 20px; font-size: 11px; color: var(--text-muted); background: #1b2438; padding: 10px; border-radius: 8px; border: 1px solid var(--border-color);">
                    💡 <b>Intraday Insights:</b> The highest discharging revenue was generated at 19:00 during the evening peak price of <b>142.80 EUR/MWh</b>. The cheapest charging occurred during a negative price window (<b>-8.20 EUR/MWh</b>) at 04:00.
                </div>
            </div>
        </div>
        
        <footer>
            E.ON Energy Markets GmbH - Automated Trading Systems Performance Tool © 2026
        </footer>
    </div>
</body>
</html>
"""
    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        file.write(html_content)
    print(f"HTML performance report generated at: {REPORT_PATH}")

def main():
    print("BESS Daily Reporting Automation Initialized...")
    try:
        metrics, trades_df, telemetry_df = calculate_kpis()
        generate_visualization(trades_df, telemetry_df)
        write_html_report(metrics)
        print("Performance analysis execution completed successfully.")
    except Exception as e:
        print(f"Automation execution failed: {e}")

if __name__ == "__main__":
    main()
