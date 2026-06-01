import pandas as pd

class BESSFCRSimulator:
    def __init__(self, total_capacity_mwh=100.0, current_soc_mwh=50.0, fcr_commitment_mw=15.0):
        self.total_capacity_mwh = total_capacity_mwh
        self.current_soc_mwh = current_soc_mwh
        self.fcr_commitment_mw = fcr_commitment_mw
        
        # FCR Kuralı: En az 30 dakika boyunca kesintisiz tam güç şarj/deşarj rezervi
        # Gerekli rezerv enerji = 15 MW * 0.5 saat = 7.5 MWh
        self.fcr_energy_reserve_mwh = fcr_commitment_mw * 0.5
        
        # Güvenlik limitleri
        self.hard_min_soc_pct = 10.0  # Fiziksel koruma limiti
        self.hard_max_soc_pct = 100.0
        
        # FCR Kısıtları Altında Çalışma Bandı
        self.fcr_min_soc_mwh = (self.hard_min_soc_pct / 100.0 * total_capacity_mwh) + self.fcr_energy_reserve_mwh
        self.fcr_max_soc_mwh = (self.hard_max_soc_pct / 100.0 * total_capacity_mwh) - self.fcr_energy_reserve_mwh
        
        self.fcr_min_soc_pct = (self.fcr_min_soc_mwh / total_capacity_mwh) * 100.0
        self.fcr_max_soc_pct = (self.fcr_max_soc_mwh / total_capacity_mwh) * 100.0

    def evaluate_trade_order(self, order_id, direction, volume_mwh):
        print(f"\n[INSPECT] Siparis {order_id} Degerlendiriliyor: {direction} | Hacim: {volume_mwh} MWh")
        print(f"Mevcut SoC: {self.current_soc_mwh} MWh ({(self.current_soc_mwh/self.total_capacity_mwh)*100.0:.1f}%)")
        
        if direction == "BUY": # Şarj (SoC Artacak)
            projected_soc_mwh = self.current_soc_mwh + volume_mwh
            
            if projected_soc_mwh <= self.fcr_max_soc_mwh:
                status = "ONAYLANDI"
                reason = "Hedef SoC, FCR üst sınırının altında kalıyor."
                self.current_soc_mwh = projected_soc_mwh
            else:
                available_charge_mwh = max(0.0, self.fcr_max_soc_mwh - self.current_soc_mwh)
                if available_charge_mwh > 0:
                    status = "KISMEN ONAYLANDI (DOWNSCALED)"
                    reason = f"Maksimum FCR şarj rezervine takıldı. Hacim {volume_mwh} MWh -> {available_charge_mwh:.2f} MWh düşürüldü."
                    self.current_soc_mwh = self.fcr_max_soc_mwh
                else:
                    status = "REDDEDİLDİ (BLOCKED)"
                    reason = f"Batarya zaten FCR üst şarj limitinde ({self.fcr_max_soc_pct}%)."
                    
        elif direction == "SELL": # Deşarj (SoC Azalacak)
            projected_soc_mwh = self.current_soc_mwh - volume_mwh
            
            if projected_soc_mwh >= self.fcr_min_soc_mwh:
                status = "ONAYLANDI"
                reason = "Hedef SoC, FCR alt sınırının üstünde kalıyor."
                self.current_soc_mwh = projected_soc_mwh
            else:
                available_discharge_mwh = max(0.0, self.current_soc_mwh - self.fcr_min_soc_mwh)
                if available_discharge_mwh > 0:
                    status = "KISMEN ONAYLANDI (DOWNSCALED)"
                    reason = f"Minimum FCR deşarj rezervine takıldı. Hacim {volume_mwh} MWh -> {available_discharge_mwh:.2f} MWh düşürüldü."
                    self.current_soc_mwh = self.fcr_min_soc_mwh
                else:
                    status = "REDDEDİLDİ (BLOCKED)"
                    reason = f"Batarya zaten FCR alt deşarj limitinde ({self.fcr_min_soc_pct}%)."
                    
        print(f"Durum: {status}")
        print(f"Açıklama: {reason}")
        print(f"İşlem Sonrası Yeni SoC: {self.current_soc_mwh} MWh ({(self.current_soc_mwh/self.total_capacity_mwh)*100.0:.1f}%)")

def main():
    print("====================================================")
    print(" BESS FCR (FREKANS KONTROL REZERVİ) KISIT KONTROLÜ   ")
    print("====================================================")
    
    # 100 MWh kapasiteli bataryada 15 MW FCR taahhüdü var
    # FCR min_SoC = 10% (10 MWh) + 7.5 MWh = 17.5 MWh (%17.5)
    # FCR max_SoC = 100% (100 MWh) - 7.5 MWh = 92.5 MWh (%92.5)
    simulator = BESSFCRSimulator(total_capacity_mwh=100.0, current_soc_mwh=25.0, fcr_commitment_mw=15.0)
    
    print(f"Batarya Toplam Kapasite  : {simulator.total_capacity_mwh} MWh")
    print(f"FCR Taahhüdü             : {simulator.fcr_commitment_mw} MW")
    print(f"FCR İçin Gerekli Rezerv  : {simulator.fcr_energy_reserve_mwh} MWh")
    print(f"Güvenli Ticaret SoC Bandı: %{simulator.fcr_min_soc_pct} - %{simulator.fcr_max_soc_pct}\n")
    
    # Sırasıyla siparişleri simüle et
    # 1. Sipariş: Batarya %25'te iken 30 MWh SELL (Deşarj) - Limit %17.5 (17.5 MWh). Kısmen onaylanmalı
    simulator.evaluate_trade_order("O-001", "SELL", 30.0)
    
    # 2. Sipariş: Batarya alt limitteyken tekrar SELL yapmaya çalışmak - Reddedilmeli
    simulator.evaluate_trade_order("O-002", "SELL", 10.0)
    
    # 3. Sipariş: Bataryayı doldurmak için 50 MWh BUY (Şarj) - Tamamıyla onaylanmalı (Hedef %17.5 + 50 = %67.5 < %92.5)
    simulator.evaluate_trade_order("O-003", "BUY", 50.0)
    
    # 4. Sipariş: Bataryayı aşırı dolduracak 35 MWh BUY - Kısmen onaylanmalı (Sınır %92.5)
    simulator.evaluate_trade_order("O-004", "BUY", 35.0)

if __name__ == "__main__":
    main()
