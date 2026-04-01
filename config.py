"""Kartal Gözü - Merkezi konfigürasyon dosyası.

Tüm EVDS seri kodları, grafik düzeni ve sabitler burada tanımlanır.
Seri kodları değiştiğinde sadece bu dosyayı güncellemeniz yeterlidir.
"""

# ============================================================================
# Pencere 1 - Günlük Veriler (4x4 = 16 grafik)
# ============================================================================

# Basit grafikler: fetch → rename → çiz
WINDOW1_SIMPLE = [
    {
        "series": ["TP.DK.USD.A.YTL"],
        "rename": {"TP_DK_USD_A_YTL": "Dolar TL"},
        "position": (0, 0),
        "msg": "Dolar TL Verisi Aliniyor ...",
        "date_type": "daily",
    },
    {
        "series": ["TP.MK.F.BILESIK"],
        "rename": {"TP_MK_F_BILESIK": "BIST 100"},
        "position": (0, 1),
        "msg": "Bist Verisi Aliniyor ...",
        "date_type": "daily",
    },
    {
        "series": ["TP.AB.TOPLAM"],
        "rename": {"TP_AB_TOPLAM": "TCMB Rezervi(Mlyn $)"},
        "position": (1, 0),
        "msg": "Rezerv Verisi Aliniyor ...",
        "date_type": "daily",
    },
    {
        "series": ["TP.APIFON3"],
        "rename": {"TP_APIFON3": "API Net Fonlama"},
        "position": (1, 1),
        "msg": "Acik Piyasa Islemleri Verisi Aliniyor ...",
        "date_type": "daily",
    },
    {
        "series": ["TP.TLDOV01.SWP"],
        "rename": {"TP_TLDOV01_SWP": "TL DOLAR Swap"},
        "position": (1, 2),
        "msg": "Swap Verisi Aliniyor ...",
        "date_type": "daily",
    },
    {
        "series": ["TP.PY.P01.ON", "TP.PY.P02.ON", "TP.PY.P06.ON"],
        "rename": {
            "TP_PY_P01_ON": "Koridor ALT",
            "TP_PY_P02_ON": "Koridor UST",
            "TP_PY_P06_ON": "Gerceklesen",
        },
        "position": (3, 0),
        "msg": "Faiz Koridoru Verisi Aliniyor ...",
        "date_type": "daily",
    },
    {
        "series": ["TP.TRY.MT02", "TP.TRY.MT03", "TP.TRY.MT06"],
        "rename": {
            "TP_TRY_MT02": "32-91 Gun Vadeli Mevduat",
            "TP_TRY_MT03": "92-181 Gun Vadeli Mevduat",
            "TP_TRY_MT06": "Toplam A.O",
        },
        "position": (3, 1),
        "msg": "Mevduat Faizi Verisi Aliniyor ...",
        "date_type": "daily",
    },
    {
        "series": ["TP.KTF18", "TP.KTFTUK01", "TP.KTF101", "TP.KTF11", "TP.KTF12"],
        "rename": {
            "TP_KTF18": "Ticari Krediler",
            "TP_KTFTUK01": "Tuketici Kredisi",
            "TP_KTF101": "Ihtiyac Kredisi",
            "TP_KTF11": "Tasit Kredisi",
            "TP_KTF12": "Konut Kredisi",
        },
        "position": (3, 2),
        "msg": "Kredi Faizi Verisi Aliniyor ...",
        "date_type": "daily",
    },
    {
        "series": ["TP.MKNETHAR.M7", "TP.MKNETHAR.M8"],
        "rename": {
            "TP_MKNETHAR_M7": "Yabancı Hisse Senedi Hareketi",
            "TP_MKNETHAR_M8": "Yabanci DIBS Hareketi",
        },
        "position": (2, 1),
        "msg": "Yabancilarin Menkul Kiymet Hareketleri Verisi Aliniyor ...",
        "date_type": "daily",
    },
    {
        "series": ["TP.PPIBSM", "TP.PPIGBTL"],
        "rename": {
            "TP_PPIBSM": "Bankalar Serbest Mevduatı",
            "TP_PPIGBTL": "Gün Başı Toplam Likidite",
        },
        "position": (1, 3),
        "msg": "Likidite Verileri Aliniyor ...",
        "date_type": "daily",
    },
]

# Hesaplamalı grafikler (özel transform fonksiyonu gerektiren)
# Bu grafikler config-driven döngüyle değil, charts.py'deki özel fonksiyonlarla çizilir.
WINDOW1_CUSTOM_CHARTS = [
    "bist_dolar",         # BIST100 / USD → (0, 2)
    "kredi_hacmi_dolar",  # Toplam Kredi Hacmi / USD → (0, 3)
    "m3_para_arzi",       # M3 yıllıklandırılmış % → (2, 0)
    "kredi_degisim",      # Toplam kredi + Tüketici KK + Konut + Araç → (2, 2), (2, 3)
    "tlref",              # TLRef + Bileşik → (3, 3)
]


# ============================================================================
# Pencere 2 - Aylık Veriler (4x4, şimdilik üst 2 sıra dolu)
# ============================================================================

# Basit aylık grafikler
WINDOW2_SIMPLE = [
    {
        "series": ["TP.TIG08"],
        "rename": {"TP_TIG08": "İşsizlik oranı %"},
        "position": (0, 3),
        "msg": "Issizlik Orani aliniyor...",
        "date_type": "monthly",
        "date_format": "%Y-%m",
    },
]

# Yıllık + Aylık bar grafik birleşimleri
WINDOW2_DUAL_CHARTS = [
    "enflasyon",              # TÜFE/ÜFE yıllık çizgi + aylık bar → (0, 0)
    "konut_fiyat_endeksi",    # KFE yıllık çizgi + aylık bar → (0, 1)
    "butce_dengesi",          # Bütçe dengesi çizgi + gelir/gider bar → (0, 2)
    "reel_kesim_guven",       # Güven endeksi çizgi + aylık bar → (1, 0)
    "imalat_kapasite",        # Kapasite kullanım çizgi + aylık bar → (1, 1)
    "tuketici_guven",         # Tüketici güven çizgi + aylık bar → (1, 2)
    "carry_trade",            # Carry Trade grafiği → (1, 3)
]


# ============================================================================
# EVDS Seri Kodları Referansı
# ============================================================================
# Bu bölüm dokümantasyon amaçlıdır.
#
# Döviz & Piyasa:
#   TP.DK.USD.A.YTL     - USD/TL Döviz Alış Kuru
#   TP.MK.F.BILESIK     - BIST 100 Bileşik Endeksi
#   TP.TLDOV01.SWP      - TL/Dolar Swap
#
# Kredi & Likidite:
#   TP.KREDI.L001        - Toplam Kredi Hacmi (Bin TL)
#   TP.BFTUKKRE.L002     - Tüketici Kredisi ve Kredi Kartları
#   TP.BFTUKKRE.L005     - Konut Kredisi Hacmi
#   TP.BFTUKKRE.L007     - Araç Kredisi Hacmi
#   TP.PPIBSM            - Bankalar Serbest Mevduatı
#   TP.PPIGBTL            - Gün Başı Toplam Likidite
#
# Faiz Oranları:
#   TP.PY.P01.ON         - Faiz Koridoru Alt Band
#   TP.PY.P02.ON         - Faiz Koridoru Üst Band
#   TP.PY.P06.ON         - Gerçekleşen Faiz
#   TP.TRY.MT02          - 32-91 Gün Vadeli Mevduat Faizi
#   TP.TRY.MT03          - 92-181 Gün Vadeli Mevduat Faizi
#   TP.TRY.MT06          - Toplam Ağırlıklı Ortalama
#   TP.KTF18             - Ticari Kredi Faizi
#   TP.KTFTUK01          - Tüketici Kredisi Faizi
#   TP.KTF101            - İhtiyaç Kredisi Faizi
#   TP.KTF11             - Taşıt Kredisi Faizi
#   TP.KTF12             - Konut Kredisi Faizi
#   TP.BISTTLREF.ORAN    - TLRef Faiz Oranı
#
# Parasal Göstergeler:
#   TP.PR.ARZ22          - M3 Para Arzı
#   TP.AB.TOPLAM         - TCMB Toplam Rezerv (Milyon $)
#   TP.APIFON3           - Açık Piyasa İşlemleri Net Fonlama
#
# Enflasyon & Fiyatlar:
#   TP.FG.J0             - TÜFE (Tüketici Fiyat Endeksi)
#   TP.TUFE1YI.T1        - Yİ-ÜFE (Yurt İçi Üretici Fiyat Endeksi)
#   TP.KFE.TR            - Konut Fiyat Endeksi
#
# Bütçe & İstihdam:
#   TP.KB.GEL001         - Bütçe Gelirleri
#   TP.KB.GID001         - Bütçe Giderleri
#   TP.TIG08             - İşsizlik Oranı
#
# Güven Endeksleri:
#   TP.GY1.N2.MA         - Reel Kesim Güven Endeksi (Mevsimsellikten Arındırılmış)
#   TP.KKO.MA            - İmalat Sanayi Kapasite Kullanım Oranı (M.A.)
#   TP.TG2.Y01           - Tüketici Güven Endeksi
#
# Menkul Kıymetler:
#   TP.MKNETHAR.M7       - Yabancı Hisse Senedi Hareketi
#   TP.MKNETHAR.M8       - Yabancı DİBS Hareketi
