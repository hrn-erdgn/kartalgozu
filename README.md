# Kartal Gözü

Bu proje, Türkiye Cumhuriyet Merkez Bankası'nın (TCMB) Elektronik Veri Dağıtım Sistemi'nden (EVDS3) makroekonomik verileri çekip, bu verileri anlamlı grafikler haline getiren bir Python uygulamasıdır.

![SS](https://github.com/hrn-erdgn/kartalgozu/blob/main/kartalgozu1.jpg)
![SS](https://github.com/hrn-erdgn/kartalgozu/blob/main/kartalgozu2.jpg)

## Proje Yapısı

| Dosya | Açıklama |
|-------|----------|
| `kartalgozu.py` | Ana giriş noktası (CLI) |
| `config.py` | Tüm EVDS seri kodları ve grafik konfigürasyonları |
| `api.py` | EVDS API bağlantı katmanı (hata yönetimi dahil) |
| `charts.py` | Grafik çizim motoru |
| `utils.py` | Yardımcı fonksiyonlar (tarih, format) |

## Önkoşullar

- Python 3.8+
- TCMB EVDS API anahtarı

## Kurulum

1. Gerekli kütüphaneleri kurun:
```bash
pip install -r requirements.txt
```

2. `.env.example` dosyasını `.env` olarak kopyalayıp API anahtarınızı girin:
```bash
cp .env.example .env
# .env dosyasını düzenleyin: EVDS_API_KEY=sizin_api_anahtariniz
```

3. Uygulamayı çalıştırın:
```bash
python kartalgozu.py
```

## Kullanım

```bash
python kartalgozu.py          # Varsayılan 1 yıllık veri
python kartalgozu.py 3        # Son 3 yıllık veri
python kartalgozu.py 10       # Maksimum 10 yıllık veri
```

## EVDS API Anahtarı Nasıl Alınır

1. [EVDS3](https://evds3.tcmb.gov.tr) sayfasına giriş yapıp bir hesap oluşturun
2. Kullanıcı adınızın altında yer alan profil bağlantısına tıklayın
3. Profil sayfanızın alt kısmında yer alan "API Anahtarı" butonuna tıklayıp değeri kopyalayın

## Gösterilen Veriler

### Pencere 1 (Günlük Veriler)
- Dolar/TL, BIST 100, BIST100 Dolar Bazlı, Toplam Kredi Hacmi ($)
- TCMB Rezervi, APİ Net Fonlama, TL/Dolar Swap, Likidite
- M3 Para Arzı, Yabancı Menkul Kıymet, Kredi Değişimleri
- Faiz Koridoru, Mevduat Faizleri, Kredi Faizleri, TLRef

### Pencere 2 (Aylık Veriler)
- Enflasyon (TÜFE/ÜFE), Konut Fiyat Endeksi, Bütçe Dengesi, İşsizlik
- Reel Kesim Güven Endeksi, Kapasite Kullanım, Tüketici Güven, Carry Trade

## Seri Kodları

Tüm EVDS seri kodları `config.py` dosyasında merkezi olarak tanımlanmıştır. Seri kodu değişikliklerinde sadece bu dosyayı güncellemeniz yeterlidir.

Evds python kütüphanesi için @fatihmete'ye teşekkürler.
