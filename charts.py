"""Kartal Gözü - Grafik çizim motoru.

Tüm matplotlib grafik oluşturma ve veri dönüşüm fonksiyonları.
"""

import logging

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from api import fetch_data
from config import WINDOW1_SIMPLE, WINDOW2_SIMPLE
from utils import (
    degerformatla,
    formatter,
    tarih_formatla,
    yuzde_degisim_formatla,
    tarih_hesapla,
)

matplotlib.use('TkAgg')

logger = logging.getLogger(__name__)


# ============================================================================
# Temel Grafik Fonksiyonları
# ============================================================================

def grafik_ciz(veri, axes, position, date_format="%d-%m-%Y"):
    """Temel çizgi grafiği çizer. Orijinal GrafikCiz fonksiyonunun karşılığı."""
    x, y = position
    ax = axes[x][y]

    veri = tarih_formatla(veri, date_format)
    veri.dropna(axis=1, how="all", inplace=True)
    veri.dropna(inplace=True)
    if "YEARWEEK" in veri.columns:
        veri.drop("YEARWEEK", axis=1, inplace=True, errors='ignore')

    data_cols = veri.columns[1:]
    if len(data_cols) == 0:
        return

    for col in data_cols:
        cizgi, = ax.plot(veri["Tarih"], veri[col], label=col)
        ax.annotate(
            degerformatla(veri[col].iloc[-1], 1),
            xy=(veri["Tarih"].iloc[-1], veri[col].iloc[-1]),
            color=cizgi.get_color(),
            va="center",
        )

    ax.set_xlim(veri["Tarih"].min(), veri["Tarih"].max())
    ax.set_title(str(veri["Tarih"].iloc[-1]))
    ax.legend(loc="upper left")
    ax.grid(alpha=0.8)
    ax.yaxis.set_major_formatter(formatter)
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    ax.tick_params(axis='y', rotation=45, labelsize=6)
    for col in data_cols:
        if (veri[col] < 0).any():
            ax.axhline(0, color='black', ls='--', linewidth=1)
            break


def bar_grafik_ekle(ax_twin, x_range, veri1, veri2, label1, label2,
                    color1='tab:blue', color2='orange', bar_width=0.35,
                    alpha=0.8, fontsize=6):
    """Twin axis üzerinde çift bar grafik çizer (aylık değişim barları)."""
    bars1 = ax_twin.bar(
        [pos - bar_width / 2 for pos in x_range],
        veri1, bar_width, color=color1, alpha=alpha,
    )
    bars2 = ax_twin.bar(
        [pos + bar_width / 2 for pos in x_range],
        veri2, bar_width, color=color2, alpha=alpha,
    )
    ax_twin.bar_label(bars1, fmt='%.1f', padding=1, fontsize=fontsize)
    ax_twin.bar_label(bars2, fmt='%.1f', padding=1, fontsize=fontsize)
    max_val = max(veri1.max(), veri2.max())
    ax_twin.set_ylim(top=max_val * 2)


def tek_bar_grafik_ekle(ax_twin, tarihler, veriler, label, color='tab:blue',
                        alpha=0.4, fmt='%.1f'):
    """Twin axis üzerinde tek bar grafik çizer."""
    bars = ax_twin.bar(tarihler, veriler, color=color, alpha=alpha)
    ax_twin.bar_label(bars, fmt=fmt, alpha=alpha)
    max_val = veriler.max()
    ax_twin.set_ylim(top=max_val * 2)


# ============================================================================
# Basit Grafikleri Çizen Döngü
# ============================================================================

def basit_grafikleri_ciz(client, axes, chart_configs, tarihler, date_key="daily"):
    """Config listesindeki basit grafikleri döngüyle çizer."""
    if date_key == "daily":
        startdate = tarihler["yilonce"]
    else:
        startdate = tarihler["aylik_baslangic"]
    enddate = tarihler["bugun"]

    for cfg in chart_configs:
        logger.info(cfg["msg"])
        data = fetch_data(client, cfg["series"], startdate, enddate)
        if data is None:
            continue
        data.rename(columns=cfg["rename"], inplace=True)

        date_fmt = cfg.get("date_format", "%d-%m-%Y")
        if date_fmt != "%d-%m-%Y":
            data['Tarih'] = pd.to_datetime(data['Tarih'], format=date_fmt, errors='coerce')

        yuzde_degisim_formatla(data)
        grafik_ciz(data, axes, cfg["position"], date_fmt)


# ============================================================================
# Pencere 1 - Özel Hesaplamalı Grafikler
# ============================================================================

def ciz_bist_dolar(client, axes, tarihler):
    """BIST100 $ cinsinden grafiği."""
    data = fetch_data(client, ['TP.MK.F.BILESIK', 'TP.DK.USD.A.YTL'],
                      tarihler["yilonce"], tarihler["bugun"])
    if data is None:
        return
    data["Bist100 $"] = data["TP_MK_F_BILESIK"] / data["TP_DK_USD_A_YTL"]
    data.drop(['TP_MK_F_BILESIK', 'TP_DK_USD_A_YTL'], axis=1, inplace=True, errors='ignore')
    grafik_ciz(data, axes, (0, 2))


def _ciz_kredi_grafik(client, axes, tarihler, series, renames, position, formulas_series=None):
    """Kredi düzey grafiği + yıllık değişim bar overlay.

    Args:
        series: Düzey seri kodları listesi
        renames: Sütun yeniden adlandırma dict'i
        position: (row, col) grafik pozisyonu
        formulas_series: Yıllık değişim için seri kodları (None ise series kullanılır)
    """
    # Düzey çizgi grafiği
    data = fetch_data(client, series, tarihler["yilonce"], tarihler["bugun"])
    if data is None or len(data) == 0:
        return
    data.rename(columns=renames, inplace=True)
    grafik_ciz(data, axes, position)

    # Yıllık değişim bar grafikleri (twinx)
    f_series = formulas_series or series
    formulas_val = [3] * len(f_series)
    yillik = fetch_data(client, f_series, tarihler["yilonce"], tarihler["bugun"],
                        formulas=formulas_val)
    if yillik is None or len(yillik) == 0:
        return

    # Orijinal düzey sütunlarını sil, sadece -3 (yıllık değişim) kalsın
    for col in list(yillik.columns):
        if col != "Tarih" and "-3" not in col and col != "YEARWEEK":
            yillik.drop(col, axis=1, inplace=True, errors='ignore')
    yillik.drop("YEARWEEK", axis=1, inplace=True, errors='ignore')
    yuzde_degisim_formatla(yillik)

    veri_cols = [c for c in yillik.columns if c != "Tarih"]
    if not veri_cols:
        return

    ax_twin = axes[position[0]][position[1]].twinx()
    x = range(len(yillik))
    n = len(veri_cols)
    bar_width = 0.8 / max(n, 1)
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']

    for i, col in enumerate(veri_cols):
        offset = (i - n / 2 + 0.5) * bar_width
        bars = ax_twin.bar([pos + offset for pos in x], yillik[col],
                           bar_width, color=colors[i % len(colors)], alpha=0.4)
        ax_twin.bar_label(bars, fmt='%.0f', fontsize=5, alpha=0.6)

    max_val = yillik[veri_cols].max().max()
    if max_val > 0:
        ax_twin.set_ylim(top=max_val * 2.5)
    axes[position[0]][position[1]].set_xlim(-0.5, len(yillik) - 0.5)


def ciz_para_arzi(client, axes, tarihler):
    """M1/M2/M3 Para Arzı Endeksi yıllık değişim grafiği (haftalık veri)."""
    data = fetch_data(
        client,
        ['TP.KAVRAMSAL.HAMM1.INDX', 'TP.KAVRAMSAL.HAMM2.INDX', 'TP.KAVRAMSAL.HAMM3.INDX'],
        tarihler["yilonce"], tarihler["bugun"],
        formulas=[3, 3, 3],
    )
    if data is None or len(data) == 0:
        return
    for col in list(data.columns):
        if col != "Tarih" and "-3" not in col and col != "YEARWEEK":
            data.drop(col, axis=1, inplace=True, errors='ignore')
    data.drop("YEARWEEK", axis=1, inplace=True, errors='ignore')
    yuzde_degisim_formatla(data)
    data.rename(columns={
        "TP_KAVRAMSAL_HAMM1_INDX-3": "M1 Yıllık Değişim %",
        "TP_KAVRAMSAL_HAMM2_INDX-3": "M2 Yıllık Değişim %",
        "TP_KAVRAMSAL_HAMM3_INDX-3": "M3 Yıllık Değişim %",
    }, inplace=True)
    grafik_ciz(data, axes, (2, 0))


def ciz_toplam_kredi_tl_yp(client, axes, tarihler):
    """TL vs YP Toplam Kredi karşılaştırma + yıllık değişim bar."""
    _ciz_kredi_grafik(
        client, axes, tarihler,
        series=['TP.HPBITABLO2.24', 'TP.HPBITABLO2.28'],
        renames={"TP_HPBITABLO2_24": "TL Toplam Kredi", "TP_HPBITABLO2_28": "YP Toplam Kredi"},
        position=(0, 3),
    )


def ciz_yp_krediler(client, axes, tarihler):
    """YP Krediler düzey + yıllık değişim bar."""
    _ciz_kredi_grafik(
        client, axes, tarihler,
        series=['TP.HPBITABLO2.29', 'TP.HPBITABLO2.30', 'TP.HPBITABLO2.31'],
        renames={
            "TP_HPBITABLO2_29": "YP Tüketici Kredisi",
            "TP_HPBITABLO2_30": "YP Ticari Kredi",
            "TP_HPBITABLO2_31": "YP Diğer Kredi",
        },
        position=(2, 2),
    )


def ciz_tl_krediler(client, axes, tarihler):
    """TL Krediler düzey + yıllık değişim bar."""
    _ciz_kredi_grafik(
        client, axes, tarihler,
        series=['TP.HPBITABLO2.25', 'TP.HPBITABLO2.26', 'TP.HPBITABLO2.27'],
        renames={
            "TP_HPBITABLO2_25": "TL Tüketici Kredisi",
            "TP_HPBITABLO2_26": "TL Ticari Kredi",
            "TP_HPBITABLO2_27": "TL Diğer Kredi",
        },
        position=(2, 3),
    )


def ciz_tlref(client, axes, tarihler):
    """TLRef ve bileşik faiz grafiği."""
    data = fetch_data(client, ["TP.BISTTLREF.ORAN"],
                      tarihler["yilonce"], tarihler["bugun"])
    if data is None:
        return
    data.rename(columns={'TP_BISTTLREF_ORAN': 'TLRef Faizi'}, inplace=True)
    data['TLRef Faizi Bilesik'] = (((data['TLRef Faizi'] * 1 / 36500 + 1) ** (365 / 1)) - 1) * 100
    grafik_ciz(data, axes, (3, 3))


# ============================================================================
# Pencere 2 - Özel Hesaplamalı Grafikler
# ============================================================================

def ciz_enflasyon(client, axes, tarihler):
    """TÜFE/ÜFE yıllık çizgi + aylık bar grafiği."""
    start = tarihler["aylik_baslangic"]
    end = tarihler["bugun"]

    # Yıllık TÜFE
    yillik = fetch_data(client, ["TP.FG.J0"], start, end, formulas=[3])
    if yillik is None:
        return
    yillik.drop(["TP_FG_J0"], axis=1, inplace=True, errors='ignore')
    yuzde_degisim_formatla(yillik)
    yillik.rename(columns={"TP_FG_J0-3": "Yillik TÜFE"}, inplace=True)

    # Yıllık ÜFE
    ufe = fetch_data(client, ['TP.TUFE1YI.T1'], start, end, formulas=[3])
    if ufe is not None:
        ufe.drop(["TP_TUFE1YI_T1"], axis=1, inplace=True, errors='ignore')
        yuzde_degisim_formatla(ufe)
        ufe.rename(columns={"TP_TUFE1YI_T1-3": "Yillik ÜFE"}, inplace=True)
        if "Yillik ÜFE" in ufe.columns:
            yillik["Yillik ÜFE"] = ufe["Yillik ÜFE"]

    grafik_ciz(yillik, axes, (0, 0))
    axes[0][0].set_ylim(bottom=0)

    # Aylık TÜFE barları
    aylik_tufe = fetch_data(client, ["TP.FG.J0"], start, end, formulas=[1])
    if aylik_tufe is None:
        return
    aylik_tufe.drop(["TP_FG_J0"], axis=1, inplace=True, errors='ignore')
    yuzde_degisim_formatla(aylik_tufe)
    aylik_tufe.rename(columns={"TP_FG_J0-1": "Aylik TÜFE"}, inplace=True)

    # Aylık ÜFE barları
    aylik_ufe = fetch_data(client, ['TP.TUFE1YI.T1'], start, end, formulas=[1])
    if aylik_ufe is None:
        return
    aylik_ufe.drop(["TP_TUFE1YI_T1"], axis=1, inplace=True, errors='ignore')
    yuzde_degisim_formatla(aylik_ufe)
    aylik_ufe.rename(columns={"TP_TUFE1YI_T1-1": "Aylik ÜFE"}, inplace=True)

    # TÜFE ve ÜFE farklı satır sayısı döndürebilir, Tarih üzerinden hizala
    aylik = pd.merge(aylik_tufe, aylik_ufe, on="Tarih", how="inner")
    tufe_col = [c for c in aylik.columns if "TÜFE" in c or "tufe" in c.lower()]
    ufe_col = [c for c in aylik.columns if "ÜFE" in c or "ufe" in c.lower()]
    if not tufe_col or not ufe_col:
        return

    ax_twin = axes[0][0].twinx()
    x = range(len(aylik))
    bar_grafik_ekle(ax_twin, x, aylik[tufe_col[0]], aylik[ufe_col[0]],
                    tufe_col[0], ufe_col[0])
    axes[0][0].margins(x=0.1)
    axes[0][0].set_xlim(-0.5, len(aylik) - 0.5)


def ciz_konut_fiyat_endeksi(client, axes, tarihler):
    """Konut Fiyat Endeksi yıllık çizgi + aylık bar grafiği."""
    start = tarihler["aylik_baslangic"]
    end = tarihler["bugun"]

    # Yıllık
    yillik = fetch_data(client, ["TP.KFE.TR"], start, end, formulas=[3])
    if yillik is None:
        return
    yillik.drop(["TP_KFE_TR"], axis=1, inplace=True, errors='ignore')
    yuzde_degisim_formatla(yillik)
    yillik.rename(columns={"TP_KFE_TR-3": "Konut Fiyat Endeksi Yillik Degisim"}, inplace=True)
    grafik_ciz(yillik, axes, (0, 1))
    axes[0][1].set_ylim(bottom=0)

    # Aylık bar
    aylik = fetch_data(client, ["TP.KFE.TR"], start, end, formulas=[1])
    if aylik is None:
        return
    aylik.drop(["TP_KFE_TR"], axis=1, inplace=True, errors='ignore')
    yuzde_degisim_formatla(aylik)
    aylik.rename(columns={"TP_KFE_TR-1": "K.F.E Aylik Değişim"}, inplace=True)

    ax_twin = axes[0][1].twinx()
    bars = ax_twin.bar(aylik['Tarih'], aylik['K.F.E Aylik Değişim'], color='tab:blue', alpha=0.8)
    ax_twin.bar_label(bars, fmt='%.1f')
    ax_twin.set_ylim(top=aylik['K.F.E Aylik Değişim'].max() * 2)
    axes[0][1].set_xlim(-0.5, len(aylik) - 0.5)


def ciz_butce_dengesi(client, axes, tarihler):
    """Bütçe dengesi çizgi + gelir/gider bar grafiği."""
    start = tarihler["aylik_baslangic"]
    end = tarihler["bugun"]

    butce = fetch_data(client, ["TP.KB.GEL001", "TP.KB.GID001"], start, end)
    if butce is None:
        return
    butce.rename(columns={
        "TP_KB_GEL001": "Bütçe Gelirleri",
        "TP_KB_GID001": "Bütçe Giderleri",
    }, inplace=True)
    butce["Bütçe Dengesi"] = butce["Bütçe Gelirleri"] - butce["Bütçe Giderleri"]
    yuzde_degisim_formatla(butce)

    # Denge çizgi grafiği
    butcegrafik = pd.DataFrame()
    butcegrafik["Tarih"] = butce['Tarih']
    butcegrafik["Bütçe Dengesi(Bin TL)"] = butce['Bütçe Dengesi']
    grafik_ciz(butcegrafik, axes, (0, 2))

    # Gelir/gider barları
    bar_width = 0.35
    x = range(len(butce))
    ax_twin = axes[0][2].twinx()
    gelir_bars = ax_twin.bar(
        [pos - bar_width / 2 for pos in x],
        butce['Bütçe Gelirleri'], bar_width, color="tab:green", alpha=0.8,
    )
    gider_bars = ax_twin.bar(
        [pos + bar_width / 2 for pos in x],
        butce['Bütçe Giderleri'], bar_width, color="tab:red", alpha=0.8,
    )
    ax_twin.bar_label(
        gelir_bars,
        labels=[degerformatla(bar.get_height(), '') for bar in gelir_bars],
        fontsize=5, weight='bold', color="green",
    )
    ax_twin.bar_label(
        gider_bars,
        labels=[degerformatla(bar.get_height(), '') for bar in gider_bars],
        fontsize=5, weight='bold', color="red",
    )
    butce_max = max(butce['Bütçe Giderleri'].max(), butce['Bütçe Gelirleri'].max())
    ax_twin.set_ylim(top=butce_max * 2)
    axes[0][2].set_xlim(-0.5, len(butce) - 0.5)


def _ciz_guven_endeksi(client, axes, tarihler, series_code, col_name,
                       renamed_level, renamed_monthly, position):
    """Güven endeksi grafiği çizer (seviye çizgi + aylık değişim bar).

    Reel Kesim, İmalat Kapasite ve Tüketici güven endekslerinin ortak mantığı.
    """
    start = tarihler["aylik_baslangic"]
    end = tarihler["bugun"]

    # Seviye grafiği
    data = fetch_data(client, [series_code], start, end)
    if data is None:
        return
    yuzde_degisim_formatla(data)
    data.rename(columns={col_name: renamed_level}, inplace=True)
    grafik_ciz(data, axes, position)

    # Aylık değişim bar
    aylik = fetch_data(client, [series_code], start, end, formulas=[2])
    if aylik is None:
        return
    aylik.drop([col_name], axis=1, inplace=True, errors='ignore')
    yuzde_degisim_formatla(aylik)
    aylik.rename(columns={f"{col_name}-2": renamed_monthly}, inplace=True)

    ax_twin = axes[position[0]][position[1]].twinx()
    tek_bar_grafik_ekle(ax_twin, aylik['Tarih'], aylik[renamed_monthly], renamed_monthly)
    axes[position[0]][position[1]].set_xlim(-0.5, len(aylik) - 0.5)


def ciz_reel_kesim_guven(client, axes, tarihler):
    """Reel Kesim Güven Endeksi (mevsimsellikten arındırılmış)."""
    logger.info("Reel Kesim Guven Endeksi Mevsimsillikten arindirilmis...")
    _ciz_guven_endeksi(
        client, axes, tarihler,
        series_code="TP.GY1.N2.MA",
        col_name="TP_GY1_N2_MA",
        renamed_level="Reel Kesim Guven Endeksi",
        renamed_monthly="Reel Kesim Guven E. Aylik",
        position=(1, 0),
    )


def ciz_imalat_kapasite(client, axes, tarihler):
    """İmalat Sanayi Kapasite Kullanım Oranı (mevsimsellikten arındırılmış)."""
    logger.info("Imalat Sanayi Kapasite Kullanim Orani Mevsimsellikten Arindirilmis....")
    _ciz_guven_endeksi(
        client, axes, tarihler,
        series_code="TP.KKO.MA",
        col_name="TP_KKO_MA",
        renamed_level="Imalat Sanayi Kapasite Kullanim Orani",
        renamed_monthly="Imalat Sanayi K.K Aylik",
        position=(1, 1),
    )


def ciz_tuketici_guven(client, axes, tarihler):
    """Tüketici Güven Endeksi."""
    logger.info("Tuketici Guven Endeksi Verileri ....")
    _ciz_guven_endeksi(
        client, axes, tarihler,
        series_code="TP.TG2.Y01",
        col_name="TP_TG2_Y01",
        renamed_level="Tuketici Guven Endeksi",
        renamed_monthly="Tuketici Guven Endeksi Aylik",
        position=(1, 2),
    )


def ciz_carry_trade(client, axes, tarihler):
    """Carry Trade grafiği (Dolar TL aylık değişim, Aylık TÜFE, TLRef aylık faiz)."""
    start = tarihler["aylik_baslangic"]
    end = tarihler["bugun"]

    data = fetch_data(client, ["TP.DK.USD.A.YTL", "TP.FG.J0", "TP.BISTTLREF.ORAN"],
                      start, end, formulas=[1, 1, 0])
    if data is None:
        return

    data.rename(columns={
        "TP_DK_USD_A_YTL-1": "Dolar TL Aylik Degisim",
        "TP_FG_J0-1": "Aylik Tufe",
        "TP_BISTTLREF_ORAN": "TLRef Aylik(Faiz)",
    }, inplace=True)
    data['TLRef Aylik(Faiz)'] = (((data['TLRef Aylik(Faiz)'] * 1 / 36500 + 1) ** (365 / 12)) - 1) * 100
    yuzde_degisim_formatla(data)
    data['Tarih'] = pd.to_datetime(data['Tarih'], format='%Y-%m', errors='coerce')
    grafik_ciz(data, axes, (1, 3))


# ============================================================================
# Ana Çizim Fonksiyonu
# ============================================================================

def tum_grafikleri_ciz(client, yil: int):
    """Tüm grafikleri oluşturur ve gösterir."""
    tarihler = tarih_hesapla(yil)

    fig, axes = plt.subplots(4, 4, figsize=(6 * 4, 4 * 3))
    fig2, axes2 = plt.subplots(4, 4, figsize=(6 * 4, 4 * 3))

    # ---- Pencere 1: Basit grafikler ----
    basit_grafikleri_ciz(client, axes, WINDOW1_SIMPLE, tarihler, "daily")

    # ---- Pencere 1: Özel hesaplamalı grafikler ----
    ciz_bist_dolar(client, axes, tarihler)
    ciz_tl_krediler(client, axes, tarihler)
    ciz_para_arzi(client, axes, tarihler)
    ciz_yp_krediler(client, axes, tarihler)
    ciz_toplam_kredi_tl_yp(client, axes, tarihler)
    ciz_tlref(client, axes, tarihler)

    # ---- Pencere 2: Basit grafikler ----
    basit_grafikleri_ciz(client, axes2, WINDOW2_SIMPLE, tarihler, "monthly")

    # ---- Pencere 2: Özel hesaplamalı grafikler ----
    ciz_enflasyon(client, axes2, tarihler)
    ciz_konut_fiyat_endeksi(client, axes2, tarihler)
    ciz_butce_dengesi(client, axes2, tarihler)
    ciz_reel_kesim_guven(client, axes2, tarihler)
    ciz_imalat_kapasite(client, axes2, tarihler)
    ciz_tuketici_guven(client, axes2, tarihler)
    ciz_carry_trade(client, axes2, tarihler)

    # ---- Pencere altlıkları ----
    bugun = tarihler["bugun"]
    for fig_obj in (fig, fig2):
        fig_obj.text(0.5, 0.03, f'Tarih: {bugun}',
                     ha='center', va='center', fontsize=15, color='gray', weight='bold')
        fig_obj.text(0.9, 0.03,
                     'Credits: Harun Erdoğan Github:hrn-erdgn Twitter:harun_erdgn ',
                     ha='center', va='center', fontsize=8, color='gray', alpha=0.7)
        fig_obj.subplots_adjust(left=0.03, right=0.96, top=0.96, hspace=0.45)

    plt.show()
