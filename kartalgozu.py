from evds import evdsAPI
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.style as style
import pandas as pd
from matplotlib.dates import AutoDateLocator, AutoDateFormatter
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import time
import matplotlib
import sys




####################################################################################
evds = evdsAPI('Beni_Sil_Api_Key_Yaz') #<<<<<< API KEY  Tırnakların içine GIRILECEK#
####################################################################################


# Varsayılan argüman değeri
arg_value = 1

# Komut satırından argüman alın. Eğer argüman verilmezse, varsayılan değeri kullan.
if len(sys.argv) > 1:
    try:
        # İlk argümanı int'e çevir ve kontrol et
        arg_value = int(sys.argv[1])
        if 1 <= arg_value <= 10:
            print(f"Alınan argüman: {arg_value}, {arg_value} yıllık veriler alınıyor")
        else:
            print("Hata: Argüman 1 ile 10 arasında bir değer olmalıdır.")
            print(f"Varsayılan argüman değeri kullanılıyor: {arg_value}")
    except ValueError:
        print("Hata: Argüman bir sayı olmalıdır.")
        print(f"Varsayılan argüman değeri kullanılıyor: 1")
else:
    print(f"Argüman girilmedi. Varsayılan olarak yıllık veriler alınıyor")



print(matplotlib.get_backend())

matplotlib.use('TkAgg')

#plt.style.use('Solarize_Light2')


gunler = arg_value * 365


bugun_tarih = datetime.now().date()
bugun = bugun_tarih.strftime("%d-%m-%Y")
yilonce_tarih = bugun_tarih - timedelta(days=gunler)
yilonce = yilonce_tarih.strftime("%d-%m-%Y")
ikiyilonce_tarih = bugun_tarih - timedelta(days=730)
ikiyilonce = ikiyilonce_tarih.strftime("%d-%m-%Y")
ucayonce_tarih = bugun_tarih - timedelta(days=90)
ucayonce = ucayonce_tarih.strftime("%d-%m-%Y")


fig, axes = plt.subplots(4,4,figsize=(6*4,4*3))

#fig.canvas.set_window_title('KartalGozu V1.0')
    
def degerformatla(value, _):
	if abs(value) >= 1e12:
		return f'{value / 1e12:.0f}T'
	elif abs(value) >= 1e9:
		return f'{value / 1e9:.0f}B'
	elif abs(value) >= 1e6:
		return f'{value / 1e6:.0f}M'
	else:
		return f'{value:.0f}'


formatter = FuncFormatter(degerformatla)


def TarihFormatla(veri):
	try:
		veri["Tarih"] = pd.to_datetime(veri["Tarih"], format="%d-%m-%Y").dt.date
		return veri
	except:
		pass





def Yuzdedegisimformatla(veri):
	for tur in veri.columns[1:]:
		veri[tur]= pd.to_numeric(veri[tur], errors='coerce')
		veri[tur] = veri[tur].round(3)



def GrafikCiz(veri, x, y):
	veri = TarihFormatla(veri)
	veri.dropna(axis=1,how="all",inplace=True)
	veri.dropna( inplace=True)
	if "YEARWEEK" in veri.columns:
		veri.drop("YEARWEEK",axis=1,inplace=True)
	for tur in veri.columns[1:]:
		cizgi, = axes[x][y].plot(veri["Tarih"], veri[tur],label=tur)
		axes[x][y].annotate(veri[tur].iloc[-1], xy=(veri["Tarih"].iloc[-1], veri[tur].iloc[-1]), color=cizgi.get_color(), va="center")
	axes[x][y].set_xlim(veri["Tarih"].min(), veri["Tarih"].max())
	axes[x][y].set_title(str(veri["Tarih"].iloc[-1]))
	axes[x][y].legend(loc="upper left")
	axes[x][y].grid(alpha=0.5)
	axes[x][y].yaxis.set_major_formatter(formatter)
	axes[x][y].tick_params(axis='x', rotation=45, labelsize=8)
	if(veri[tur]<0).any():
		axes[x][y].axhline(0, color='black', ls='--', linewidth=1)






#============================================== Dolar TL ============================================================================
print("Dolar TL Verisi Aliniyor ...")
datadolartl = evds.get_data(['TP.DK.USD.A.YTL'], startdate=yilonce, enddate=bugun)
datadolartl.rename(columns={'TP_DK_USD_A_YTL':'Dolar TL'},inplace=True)
GrafikCiz(datadolartl,0,0)


print("Bist Verisi Aliniyor ...")
bist = evds.get_data(['TP.MK.F.BILESIK'], startdate=yilonce, enddate=bugun)
bist.rename(columns={'TP_MK_F_BILESIK':'BIST 100'},inplace=True)
GrafikCiz(bist,0,1)


bistdolar = evds.get_data(['TP.MK.F.BILESIK', 'TP.DK.USD.A.YTL'], startdate=yilonce, enddate=bugun)
bistdolar["Bist100 $"] = bistdolar["TP_MK_F_BILESIK"] / bistdolar["TP_DK_USD_A_YTL"]
bistdolar.drop(['TP_MK_F_BILESIK','TP_DK_USD_A_YTL'], axis=1, inplace=True)
GrafikCiz(bistdolar,0,2)



print("Toplam Kredi Hacmi Verisi Aliniyor ...")
kredihacmidolar = evds.get_data(['TP.KREDI.L001','TP.DK.USD.A.YTL'], startdate=yilonce, enddate=bugun)
kredihacmidolar["Toplam Kredi Hacmi $"] = kredihacmidolar["TP_KREDI_L001"] / kredihacmidolar["TP_DK_USD_A_YTL"]
kredihacmidolar.drop(['TP_KREDI_L001','TP_DK_USD_A_YTL'], axis=1, inplace=True)
GrafikCiz(kredihacmidolar,0,3)


print("Rezerv Verisi Aliniyor ...")
rezerv = evds.get_data(['TP.AB.A02','TP.AB.A10','TP.DK.USD.A.YTL'], startdate=yilonce, enddate=bugun)
rezerv["Brüt TCMB Dolar Rezervi"] = (rezerv["TP_AB_A02"] - rezerv["TP_AB_A10"]) / rezerv["TP_DK_USD_A_YTL"]
rezerv.drop(["TP_AB_A02","TP_AB_A10","TP_DK_USD_A_YTL"], axis=1, inplace=True)
GrafikCiz(rezerv,1,0)





print("Acik Piyasa Islemleri Verisi Aliniyor ...")
tcmbnetfonlama = evds.get_data(['TP.APIFON3'], startdate=yilonce, enddate=bugun)
tcmbnetfonlama.rename(columns={'TP_APIFON3':'API Net Fonlama'},inplace=True)
GrafikCiz(tcmbnetfonlama,1,1)

print("Swap Verisi Aliniyor ...")
bankaswap = evds.get_data(['TP.TLDOV01.SWP'], startdate=yilonce, enddate=bugun)
bankaswap.rename(columns={'TP_TLDOV01_SWP':'TL DOLAR Swap'},inplace=True)
GrafikCiz(bankaswap,1,2)





print("Faiz Koridoru Verisi Aliniyor ...")
apioranlari = yabancidegisim = evds.get_data(["TP.PY.P01.ON", "TP.PY.P02.ON", "TP.PY.P06.ON"], startdate=yilonce, enddate=bugun)
apioranlari.rename(columns={'TP_PY_P01_ON':'Koridor ALT', 'TP_PY_P02_ON':'Koridor UST', 'TP_PY_P06_ON':'Gerceklesen'},inplace=True)
GrafikCiz(apioranlari,3,0)


print("Mevduat Faizi Verisi Aliniyor ...")
datafaiz = evds.get_data(['TP.TRY.MT02', "TP.TRY.MT03", "TP.TRY.MT06" ], startdate=yilonce, enddate=bugun)
datafaiz.rename(columns={'TP_TRY_MT02':'32-91 Gun Vadeli Mevduat', 'TP_TRY_MT03':'92-181 Gun Vadeli Mevduat', 'TP_TRY_MT06':'Toplam A.O'},inplace=True)
GrafikCiz(datafaiz,3,1)#mevduat


print("Kredi Faizi Verisi Aliniyor ...")
kredifaizleri = evds.get_data(["TP.KTF18", "TP.KTFTUK01", "TP.KTF101", "TP.KTF11", "TP.KTF12"] , startdate=yilonce, enddate=bugun)
kredifaizleri.rename(columns={'TP_KTF18':'Ticari Krediler', 'TP_KTFTUK01':'Tuketici Kredisi', 'TP_KTF101':'Ihtiyac Kredisi', 'TP_KTF11':'Tasit Kredisi', 'TP_KTF12':'Konut Kredisi'},inplace=True)
GrafikCiz(kredifaizleri,3,2) # kredi faizleri






print("Para Arzi Verisi Aliniyor ...")

arz3 = evds.get_data(['TP.PR.ARZ22'], startdate=yilonce, enddate=bugun, formulas=[1])
arz3.drop('TP_PR_ARZ22', axis=1, inplace=True)
Yuzdedegisimformatla(arz3)
arz3["TP_PR_ARZ22-1"] = arz3["TP_PR_ARZ22-1"] * 52

arz3["3 Aylık H.O Yıllıklandırılmış"] = arz3["TP_PR_ARZ22-1"].rolling(window=13).mean()
arz3.rename(columns={'TP_PR_ARZ22-1':'M3 Para Arzı Haftalık Değişim Yıllıklandırılmış' },inplace=True)
GrafikCiz(arz3,2,0)





print("Kredi Hacmi Verisi Aliniyor ...")

toplamkredidegisim = evds.get_data(['TP.KREDI.L001'], startdate=yilonce, enddate=bugun, formulas=[1])
toplamkredidegisim.drop(["TP_KREDI_L001"], axis=1, inplace=True)
Yuzdedegisimformatla(toplamkredidegisim)
toplamkredidegisim.rename(columns={'TP_KREDI_L001-1':'Toplam Kredi Hacmi Değişim'},inplace=True)
GrafikCiz(toplamkredidegisim,2,2)


print("Tuketici Kredisi Verisi Aliniyor ...")

tuketicikk = evds.get_data(['TP.BFTUKKRE.L002'], startdate=yilonce, enddate=bugun, formulas=[1])
tuketicikk.drop(['TP_BFTUKKRE_L002'], axis=1, inplace=True)
Yuzdedegisimformatla(tuketicikk)
tuketicikk.rename(columns={'TP_BFTUKKRE_L002-1':'Tüketici ve Kredi Kartları'},inplace=True)
GrafikCiz(tuketicikk,2,2)



konut = evds.get_data(['TP.BFTUKKRE.L005'], startdate=yilonce, enddate=bugun, formulas=[1])
Yuzdedegisimformatla(konut)
konut.drop(["TP_BFTUKKRE_L005"], axis=1,inplace=True)
konut.rename(columns={'TP_BFTUKKRE_L005-1':'Konut Kredisi Hacmi'},inplace=True)
GrafikCiz(konut,2,3)


arac = evds.get_data(['TP.BFTUKKRE.L007'], startdate=yilonce, enddate=bugun, formulas=[1])
arac.drop(["TP_BFTUKKRE_L007"], axis=1, inplace=True)
Yuzdedegisimformatla(arac)
arac.rename(columns={'TP_BFTUKKRE_L007-1':'Araç Kredisi Hacmi'},inplace=True)
GrafikCiz(arac,2,3)



print("Yabancilarin Menkul Kiymet Hareketleri Verisi Aliniyor ...")

yabancidegisim = evds.get_data(["TP.MKNETHAR.M7", "TP.MKNETHAR.M8"], startdate=yilonce, enddate=bugun)
yabancidegisim.rename(columns={'TP_MKNETHAR_M7': 'Yabancı Hisse Senedi Hareketi', 'TP_MKNETHAR_M8': 'Yabanci DIBS Hareketi'}, inplace=True)
GrafikCiz(yabancidegisim,2,1)

print("TLRef Verisi Aliniyor ...")

tlref = evds.get_data(["TP.BISTTLREF.ORAN"], startdate=yilonce, enddate=bugun)
tlref.rename(columns={'TP_BISTTLREF_ORAN' : 'TLRef Faizi'}, inplace=True)
tlref['TLRef Faizi Bilesik'] = (((tlref['TLRef Faizi']*1/36500+1) ** (365/1)) -1) * 100
GrafikCiz(tlref,3,3)

print("Likidite Verileri Aliniyor ...")

likidite = evds.get_data(["TP.PPIBSM", "TP.PPIGBTL"], startdate=yilonce, enddate=bugun)
likidite.rename(columns={"TP_PPIBSM":"Bankalar Serbest Mevduatı", "TP_PPIGBTL":"Gün Başı Toplam Likidite"}, inplace=True)
GrafikCiz(likidite,1,3)


# Grafiği gösterme
plt.figtext(0.5 ,0.03 , 'Tarih: ' + bugun, ha='center', va='center', fontsize=15, color='gray',  weight='bold') 
plt.figtext(0.9 ,0.03 , 'Credits: Harun Erdoğan Github:hrn-erdgn Twitter:harun_erdgn ', ha='center', va='center', fontsize=8, color='gray', alpha=0.7 ) 

fig.subplots_adjust(left=0.03, right=0.96, top=0.96, hspace=0.45)
plt.show()
