"""Kartal Gözü - TCMB EVDS Makroekonomik Veri Görselleştirici.

Türkiye Cumhuriyet Merkez Bankası'nın Elektronik Veri Dağıtım Sistemi'nden
(EVDS3) makroekonomik verileri çekip anlamlı grafikler haline getirir.

Kullanım:
    python kartalgozu.py          # Varsayılan 1 yıllık veri
    python kartalgozu.py 3        # Son 3 yıllık veri
    python kartalgozu.py 10       # Maksimum 10 yıllık veri
"""

import sys
import logging

from api import get_evds_client
from charts import tum_grafikleri_ciz


def parse_args() -> int:
    """Komut satırı argümanını parse eder. 1-10 arası yıl değeri döner."""
    if len(sys.argv) <= 1:
        logging.info("Argüman girilmedi. Varsayılan olarak 1 yıllık veriler alınıyor")
        return 1

    try:
        value = int(sys.argv[1])
        if 1 <= value <= 10:
            logging.info(f"Alınan argüman: {value}, {value} yıllık veriler alınıyor")
            return value
        else:
            logging.warning("Hata: Argüman 1 ile 10 arasında bir değer olmalıdır.")
            logging.info("Varsayılan argüman değeri kullanılıyor: 1")
            return 1
    except ValueError:
        logging.warning("Hata: Argüman bir sayı olmalıdır.")
        logging.info("Varsayılan argüman değeri kullanılıyor: 1")
        return 1


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    yil = parse_args()
    client = get_evds_client()
    tum_grafikleri_ciz(client, yil)


if __name__ == "__main__":
    main()
