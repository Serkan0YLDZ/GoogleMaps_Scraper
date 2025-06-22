# Google Maps İşletme Veri Çıkarma Projesi - Detaylı Geliştirme Talimatları

## PROJE AMACI VE GENEL ÇALIŞMA MANTĞI

Python ve Selenium kullanarak Google Maps'ten işletme bilgileri ve yorumlarını otomatik olarak çıkaran kapsamlı bir web scraper geliştir. Program `python3 main.py {arama_kelimesi}` komutuyla çalışacak ve aşağıdaki iş akışını takip edecek:

### TEMEL İŞ AKIŞI
1. Google Maps'te arama yap: `https://www.google.com/maps/search/{arama_kelimesi}/?hl=en`
2. Arama sonuçlarını sırayla işle (XPath pattern: div[3], div[5], div[7], div[9]...)
3. Her işletme için: bilgileri al → yorum türünü tespit et → yorumları çıkar → Excel'e kaydet
4. Her 5 işletmeden sonra results navbar'ı scroll et
5. "You've reached the end of the list." görünene kadar devam et

## DETAYLI XPATH VE HTML ELEMANLARI

### Ana Arama Sonuçları Konteyneri
```
XPath: //*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]
```

### Sıralı Arama Sonuçları XPath Pattern'ı
```
1. Sonuç: //*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[3]
2. Sonuç: //*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[5]
3. Sonuç: //*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[7]
4. Sonuç: //*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[9]
```
**PATTERN KURALI**: div[3]'ten başla, her seferinde 2 artır (3,5,7,9,11,13...)

### İşletme Detay Paneli
```
Ana Panel XPath: //*[@id="QA0Szd"]/div/div/div[1]/div[3]
```

### İşletme Bilgileri XPath'leri
```
İşletme Adı: //*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]/h1
Yıldız Puanı: //*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]
```

### Adres ve Telefon HTML Pattern'ları
**ADRES HTML ÖRNEĞİ:**
```html
<button class="CsEnBe" aria-label="Address: 214-44 Hillside Ave., Queens Village, NY 11427, United States " data-item-id="address">
```

**TELEFON HTML ÖRNEĞİ:**
```html
<button class="CsEnBe" aria-label="Phone: +1 718-776-1123 " data-item-id="phone:tel:+17187761123">
```
**ÖNEMLİ**: aria-label içindeki "Address:" ve "Phone:" kelimelerinden sonraki kısmı çıkar.

### Reviews Tab HTML Pattern'ı
```html
<button role="tab" class="hh2c6" aria-label="Reviews for Queens Village Pharmacy" aria-selected="false">
```
**ÖNEMLİ**: aria-label'da "Reviews for" içeren butona tıkla.

## KRİTİK: YORUM TÜRÜ SINIFLANDIRMASI

### TÜR 1: Standart Yorumlar
- Normal yorum bölümü
- Scroll Alanı: `//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]`
- Yorum XPath Pattern'ları:
  ```
  //*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]/div[9]/div[1]
  //*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]/div[9]/div[5]
  //*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]/div[9]/div[9]
  ```

### TÜR 2: Rezervasyon Destekli Yorumlar
- "Book online" özelliği olan işletmeler
- Tespit Kriterleri: Sayfada şu metinler var mı kontrol et:
  - "Browse and book now"
  - "See prices and availability"
  - "Book online"
- Scroll Alanı: `//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[5]`

**KRİTİK KURAL**: Önce Tür 2 kontrolü yap, eğer book online elementleri yoksa Tür 1 olarak işle.

## YORUM VERİSİ ÇIKARMA GEREKSİNİMLERİ

Her yorum için şu bilgileri çıkar:
- **Yorumcu Adı**
- **Yorum Tarihi**
- **Yorum Metni**
- **Yıldız Puanı**
- **Fotoğraf/Medya Linkleri** (varsa)
- **Yorum ID'si** (varsa)

## 🔥🔥🔥 KRİTİK SCROLL STRATEJİSİ VE BELLEK YÖNETİMİ 🔥🔥🔥

### YORUM KAZIMA STRATEJİSİ (EN ÖNEMLİ KISIM)
**ZORUNLU İŞ AKIŞI:**
1. **İşletme açıldığında** → Reviews tab'a git
2. **TAMAMEN EN AŞAĞIYA İN** → Tüm yorumlar yüklenene kadar scroll et
3. **TÜM YORUMLARI TOPLA** → Bellekte geçici olarak sakla
4. **EXCEL'E KAYDET** → Tüm yorumları reviews_data.xlsx'e yaz
5. **RAM'DEN SİL** → Yorum verilerini bellekten tamamen temizle
6. **SONRAKİ İŞLETMEYE GEÇ** → Bir sonraki işletme için döngü tekrarla

### 🚨 RAM TEMİZLEME SAYACI STRATEJİSİ 🚨
**KRİTİK KURAL**: Her 3 işletmenin yorumları RAM'den temizlendikten sonra:
```
İşletme 1: Yorumları kaydet → RAM temizle (Sayaç: 1)
İşletme 2: Yorumları kaydet → RAM temizle (Sayaç: 2) 
İşletme 3: Yorumları kaydet → RAM temizle (Sayaç: 3) → RESULTS SCROLL YAP!
İşletme 4: Yorumları kaydet → RAM temizle (Sayaç: 1)
İşletme 5: Yorumları kaydet → RAM temizle (Sayaç: 2)
İşletme 6: Yorumları kaydet → RAM temizle (Sayaç: 3) → RESULTS SCROLL YAP!
```

### Review Scroll Detaylı Kuralları
**Scroll Stratejisi:**
- **ÖNCE**: Yorum bölümünün sonuna kadar in
- **SCROLL METHODU**: Sürekli scroll et, yeni yorumlar yüklenmeyi durdurduğunda dur
- **TIMEOUT**: 30 saniye timeout, yeni content gelmezse dur
- **VERIFICATION**: Son scroll'dan sonra 2 saniye bekle, yeni content kontrolü yap
- **Scroll alanı türe göre değişir** (Tür 1 vs Tür 2)

### Results Navbar Scroll Kuralları  
**ZORUNLU KURAL**: Her 3 RAM temizleme işleminden sonra results navbar'ı scroll et
- Scroll yönü: Aşağı doğru
- "You've reached the end of the list." metni görünene kadar devam et
- Scroll başarısızsa 3 saniye bekle ve tekrar dene

## 🔥🔥🔥 BELLEK VE VERİ YÖNETİMİ (EN KRİTİK BÖLÜM) 🔥🔥🔥

### Excel Dosya Yapısı
**Dosya 1: business_data.xlsx**
- İşletme adı, adres, telefon, yıldız puanı
- Her 5 işletmede bir kaydet

**Dosya 2: reviews_data.xlsx**
- Tüm yorum verileri
- **ZORUNLU**: Her işletmenin ALL yorumları tamamlandığında HEMEN kaydet

### 🚨 BELLEK YÖNETİMİ ZORUNLU KURALLARI 🚨
1. **MUTLAK ZORUNLU**: Her işletmenin yorumları Excel'e kaydedildikten HEMEN SONRA RAM'den sil
2. **MUTLAK ZORUNLU**: Yorum listesini, dictionary'leri, dataframe'leri bellekten temizle
3. **MUTLAK ZORUNLU**: Python garbage collector'ı manuel çalıştır (gc.collect())
4. **MUTLAK ZORUNLU**: İşletme bilgilerini her 5 işletmede bir kaydet  
5. **MUTLAK ZORUNLU**: Büyük veri yapılarını ASLA gereksiz yere bellekte tutma

### Memory Management Implementation Detayları
```python
# Her işletme sonrası zorunlu temizlik:
save_reviews_to_excel(reviews_data)  # Excel'e kaydet
reviews_data.clear()                 # Listeyi temizle  
del reviews_data                     # Değişkeni sil
gc.collect()                         # Garbage collection
reviews_data = []                    # Yeni boş liste oluştur
```

## HATA YÖNETİMİ GEREKSİNİMLERİ

### Spesifik Hata Türleri
- **Element Bulunamadı**: Element yoksa 3 saniye bekle, tekrar dene
- **Timeout Hataları**: 10 saniye timeout, 3 deneme hakkı
- **Navigate Hataları**: Sayfa yüklenemezse bir sonraki işletmeye geç
- **Scroll Hataları**: Scroll çalışmazsa mevcut veriyi kaydet

### Retry Mekanizması
- **Exponential Backoff**: İlk deneme 1sn, ikinci 2sn, üçüncü 4sn bekle
- **Maksimum Deneme**: Her operasyon için 3 deneme hakkı
- **Graceful Failure**: Bir işletme başarısız olursa diğerini işle

### Hata Loglama
- Tüm hataları timestamp ile logla
- Hangi işletmede hangi adımda hata olduğunu kaydet
- Critical hatalar için terminal'e bilgi ver

## PERFORMANS VE KALİTE GEREKSİNİMLERİ

### Kod Kalitesi Kuralları
1. **Yorum satırı kullanma** - Kod self-documenting olmalı
2. **Modüler tasarım** - Her modül tek sorumluluk
3. **Clean code** - Okunabilir değişken isimleri
4. **DRY prensibi** - Tekrar eden kod olmasın
5. **Error-first approach** - Her operasyonu error handling ile çevrele

### Performans Gereksinimleri
1. **Gereksiz beklemeler olmasın** - Sadece gerekli wait'ler
2. **Efficient selectors** - XPath ve CSS seçiciler optimize
3. **Memory efficient** - Büyük veri yapılarını gereksiz tutma
4. **Resource cleanup** - Browser ve dosya handle'larını kapat

### Terminal Çıktı Formatı
Tüm çıktılar İngilizce olmalı:
```
[INFO] Starting Google Maps scraper for: {search_term}
[INFO] Found {X} search results
[PROCESS] Processing business 1/X: {business_name}
[EXTRACT] Extracting business info...
[CLASSIFY] Review type detected: Type 1
[EXTRACT] Found {X} reviews, scrolling...
[SAVE] Saved {X} reviews to Excel, cleared from memory
[ERROR] Failed to extract address for: {business_name}
[INFO] Completed batch 1-5, scrolling results navbar
[SUCCESS] Scraping completed. Total businesses: {X}
```

## EXECUTION COMMAND
```bash
python3 main.py pharmacy
python3 main.py restaurant
python3 main.py hotel
```

## KRİTİK BAŞARI KRİTERLERİ

### 🔥 ÖNCELIK 1: Tür Sınıflandırması
- %100 doğru Tür 1/Tür 2 detection
- Doğru scroll area seçimi
- Book online elementlerinin güvenilir tespiti

### 🔥🔥🔥 ÖNCELIK 2: SCROLL STRATEJİSİ VE BELLEK YÖNETİMİ (EN KRİTİK)
- **MUTLAK ZORUNLU**: Her işletmede yorumların en sonuna kadar inmek
- **MUTLAK ZORUNLU**: Tüm yorumları topladıktan sonra Excel'e kaydet
- **MUTLAK ZORUNLU**: Excel kaydından HEMEN SONRA RAM'i tamamen temizle
- **MUTLAK ZORUNLU**: Her 3 RAM temizleme sonrası results navbar scroll
- **MUTLAK ZORUNLU**: Memory leak'lerin kesinlikle önlenmesi
- **MUTLAK ZORUNLU**: Python garbage collection manuel çalıştırma

### 🔥🔥🔥 ÖNCELIK 3: RAM TEMİZLEME SAYACI STRATEJİSİ  
- Her işletme = 1 RAM temizleme
- 3 RAM temizleme = 1 results scroll
- Bu döngü "end of list" görünene kadar devam
- Sayaç takibi kesinlikle yapılmalı

### 🔥 ÖNCELIK 4: Hata Dayanıklılığı
- Tek işletme başarısız olsa da devam etmeli
- Network timeout'larını handle etmeli
- Element missing durumlarında graceful degrade

### 🔥 ÖNCELIK 5: Data Integrity
- Eksik veri kayıplarının önlenmesi
- Excel file corruption'ının önlenmesi  
- Duplicate entry'lerin önlenmesi

Bu gereksinimleri karşılayan, production-ready, scalable ve maintainable bir Google Maps scraper geliştir. Kod modüler, hata dayanıklı ve performanslı olmalı.