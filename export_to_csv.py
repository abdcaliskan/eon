import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "bess_data.db")
TRADES_CSV = os.path.join(BASE_DIR, "trades_data.csv")
TELEMETRY_CSV = os.path.join(BASE_DIR, "battery_telemetry.csv")

def export_data():
    if not os.path.exists(DB_NAME):
        print(f"Error: Database file not found ({DB_NAME}).")
        return
        
    conn = sqlite3.connect(DB_NAME)
    
    print("Reading data from database (Turkish/European Regional Settings Compatible)...")
    
    # Export trades_table
    trades_df = pd.read_sql_query("SELECT * FROM trades_table", conn)
    # Using ';' separator and ',' decimal for Turkish/European Power BI compatibility
    trades_df.to_csv(TRADES_CSV, index=False, sep=';', decimal=',', encoding='utf-8-sig')
    print(f"-> Bilateral trades data saved to: {TRADES_CSV} ({len(trades_df)} rows)")
    
    # Export battery_status_table
    telemetry_df = pd.read_sql_query("SELECT * FROM battery_status_table", conn)
    telemetry_df.to_csv(TELEMETRY_CSV, index=False, sep=';', decimal=',', encoding='utf-8-sig')
    print(f"-> Telemetry data saved to: {TELEMETRY_CSV} ({len(telemetry_df)} rows)")
    
    conn.close()
    print("\nAll CSV data files successfully updated for Power BI ingestion!")

if __name__ == "__main__":
    export_data()
