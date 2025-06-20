# Google Maps Scraper - Teknik Dokümantasyon

## 🏗️ Sistem Mimarisi

### Veri Toplama Süreci

1. **Hedef URL**: Google Maps işletme sayfası
2. **Veri Çıkarma**: HTML DOM yapısından bilgi çıkarma
3. **Veri Saklama**: Metin dosyalarında HTML formatında saklama
4. **Kategorilendirme**: Farklı veri türleri için ayrı dosyalar

### Dosya Yapısı Analizi

#### about.txt
```
Boyut: ~2KB
Format: HTML
İçerik: İşletme özellik verileri
Kodlama: UTF-8
```

**Ana Bileşenler:**
- Erişilebilirlik bilgileri
- İşletme kategorisi (Small Business)
- Hizmet seçenekleri
- Planlama bilgileri
- Ödeme yöntemleri

#### overview.txt
```
Boyut: ~50KB+
Format: HTML
İçerik: Ana sayfa tam içeriği
Kodlama: UTF-8
```

**Ana Bileşenler:**
- İşletme başlığı ve fotoğraflar
- İletişim bilgileri
- Çalışma saatleri tablosu
- Eylem butonları (Directions, Save, Share)
- Değerlendirme özeti
- Fotoğraf galerisi
- Web sonuçları

#### review.txt
```
Boyut: ~25KB+
Format: HTML
İçerik: Müşteri yorumları
Kodlama: UTF-8
```

**Ana Bileşenler:**
- Yorum sahibi profil bilgileri
- Yıldız değerlendirmeleri
- Yorum metinleri
- Tarih bilgileri
- İşletme yanıtları
- Beğeni/paylaşım butonları

#### result_navbar.txt
```
Boyut: Minimal
Format: Metin
İçerik: Dosya yolu referansı
```

## 🔍 HTML Yapısı Analizi

### CSS Sınıfları

#### Ana Konteyner Sınıfları
```css
.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde
```
- Google Maps ana içerik konteyneri
- Responsive tasarım desteği
- Standart padding ve margin değerleri

#### Yorum Yapısı
```css
.jftiEf.fontBodyMedium
```
- Ana yorum konteyneri
- Orta boy font kullanımı
- Mobil uyumlu tasarım

#### Değerlendirme Yapısı
```css
.kvMYJc[role="img"][aria-label="5 stars"]
```
- Yıldız değerlendirme gösterimi
- Erişilebilirlik desteği
- ARIA etiketleri

### Veri Çıkarma Stratejileri

#### 1. İletişim Bilgileri
```html
<div class="Io6YTe fontBodyMedium kR99db fdkmkc">
  6801 Myrtle Ave, Glendale, NY 11385, United States
</div>
```

#### 2. Çalışma Saatleri
```html
<table class="eK4R0e fontBodyMedium">
  <tr class="y0skZc">
    <td class="ylH6lf fontTitleSmall">Friday</td>
    <td class="mxowUb">10 AM–7:30 PM</td>
  </tr>
</table>
```

#### 3. Değerlendirmeler
```html
<span class="kvMYJc" role="img" aria-label="5 stars">
  <span class="hCCjke google-symbols NhBTye elGi1d">★</span>
</span>
```

## 📊 Veri Modeli

### İşletme Profili
```json
{
  "name": "Glenridge Pharmacy",
  "address": "6801 Myrtle Ave, Glendale, NY 11385, United States",
  "phone": "+1 718-366-3561",
  "website": "glenridgerx.com",
  "rating": 4.7,
  "review_count": 57,
  "category": "Pharmacy",
  "business_hours": {
    "monday": "10 AM–7:30 PM",
    "tuesday": "10 AM–7:30 PM",
    "wednesday": "10 AM–7:30 PM",
    "thursday": "10 AM–7:30 PM",
    "friday": "10 AM–7:30 PM",
    "saturday": "10 AM–6 PM",
    "sunday": "Closed"
  }
}
```

### Yorum Yapısı
```json
{
  "reviewer": {
    "name": "Diana Martinez",
    "review_count": 7,
    "profile_image": "https://lh3.googleusercontent.com/..."
  },
  "rating": 5,
  "date": "3 months ago",
  "text": "I switched from CVS a few years ago and it was for the best...",
  "likes": 0,
  "business_response": null
}
```

## 🛠️ Geliştirme Önerileri

### 1. Veri Ayrıştırma Scripti
```python
import re
from bs4 import BeautifulSoup

def parse_business_info(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # İşletme adını çıkar
    name = soup.find('h1', class_='DUwDvf lfPIob')
    
    # Adres bilgisini çıkar
    address = soup.find('div', class_='Io6YTe fontBodyMedium kR99db fdkmkc')
    
    # Telefon numarasını çıkar
    phone = soup.find('div', class_='Io6YTe fontBodyMedium kR99db fdkmkc')
    
    return {
        'name': name.text.strip() if name else None,
        'address': address.text.strip() if address else None,
        'phone': phone.text.strip() if phone else None
    }
```

### 2. Yorum Analizi Scripti
```python
def extract_reviews(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    reviews = []
    
    for review_div in soup.find_all('div', class_='jftiEf fontBodyMedium'):
        reviewer_name = review_div.find('div', class_='d4r55')
        rating = len(review_div.find_all('span', class_='hCCjke google-symbols NhBTye elGi1d'))
        review_text = review_div.find('span', class_='wiI7pd')
        
        if reviewer_name and review_text:
            reviews.append({
                'reviewer': reviewer_name.text.strip(),
                'rating': rating,
                'text': review_text.text.strip()
            })
    
    return reviews
```

### 3. Veri Doğrulama
```python
def validate_business_data(data):
    required_fields = ['name', 'address', 'phone']
    
    for field in required_fields:
        if not data.get(field):
            print(f"Eksik alan: {field}")
            return False
    
    # Telefon numarası formatını kontrol et
    phone_pattern = r'^\+?1?\s?\(?[0-9]{3}\)?\s?[0-9]{3}\s?[0-9]{4}$'
    if not re.match(phone_pattern, data['phone']):
        print("Geçersiz telefon numarası formatı")
        return False
    
    return True
```

## 🔧 Performans Optimizasyonu

### 1. Dosya Boyutu Yönetimi
- HTML minification uygulanabilir
- Gereksiz CSS sınıfları kaldırılabilir
- Veri sıkıştırma teknikleri kullanılabilir

### 2. Veri İşleme Hızı
- BeautifulSoup yerine lxml parser kullanılabilir
- Paralel işleme teknikleri uygulanabilir
- Çoklu thread yapısı kurulabilir

### 3. Bellek Kullanımı
- Stream processing teknikleri
- Chunk-based veri okuma
- Garbage collection optimizasyonu

## 🚨 Hata Yönetimi

### Yaygın Hatalar
1. **HTML Yapısı Değişiklikleri**: Google Maps arayüzü güncellendiğinde
2. **Rate Limiting**: Çok fazla istek gönderildiğinde
3. **JavaScript Bağımlılıkları**: Dinamik içerik yüklenemediğinde
4. **CAPTCHA**: Bot detection sistemleri devreye girdiğinde

### Hata Çözümleri
```python
import time
import random

def robust_scraper(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Scraping işlemi
            result = scrape_page(url)
            return result
        except Exception as e:
            print(f"Hata (deneme {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                # Rastgele bekleme süresi
                time.sleep(random.uniform(1, 5))
            else:
                raise e
```

## 📝 Lisans ve Etik Kullanım

### Google ToS Uyumluluğu
- robots.txt dosyasına uyum
- Rate limiting uygulama
- Ticari kullanım sınırlamaları

### Veri Gizliliği
- Kişisel bilgilerin anonimleştirilmesi
- GDPR uyumluluğu
- Veri saklama süresi sınırlamaları

---

**Teknik Dokümentasyon Versiyonu**: 1.0
**Son Güncelleme**: 2024
**Yazarlar**: Geliştirici Ekibi
