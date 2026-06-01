import subprocess
import sys
import os
import webbrowser
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def check_and_install_dependencies():
    """Gerekli kütüphanelerin yüklü olup olmadığını kontrol eder, eksikse yükler."""
    required = {"pandas", "matplotlib"}
    try:
        import pandas
        import matplotlib
        print("Gerekli paketler (pandas, matplotlib) zaten yüklü.")
    except ImportError:
        print("Gerekli kütüphaneler eksik, yükleniyor (pandas, matplotlib)...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "matplotlib"])
            print("Kütüphaneler başarıyla yüklendi.")
        except Exception as e:
            print(f"Kütüphane kurulumunda hata oluştu: {e}")
            print("Lütfen terminalde manuel olarak çalıştırın: pip install pandas matplotlib")
            sys.exit(1)

def main():
    print("====================================================")
    print(" E.ON BESS Otomasyon ve Raporlama Orkestratörü      ")
    print("====================================================")
    
    # 1. Paketleri kontrol et
    check_and_install_dependencies()
    
    # 2. db_setup.py çalıştır
    print("\nAdım 1: Veritabanının Hazırlanması ve Mock Verilerin Yüklenmesi...")
    try:
        db_setup_path = os.path.join(BASE_DIR, "db_setup.py")
        subprocess.check_call([sys.executable, db_setup_path])
        print("-> Veritabanı başarıyla hazırlandı.")
    except Exception as e:
        print(f"Veritabanı kurulum hatası: {e}")
        sys.exit(1)
        
    # 3. automation.py çalıştır
    print("\nAdım 2: Veri Analizinin Yapılması ve Raporların Üretilmesi...")
    try:
        automation_path = os.path.join(BASE_DIR, "automation.py")
        subprocess.check_call([sys.executable, automation_path])
        print("-> Raporlar başarıyla üretildi.")
    except Exception as e:
        print(f"Raporlama hatası: {e}")
        sys.exit(1)
        
    # 4. Raporu tarayıcıda aç
    report_html = os.path.join(BASE_DIR, "daily_report.html")
    if os.path.exists(report_html):
        print(f"\nAdım 3: Sonuçların Tarayıcıda Görüntülenmesi...")
        print(f"Rapor dosyası açılıyor: {report_html}")
        time.sleep(1) # Dosyanın tam yazılması için küçük bir bekleme
        webbrowser.open(f"file:///{report_html.replace('\\', '/')}")
        print("İşlem başarıyla tamamlandı. Tarayıcınızı kontrol edin!")
    else:
        print("\nHata: Rapor dosyası bulunamadı.")
        sys.exit(1)

if __name__ == "__main__":
    main()
