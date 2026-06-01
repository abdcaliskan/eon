import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "bess_data.db")
TRADES_CSV = os.path.join(BASE_DIR, "trades_data.csv")
TELEMETRY_CSV = os.path.join(BASE_DIR, "battery_telemetry.csv")

def export_data():
    if not os.path.exists(DB_NAME):
        print(f"Hata: Veritabanı bulunamadı ({DB_NAME}).")
        return
        
    conn = sqlite3.connect(DB_NAME)
    
    print("Veritabanından veriler okunuyor (Türkçe/Avrupa Bölgesel Ayarlarına Uyumlu)...")
    
    # trades_table verisini çek
    trades_df = pd.read_sql_query("SELECT * FROM trades_table", conn)
    # separator olarak ';' ve ondalık olarak ',' kullanıyoruz.
    trades_df.to_csv(TRADES_CSV, index=False, sep=';', decimal=',', encoding='utf-8-sig')
    print(f"-> İşlem verileri kaydedildi: {TRADES_CSV} ({len(trades_df)} satır)")
    
    # battery_status_table verisini çek
    telemetry_df = pd.read_sql_query("SELECT * FROM battery_status_table", conn)
    telemetry_df.to_csv(TELEMETRY_CSV, index=False, sep=';', decimal=',', encoding='utf-8-sig')
    print(f"-> Telemetri verileri kaydedildi: {TELEMETRY_CSV} ({len(telemetry_df)} satır)")
    
    conn.close()
    print("\nPower BI aktarımı için Türkçe uyumlu CSV dosyaları başarıyla güncellendi!")

if __name__ == "__main__":
    export_data()
