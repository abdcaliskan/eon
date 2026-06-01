# E.ON Energy Markets - Short-Term Trading & BESS 101
## Mülakat ve Sektör Hazırlık Rehberi (Working Student Short-Term Trading)

Bu rehber, **E.ON Energy Markets GmbH (EEM)** bünyesindeki **Working Student Short-Term Trading** rolünün mülakatlarında seni en üst sıraya taşıyacak sektörel bilgileri, teknik tanımları ve hazırladığımız simülasyonları içeren kapsamlı bir kılavuzdur.

---

## Bölüm 1: E.ON Energy Markets (EEM) ve Rolün Amacı

**E.ON Energy Markets (EEM)**, E.ON Grubu'nun Essen ve Münih merkezli enerji ticaret koludur. Temel amacı, E.ON'un bölgesel operasyonel birimlerinin (Regional Business Units) enerji piyasalarına erişimini koordine etmek, portföy risklerini yönetmek ve esnek varlıkları (BESS vb.) optimize etmektir.

### 🏃 Bir Playmaker Olarak Sorumluluğun:
Bu rolde **ST Flex (Short-Term Flexibility) ve Algoritmik Trading** ekibinin bir parçası olacaksın. Temel görevin:
*   Batarya Enerji Depolama Sistemleri'nin (BESS) ve diğer esnek varlıkların kısa vadeli elektrik piyasalarına (Day-Ahead, Intraday, Balancing) entegrasyonuna destek olmak.
*   Trading operasyonlarında veri akışlarını otomatikleştirmek, performans raporları hazırlamak (Power BI/Python/SQL) ve IT ile trading masası arasında köprü olmaktır (User Story yazmak).

---

## Bölüm 2: Almanya Kısa Vadeli Elektrik Piyasaları 101

Almanya enerji piyasası, BESS entegrasyonu için Avrupa'nın en gelişmiş ve dinamik piyasasıdır. Ticaret 3 ana vadede döner:

| Piyasa Türü | Ticaret Zamanı | Sözleşme Tipleri | BESS İçin Önemi |
| :--- | :--- | :--- | :--- |
| **Day-Ahead Market (EPEX SPOT)** | Teslimat gününden bir önceki gün saat **12:00 (CET)**'de kapanan açık artırma (auction). | Saatlik veya Blok elektrik sözleşmeleri. | Günlük baz yük şarj/deşarj planını (base schedule) belirlemek için kullanılır. |
| **Intraday Market (EPEX SPOT)** | Kesintisiz (continuous) olarak teslimat saatinden **5 ila 30 dakika** öncesine kadar işlem yapılabilir. | Saatlik veya 15 Dakikalık (Quarter-hourly) sözleşmeler. | **Arbitraj Fırsatı:** Rüzgar/Güneş dalgalanmalarına göre fiyatlar anlık değişir (negatif fiyatlar oluşur). Batarya hızlı tepkiyle kar marjını büyütür. |
| **Balancing Markets (Dengeleme/Yedek Güç)** | TSO'lar (Şebeke Operatörleri: TenneT, Amprion vb.) şebeke frekansını (50 Hz) korumak için satın alır. | FCR (Saniyelik tepki), aFRR (Dakikalık tepki). | **Kapasite Ödemesi:** Batarya şebekeye bağlı kalıp beklediği (rezerv ayırdığı) her saat için ödeme alır. |

---

## Bölüm 3: BESS (Batarya Depolama) Teknik Terimleri & Metrikleri

Mülakatta bu terimleri profesyonelce kullanman seni doğrudan kıdemli bir aday gibi gösterecektir:

*   **State of Charge (SoC - Doluluk Oranı %):** Bataryanın o anki enerji seviyesidir. Fiziksel ömrü korumak için genelde %10 (SoC_min) ile %100 (SoC_max) arasında çalıştırılır.
*   **Round-Trip Efficiency (RTE - Gidiş-Dönüş Verimliliği %):** Şebekeden çekilen şarj enerjisinin ne kadarının deşarj edilerek şebekeye geri verilebildiğidir. Lityum-iyon piller için bu oran **%85 - %90** civarındadır (kalan %10-15 ısı ve dönüştürücü kaybıdır).
*   **Equivalent Cycles (Eşdeğer Döngü Sayısı):** Bataryanın yıpranma (degradasyon) ölçüsüdür. Bataryanın kapasitesi kadar deşarj yapılması 1 döngü sayılır. Günlük döngü bütçesi aşılırsa batarya garantisi zarar görür.
*   **Ausgleichsenergie (Dengesizlik Cezası):** Satış taahhüdü verilip fiziksel olarak elektrik teslim edilmediğinde ödenen cezadır. Almanya şebeke operatörleri (TSO), bu açığı kapatmak için **reBiG** (dengesizlik fiyatı) üzerinden E.ON'a ceza keser.

---

## Bölüm 4: Mülakatta Karşılaşabileceğin Sorular ve "Simülasyon" Referanslı Cevaplar

### Soru 1: Bir BESS projesinde trader'lar ile IT/Geliştirici ekibi arasındaki en büyük operasyonel risklerden biri nedir ve bunu nasıl çözersin?
> **Yanıt:** En büyük risklerden biri trading botunun agresif çalışarak fiziksel sınırları (bataryanın boş olması gibi) göz ardı etmesi ve E.ON'a dengesizlik cezası (Ausgleichsenergie) ödetmesidir.
> 
> *Çözüm olarak:* IT ekibinin anlayacağı dilde net Gherkin kabul kriterlerine sahip bir **User Story** hazırlarım. Piyasaya satış emri iletilmeden önce sistemin telemetri verilerinden anlık **State of Charge (SoC)** bilgisini sorgulamasını ve yeterli enerji yoksa emri bloklamasını sağlayan bir fail-safe mekanizması kurgularım.
> *(Referans: Projemizdeki [db_setup.py](file:///c:/Users/abdul/OneDrive/Desktop/BESS_Trading_Automation/db_setup.py) ve [automation.py](file:///c:/Users/abdul/OneDrive/Desktop/BESS_Trading_Automation/automation.py) kodları).*

### Soru 2: Algo botun SoC kontrolü yapmaması E.ON'a finansal olarak nasıl yansır? Bir simülasyon yaptın mı?
> **Yanıt:** Evet, bunu simüle eden bir çalışma yaptım. Örneğin, 25 MWh'lik bir akşam piki satış emrinde batarya boşsa ve bot SoC kontrolü yapmadan bu emri borsaya gönderirse:
> *   Bot borsa fiyatı üzerinden (örn. 142.80 EUR/MWh) satış geliri taahhüt eder.
> *   Ancak teslimat yapılamadığı için şebeke operatörü ortalama 280 EUR/MWh reBiG fiyatından **dengesizlik cezası** keser.
> *   Sonuçta **-3,430 EUR** net zarar oluşur. SoC doğrulaması yapan güvenli bot ise bu siparişi bloke ederek E.ON'u bu zarardan kurtarır.
> *(Referans: Yazdığımız [imbalance_simulation.py](file:///c:/Users/abdul/OneDrive/Desktop/BESS_Trading_Automation/imbalance_simulation.py) betiği).*

### Soru 3: Bataryayı hem spot piyasada (Intraday) arbitraj için koşturup hem de frekans dengeleme (FCR) hizmetine soktuğumuzda trading botu nasıl kısıtlamalıyız?
> **Yanıt:** FCR (Frequency Containment Reserve) çift yönlü simetrik bir hizmettir. Yani şebeke frekansı düştüğünde deşarj, yükseldiğinde ise şarj olmaya hazır olmalıyız. TSO kurallarına göre en az 30 dakika boyunca taahhüt ettiğimiz FCR gücünü (örn. 15 MW) verebilecek enerji rezervini korumalıyız (15 MW * 0.5h = 7.5 MWh).
> 
> Bu durum trading botunun hareket alanını kısıtlar:
> *   Batarya kapasitesi 100 MWh ise, botun ticaret yapabileceği güvenli SoC bandı **%17.5 ile %92.5** arasına sıkışır.
> *   Bu limitleri aşan şarj (BUY) veya deşarj (SELL) emirleri trading sistemi tarafından ya tamamen engellenmeli ya da limit sınırına kadar ölçeklendirilmelidir (downscaled).
> *(Referans: Yazdığımız [fcr_constraints.py](file:///c:/Users/abdul/OneDrive/Desktop/BESS_Trading_Automation/fcr_constraints.py) betiği).*

### Soru 4: Süreç otomasyonu (Process Automation) ve Raporlama konusunda ne tür deneyimlerin var?
> **Yanıt:** Excel/CSV üzerinden yapılan manuel raporlama süreçlerini otomatikleştirecek Python mimarileri tasarlıyorum. SQLite veri tabanından telemetri ve işlem verilerini SQL sorgularıyla Pandas ortamına çekip; Net P&L, RTE% ve Döngü Sayısı gibi KPI'ları otomatik hesaplayan, Matplotlib ile şarj profil grafiklerini üreten ve bunu modern bir HTML raporuna dökerek otomatik e-posta gönderimini tetikleyen uçtan uca orkestratör betikleri kurguladım.
> *(Referans: Yazdığımız [run_automation.py](file:///c:/Users/abdul/OneDrive/Desktop/BESS_Trading_Automation/run_automation.py) betiği).*

---
*Bu rehber ve beraberindeki Python simülasyonları, mülakat sırasında E.ON trading ekiplerine teknik ve piyasa hakimiyetini doğrudan kanıtlayacaktır.*
