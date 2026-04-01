"""Kartal Gözü - Yardımcı fonksiyonlar.

Tarih hesaplama, veri formatlama ve değer gösterim fonksiyonları.
"""

from datetime import datetime, timedelta
import pandas as pd
from matplotlib.ticker import FuncFormatter


def degerformatla(value, _):
    """Büyük sayıları okunabilir formata dönüştürür (T/B/M/K)."""
    if abs(value) >= 1e12:
        return f'{value / 1e12:.1f}T'
    elif abs(value) >= 1e9:
        return f'{value / 1e9:.1f}B'
    elif abs(value) >= 1e6:
        return f'{value / 1e6:.1f}M'
    elif abs(value) >= 1e3:
        return f'{value / 1e3:.1f}K'
    else:
        return f'{value:.2f}'


formatter = FuncFormatter(degerformatla)


def tarih_formatla(veri, date_format="%d-%m-%Y"):
    """DataFrame'deki 'Tarih' sütununu datetime'a dönüştürür."""
    try:
        veri["Tarih"] = pd.to_datetime(veri["Tarih"], format=date_format).dt.date
    except (ValueError, KeyError):
        pass
    return veri


def yuzde_degisim_formatla(veri):
    """Tarih dışındaki sütunları sayısala dönüştürür ve 3 ondalık basamağa yuvarlar."""
    for col in veri.columns[1:]:
        veri[col] = pd.to_numeric(veri[col], errors='coerce')
        veri[col] = veri[col].round(3)


def tarih_hesapla(yil: int) -> dict:
    """Verilen yıl sayısına göre tarih aralıklarını hesaplar.

    Returns:
        dict: bugun, yilonce, aylik_baslangic anahtarlarıyla tarih stringleri
    """
    bugun_tarih = datetime.now().date()
    bugun = bugun_tarih.strftime("%d-%m-%Y")

    gunluk_baslangic = bugun_tarih - timedelta(days=yil * 365)
    yilonce = gunluk_baslangic.strftime("%d-%m-%Y")

    # Aylık veriler için ~13 ay geriye git (yıllık değişim hesabı için ekstra 1 ay)
    aylik_baslangic = bugun_tarih - timedelta(days=yil * 396)
    aylik = aylik_baslangic.strftime("%d-%m-%Y")

    return {
        "bugun": bugun,
        "yilonce": yilonce,
        "aylik_baslangic": aylik,
    }
