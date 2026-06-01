import sqlite3
import datetime
import random
import os

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bess_data.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. trades_table oluşturma
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
    
    # 2. battery_status_table oluşturma
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
    print(f"Veritabanı tabloları oluşturuldu: {DB_NAME}")

def populate_mock_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabloları temizle
    cursor.execute("DELETE FROM trades_table")
    cursor.execute("DELETE FROM battery_status_table")
    
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    
    # --- trades_table Verisi Ekleme ---
    # BUY: şarj için ucuz fiyatlarla alış, SELL: deşarj için yüksek fiyatlarla satış
    trades = [
        # Gece şarjı (Düşük fiyatlar)
        ("T-001", f"{yesterday}T02:00:00", "BUY", 25.0, 12.50, "COMPLETED"),
        ("T-002", f"{yesterday}T04:00:00", "BUY", 25.0, -8.20, "COMPLETED"),  # Negatif Fiyat fırsatı!
        # Sabah deşarjı (Pik saatler)
        ("T-003", f"{yesterday}T08:00:00", "SELL", 20.0, 95.40, "COMPLETED"),
        # Öğle şarjı (Güneş enerjisi bolluğu / ucuz fiyat)
        ("T-004", f"{yesterday}T12:00:00", "BUY", 30.0, 15.10, "COMPLETED"),
        # Akşam deşarjı (Yüksek akşam piki fiyatları)
        ("T-005", f"{yesterday}T19:00:00", "SELL", 25.0, 142.80, "COMPLETED"),
        ("T-006", f"{yesterday}T20:00:00", "SELL", 25.0, 135.00, "COMPLETED")
    ]
    
    cursor.executemany("""
        INSERT INTO trades_table (trade_id, timestamp, trade_direction, volume_mwh, price_eur_per_mwh, execution_status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, trades)
    
    # --- battery_status_table Verisi Ekleme (5'er dakikalık periyotlarla) ---
    # BESS Kapasitesi: 50 MW / 100 MWh (2 saatlik depolama)
    max_capacity_mwh = 100.0
    current_soc_mwh = 10.0  # Başlangıç doluluğu %10
    
    telemetry_data = []
    
    start_time = datetime.datetime.combine(yesterday, datetime.time.min)
    for step in range(288):  # 24 saat * 12 (5'er dakika) = 288 periyot
        current_time = start_time + datetime.timedelta(minutes=5 * step)
        time_str = current_time.strftime("%Y-%m-%dT%H:%M:%S")
        hour = current_time.hour
        
        # Güç profili (power_mw: negatif = şarj, pozitif = deşarj)
        if 1 <= hour < 3: # Gece şarj 1. etap
            power = -20.0  # MW
        elif 3 <= hour < 5: # Gece şarj 2. etap
            power = -20.0
        elif 7 <= hour < 9: # Sabah deşarj
            power = 20.0
        elif 11 <= hour < 14: # Öğle şarj
            power = -15.0
        elif 18 <= hour < 21: # Akşam deşarj
            power = 25.0
        else:
            power = 0.0  # Idle
            
        # SoC hesaplama: Enerji (MWh) = Güç (MW) * Zaman (Saat) -> 5 dakika = 1/12 saat
        # Güç negatifse şarj (soC artar), pozitifse deşarj (soC azalır)
        energy_change = -power * (5.0 / 60.0)  # power_mw negatif ise + değer verir, pozitif ise - değer verir
        
        # Sistem kayıpları (Şarj verimi %95, deşarj verimi %95, RTE yaklaşık %90)
        if energy_change > 0:
            energy_change *= 0.95  # Şarj verim kaybı
        elif energy_change < 0:
            energy_change /= 0.95  # Deşarj verim kaybı
            
        current_soc_mwh = max(10.0, min(max_capacity_mwh, current_soc_mwh + energy_change)) # min %10, max %100 limitleri
        soc_pct = (current_soc_mwh / max_capacity_mwh) * 100.0
        
        # Sıcaklık simülasyonu
        temp = 20.0 + (abs(power) * 0.15) + random.uniform(-0.5, 0.5)
        
        telemetry_data.append((time_str, power, soc_pct, current_soc_mwh, temp))
        
    cursor.executemany("""
        INSERT INTO battery_status_table (timestamp, power_mw, soc_percentage, soc_mwh, battery_temperature)
        VALUES (?, ?, ?, ?, ?)
    """, telemetry_data)
    
    conn.commit()
    conn.close()
    print(f"Mock telemetri ve işlem verileri başarıyla eklendi! (Kayıt sayısı: {len(telemetry_data)})")

if __name__ == "__main__":
    init_db()
    populate_mock_data()
