import pandas as pd
import numpy as np

def run_simulation():
    print("====================================================")
    # reBiG: Alm. Dengesizlik Enerjisi Fiyatı ortalaması (Pik saatlerde çok yükselir)
    IMBALANCE_PENALTY_PRICE = 280.0 # EUR/MWh
    
    print(" BESS DENGESİZLİK MALİYETİ (CEZA) SİMÜLASYONU       ")
    print("====================================================")
    print(f"Varsayılan Dengesizlik Fiyatı (reBiG): {IMBALANCE_PENALTY_PRICE} EUR/MWh\n")
    
    # Simüle edilen işlem: Akşam piki satışı
    requested_sell_volume = 25.0 # MWh
    agreed_price = 142.80 # EUR/MWh (Gömülü borsa satış fiyatı)
    
    # Batarya durumu: Tamamen boş (Minimum SoC sınırında)
    available_usable_energy = 0.0 # MWh
    
    # --------------------------------------------------
    # DURUM 1: Agresif Bot (SoC Kontrolü Olmayan)
    # --------------------------------------------------
    # Bot satışı onaylar, ancak fiziksel teslimat yapılamaz.
    # Finansal Sonuç: Borsa satış gelirini alır (+), ancak teslim edemediği miktar için 
    # şebeke operatörüne (TSO) dengesizlik cezası (-) öder.
    gross_revenue_1 = requested_sell_volume * agreed_price
    imbalance_volume_1 = requested_sell_volume - available_usable_energy
    penalty_cost_1 = imbalance_volume_1 * IMBALANCE_PENALTY_PRICE
    net_pnl_1 = gross_revenue_1 - penalty_cost_1
    
    # --------------------------------------------------
    # DURUM 2: Güvenli Bot (Görev 1'de Yazdığımız User Story)
    # --------------------------------------------------
    # Bot bataryanın boş olduğunu görür, satışı borsaya iletmeden engeller (Block).
    # Finansal Sonuç: Satış geliri elde edilmez (0), ancak dengesizlik cezası da oluşmaz (0).
    gross_revenue_2 = 0.0
    imbalance_volume_2 = 0.0
    penalty_cost_2 = 0.0
    net_pnl_2 = 0.0
    
    # --------------------------------------------------
    # Raporlama
    # --------------------------------------------------
    savings = net_pnl_2 - net_pnl_1
    
    print("--- DURUM 1: Agresif Bot (SoC Kontrolü Yok) ---")
    print(f"Borsada Taahhüt Edilen Satış: {requested_sell_volume} MWh")
    print(f"Fiziksel Teslim Edilen Güç : {available_usable_energy} MWh")
    print(f"Olası Borsa Geliri         : +{gross_revenue_1:,.2f} EUR")
    print(f"Dengesizlik Cezası (reBiG) : -{penalty_cost_1:,.2f} EUR")
    print(f"Net Kar/Zarar              : {net_pnl_1:,.2f} EUR")
    if net_pnl_1 < 0:
        print("Sonuç: Kardan çok zarar edildi! Şebeke dengesizliği nedeniyle ceza ödendi.")
    print()
    
    print("--- DURUM 2: Güvenli Bot (Görev 1 - SoC Kontrollü) ---")
    print(f"Borsada Taahhüt Edilen Satış: 0.00 MWh (Bloke edildi)")
    print(f"Fiziksel Teslim Edilen Güç : 0.00 MWh")
    print(f"Dengesizlik Cezası (reBiG) : -0.00 EUR")
    print(f"Net Kar/Zarar              : {net_pnl_2:,.2f} EUR")
    print("Sonuç: Risk sıfırlandı, ceza engellendi.")
    print()
    
    print("====================================================")
    print(f" GÜVENLİ BOTUN SAĞLADIĞI TASARRUF: {savings:,.2f} EUR ")
    print("====================================================")
    print("Açıklama: Yazılım geliştirme ekibine (IT) verdiğimiz User Story")
    print("sayesinde E.ON tek bir işlem hatasından bu cezayı ödemekten kurtulmuştur.")

if __name__ == "__main__":
    run_simulation()
