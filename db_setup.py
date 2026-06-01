import sqlite3
import datetime
import random
import os

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bess_data.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Create trades_table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades_table (
        trade_id TEXT PRIMARY KEY,
        timestamp TEXT,
        trade_direction TEXT,
        volume_mwh REAL,
        price_eur_per_mwh REAL,
        execution_status TEXT
    )
    """)
    
    # 2. Create battery_status_table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS battery_status_table (
        telemetry_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        power_mw REAL,
        soc_percentage REAL,
        soc_mwh REAL,
        battery_temperature REAL
    )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database tables initialized: {DB_NAME}")

def populate_mock_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Clear tables
    cursor.execute("DELETE FROM trades_table")
    cursor.execute("DELETE FROM battery_status_table")
    
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    
    # --- Populate trades_table ---
    # BUY: Charge at low prices, SELL: Discharge at peak prices
    trades = [
        # Night charging (low prices)
        ("T-001", f"{yesterday}T02:00:00", "BUY", 25.0, 12.50, "COMPLETED"),
        ("T-002", f"{yesterday}T04:00:00", "BUY", 25.0, -8.20, "COMPLETED"),  # Negative price opportunity
        # Morning discharging (peak hours)
        ("T-003", f"{yesterday}T08:00:00", "SELL", 20.0, 95.40, "COMPLETED"),
        # Noon charging (solar peak / cheap price)
        ("T-004", f"{yesterday}T12:00:00", "BUY", 30.0, 15.10, "COMPLETED"),
        # Evening discharging (peak prices)
        ("T-005", f"{yesterday}T19:00:00", "SELL", 25.0, 142.80, "COMPLETED"),
        ("T-006", f"{yesterday}T20:00:00", "SELL", 25.0, 135.00, "COMPLETED")
    ]
    
    cursor.executemany("""
        INSERT INTO trades_table (trade_id, timestamp, trade_direction, volume_mwh, price_eur_per_mwh, execution_status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, trades)
    
    # --- Populate battery_status_table (5-minute telemetry intervals) ---
    # BESS Capacity: 50 MW / 100 MWh
    max_capacity_mwh = 100.0
    current_soc_mwh = 10.0  # Initial SoC at 10%
    
    telemetry_data = []
    
    start_time = datetime.datetime.combine(yesterday, datetime.time.min)
    for step in range(288):  # 24 hours * 12 (5-minute intervals) = 288 periods
        current_time = start_time + datetime.timedelta(minutes=5 * step)
        time_str = current_time.strftime("%Y-%m-%dT%H:%M:%S")
        hour = current_time.hour
        
        # Power profile (power_mw: negative = charge, positive = discharge)
        if 1 <= hour < 3:
            power = -20.0  # MW
        elif 3 <= hour < 5:
            power = -20.0
        elif 7 <= hour < 9:
            power = 20.0
        elif 11 <= hour < 14:
            power = -15.0
        elif 18 <= hour < 21:
            power = 25.0
        else:
            power = 0.0  # Idle
            
        # SoC Calculation: Energy (MWh) = Power (MW) * Time (Hours) -> 5 mins = 1/12 hour
        energy_change = -power * (5.0 / 60.0)
        
        # System losses (95% charge efficiency, 95% discharge efficiency, RTE ~90%)
        if energy_change > 0:
            energy_change *= 0.95  # Charge losses
        elif energy_change < 0:
            energy_change /= 0.95  # Discharge losses
            
        current_soc_mwh = max(10.0, min(max_capacity_mwh, current_soc_mwh + energy_change)) # bounds at 10% to 100%
        soc_pct = (current_soc_mwh / max_capacity_mwh) * 100.0
        
        # Temperature simulation
        temp = 20.0 + (abs(power) * 0.15) + random.uniform(-0.5, 0.5)
        
        telemetry_data.append((time_str, power, soc_pct, current_soc_mwh, temp))
        
    cursor.executemany("""
        INSERT INTO battery_status_table (timestamp, power_mw, soc_percentage, soc_mwh, battery_temperature)
        VALUES (?, ?, ?, ?, ?)
    """, telemetry_data)
    
    conn.commit()
    conn.close()
    print(f"Mock telemetry and trading data successfully added! (Record count: {len(telemetry_data)})")

if __name__ == "__main__":
    init_db()
    populate_mock_data()
