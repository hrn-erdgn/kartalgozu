"""Kartal Gözü - EVDS API katmanı.

API anahtarı yönetimi, veri çekme ve hata yönetimi.
"""

import os
import logging

from evds import evdsAPI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def get_evds_client() -> evdsAPI:
    """EVDS API istemcisini oluşturur.

    API anahtarını şu sırayla arar:
    1. EVDS_API_KEY ortam değişkeni
    2. .env dosyası

    Raises:
        ValueError: API anahtarı bulunamazsa
    """
    load_dotenv()
    key = os.environ.get("EVDS_API_KEY")
    if not key:
        raise ValueError(
            "EVDS_API_KEY ortam değişkeni tanımlanmamış!\n"
            "Çözüm: .env dosyasına EVDS_API_KEY=xxx ekleyin veya\n"
            "       export EVDS_API_KEY=xxx komutunu çalıştırın.\n"
            "API anahtarı almak için: https://evds3.tcmb.gov.tr"
        )
    return evdsAPI(key)


def fetch_data(client, series, startdate, enddate, **kwargs):
    """EVDS'den veri çeker. Hata durumunda None döner.

    Args:
        client: evdsAPI istemcisi
        series: Seri kodu listesi
        startdate: Başlangıç tarihi (dd-mm-yyyy)
        enddate: Bitiş tarihi (dd-mm-yyyy)
        **kwargs: formulas, frequency, aggregation_types vb.

    Returns:
        DataFrame veya None (hata durumunda)
    """
    try:
        logger.info(f"Veri alınıyor: {series}")
        return client.get_data(series, startdate=startdate, enddate=enddate, **kwargs)
    except Exception as e:
        logger.error(f"Veri alınamadı ({series}): {e}")
        return None
