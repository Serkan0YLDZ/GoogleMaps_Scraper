# Google Maps Scraper

## 📋 Proje Hakkında

Bu proje, Google Maps'ten işletme bilgilerini toplamak için geliştirilmiş bir web scraper'dır. Proje, özellikle Glenridge Pharmacy gibi işletmelerin Google Maps sayfalarından önemli verileri (genel bilgiler, yorumlar, hakkında bilgileri ve navbar verileri) çıkarmaya odaklanmıştır.

## 🎯 Özellikler

- **Genel Bilgi Çıkarma**: İşletme adı, adres, telefon, web sitesi, çalışma saatleri gibi temel bilgileri toplar
- **Yorum Analizi**: Müşteri yorumlarını, değerlendirmelerini ve yanıtları analiz eder
- **Hakkında Bilgileri**: İşletmenin erişilebilirlik, hizmet seçenekleri, ödeme yöntemleri gibi detaylarını toplar
- **Navbar Verilerini**: Sayfanın navigasyon ve menü yapısını analiz eder

## 📁 Proje Yapısı

```
GoogleMaps_Scraper/
├── about.txt          # İşletme hakkında bilgiler (HTML formatında)
├── overview.txt       # İşletmenin genel bilgileri ve ana sayfa içeriği
├── review.txt         # Müşteri yorumları ve değerlendirmeleri
├── result_navbar.txt  # Navbar ve navigasyon verileri
└── README.md          # Bu dosya
```

## 📊 Toplanan Veri Türleri

### 1. Genel Bilgiler (overview.txt)
- **İşletme Adı**: Glenridge Pharmacy
- **Adres**: 6801 Myrtle Ave, Glendale, NY 11385, United States
- **Telefon**: +1 718-366-3561
- **Web Sitesi**: glenridgerx.com
- **Çalışma Saatleri**: Haftalık çalışma programı
- **Değerlendirmeler**: 4.7 yıldız (57 yorum)
- **Kategori**: Eczane
- **Fotoğraflar ve Videolar**: İşletme görselleri

### 2. Hakkında Bilgileri (about.txt)
- **Erişilebilirlik**: Tekerlekli sandalye erişimi
- **İşletme Türü**: Küçük işletme
- **Hizmet Seçenekleri**: 
  - Teslimat
  - Mağazadan teslim alma
  - Mağaza içi alışveriş
  - Yerinde hizmet
  - Aynı gün teslimat
- **Planlama**: Hızlı ziyaret için uygun
- **Ödeme Yöntemleri**: Kredi kartı, banka kartı, NFC mobil ödemeler

### 3. Müşteri Yorumları (review.txt)
- **Detaylı Yorumlar**: Her yorum için tam metin, yıldız sayısı, tarih
- **Yorum Sahibi Bilgileri**: İsim, fotoğraf, toplam yorum sayısı
- **İşletme Yanıtları**: Sahibin müşteri yorumlarına verdiği yanıtlar
- **Etkileşim Verileri**: Beğeni sayıları ve paylaşım seçenekleri

## 🛠️ Teknik Detaylar

### Veri Formatı
- Tüm veriler HTML formatında saklanmıştır
- Google Maps'in orijinal CSS sınıfları ve yapısı korunmuştur
- Zengin metin formatları ve stil bilgileri dahil edilmiştir

### HTML Yapısı
```html
<div class="m6QErb DxyBCb kA9KIf dS8AEf XiKgde">
  <!-- İçerik burada -->
</div>
```

## 📈 Analiz Örnekleri

### Müşteri Memnuniyeti
- **Genel Değerlendirme**: 4.7/5 yıldız
- **Toplam Yorum**: 57 adet
- **Pozitif Geri Bildirimler**: Hızlı servis, dostane personel, temiz mağaza
- **Negatif Geri Bildirimler**: Yeni eczacının kaba davranışı

### Hizmet Analizi
- **En Çok Övülen**: Müşteri hizmeti, hızlı teslimat
- **Rekabet Avantajı**: CVS'ye göre daha iyi hizmet
- **Öne Çıkan Özellikler**: Yerel eczane, kişisel hizmet

## 🚀 Kullanım Alanları

1. **Rekabet Analizi**: Benzer işletmelerle karşılaştırma
2. **Müşteri Deneyimi Analizi**: Geri bildirim analizi
3. **İş Geliştirme**: Hizmet iyileştirme önerileri
4. **Pazarlama Stratejisi**: Güçlü yönlerin vurgulanması
5. **Operasyonel İyileştirme**: Zayıf alanların belirlenmesi

## 📋 Veri Kalitesi

- **Doğruluk**: Google Maps'ten doğrudan alınmış veriler
- **Güncellik**: Scraping zamanına göre güncel bilgiler
- **Bütünlük**: İşletme profili tam olarak kapsamlı
- **Yapısal**: Düzenli HTML formatında organize edilmiş

## ⚠️ Önemli Notlar

1. **Telif Hakkı**: Google Maps verilerinin kullanımında Google'ın hizmet şartlarına uyulmalıdır
2. **Gizlilik**: Kişisel bilgilerin işlenmesinde GDPR ve yerel yasalara uyum sağlanmalıdır
3. **Güncellik**: Veriler scraping zamanından itibaren değişebilir
4. **Kullanım Sınırları**: Ticari kullanım öncesi yasal gereksinimler kontrol edilmelidir

## 🔄 Güncelleme Döngüsü

- **Haftalık**: Yeni yorumlar ve değerlendirmeler
- **Aylık**: İşletme bilgilerinde değişiklikler
- **Mevsimlik**: Çalışma saatleri güncellemeleri
- **Yıllık**: Genel işletme profili revizyonu

## 📞 İletişim

Bu proje hakkında sorularınız için:
- Proje deposu: [GitHub Repository]
- E-posta: [İletişim e-postası]
- Dokümentasyon: Bu README dosyası

---

**Son Güncelleme**: 2024
**Proje Versiyonu**: 1.0
**Durum**: Aktif
