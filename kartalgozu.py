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
fig2, axes2 = plt.subplots(4,4,figsize=(6*4,4*3))   # 2. Pencere
#fig.canvas.set_window_title('KartalGozu V1.0')

def degerformatla(value, _):
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


def TarihFormatla(veri):
    try:
        veri["Tarih"] = pd.to_datetime(veri["Tarih"], format="%d-%m-%Y").dt.date
        return veri
    except:
        return veri





def Yuzdedegisimformatla(veri):
    for tur in veri.columns[1:]:
        veri[tur]= pd.to_numeric(veri[tur], errors='coerce')
        veri[tur] = veri[tur].round(3)



def GrafikCiz(veri, x, y, parametre):
    veri = TarihFormatla(veri)
    veri.dropna(axis=1,how="all",inplace=True)
    veri.dropna( inplace=True)
    if "YEARWEEK" in veri.columns:
        veri.drop("YEARWEEK",axis=1,inplace=True)
    if parametre == 1:
        cizilecek_axes = axes
    elif parametre == 2:
        cizilecek_axes = axes2
    else:
        raise ValueError("Parametre 1 veya 2 olabilir")

    for tur in veri.columns[1:]:
        cizgi, = cizilecek_axes[x][y].plot(veri["Tarih"], veri[tur],label=tur)
        cizilecek_axes[x][y].annotate(degerformatla(veri[tur].iloc[-1],1), xy=(veri["Tarih"].iloc[-1], veri[tur].iloc[-1]), color=cizgi.get_color(), va="center")
    cizilecek_axes[x][y].set_xlim(veri["Tarih"].min(), veri["Tarih"].max())
    cizilecek_axes[x][y].set_title(str(veri["Tarih"].iloc[-1]))
    cizilecek_axes[x][y].legend(loc="upper left")
    cizilecek_axes[x][y].grid(alpha=0.8)
    cizilecek_axes[x][y].yaxis.set_major_formatter(formatter)
    cizilecek_axes[x][y].tick_params(axis='x', rotation=45, labelsize=8)
    cizilecek_axes[x][y].tick_params(axis='y', rotation=45, labelsize=6)
    if(veri[tur]<0).any():
        cizilecek_axes[x][y].axhline(0, color='black', ls='--', linewidth=1)






#============================================== Dolar TL ============================================================================
print("Dolar TL Verisi Aliniyor ...")
datadolartl = evds.get_data(['TP.DK.USD.A.YTL'], startdate=yilonce, enddate=bugun)
datadolartl.rename(columns={'TP_DK_USD_A_YTL':'Dolar TL'},inplace=True)
GrafikCiz(datadolartl,0,0,1)
#=====================================================================================================================================

############################################### BIST Bolgesi ################################
print("Bist Verisi Aliniyor ...")
bist = evds.get_data(['TP.MK.F.BILESIK'], startdate=yilonce, enddate=bugun)
bist.rename(columns={'TP_MK_F_BILESIK':'BIST 100'},inplace=True)
GrafikCiz(bist,0,1,1)
############################################################################################

################################## Bist Dolar Bolgesi ######################################
bistdolar = evds.get_data(['TP.MK.F.BILESIK', 'TP.DK.USD.A.YTL'], startdate=yilonce, enddate=bugun)
bistdolar["Bist100 $"] = bistdolar["TP_MK_F_BILESIK"] / bistdolar["TP_DK_USD_A_YTL"]
bistdolar.drop(['TP_MK_F_BILESIK','TP_DK_USD_A_YTL'], axis=1, inplace=True)
GrafikCiz(bistdolar,0,2,1)
###########################################################################################

################################# Toplam Kredi Hacmi Bolgesi ################
print("Toplam Kredi Hacmi Verisi Aliniyor ...")
kredihacmidolar = evds.get_data(['TP.KREDI.L001','TP.DK.USD.A.YTL'], startdate=yilonce, enddate=bugun)
kredihacmidolar["Toplam Kredi Hacmi $"] = kredihacmidolar["TP_KREDI_L001"] / kredihacmidolar["TP_DK_USD_A_YTL"]
kredihacmidolar.drop(['TP_KREDI_L001','TP_DK_USD_A_YTL'], axis=1, inplace=True)
GrafikCiz(kredihacmidolar,0,3,1)
#########################################################################################

######################################## Rezerv Bolgesi ##################################
print("Rezerv Verisi Aliniyor ...")
#rezerv = evds.get_data(['TP.AB.A02','TP.AB.A10','TP.DK.USD.A.YTL'], startdate=yilonce, enddate=bugun)
#rezerv["Brüt TCMB Dolar Rezervi"] = (rezerv["TP_AB_A02"] - rezerv["TP_AB_A10"]) / rezerv["TP_DK_USD_A_YTL"]
#rezerv.drop(["TP_AB_A02","TP_AB_A10","TP_DK_USD_A_YTL"], axis=1, inplace=True)


rezerv = evds.get_data(['TP.AB.TOPLAM'], startdate=yilonce, enddate=bugun)
rezerv.rename(columns={'TP_AB_TOPLAM': 'TCMB Rezervi(Mlyn $)'}, inplace=True)
GrafikCiz(rezerv,1,0,1)
###########################################################################################

#################################### Api Grafigi Bolgesi #################################
print("Acik Piyasa Islemleri Verisi Aliniyor ...")
tcmbnetfonlama = evds.get_data(['TP.APIFON3'], startdate=yilonce, enddate=bugun)
tcmbnetfonlama.rename(columns={'TP_APIFON3':'API Net Fonlama'},inplace=True)
GrafikCiz(tcmbnetfonlama,1,1,1)
############################################################################################

########################################### Swap Verisi Bolgesi ##############################
print("Swap Verisi Aliniyor ...")
bankaswap = evds.get_data(['TP.TLDOV01.SWP'], startdate=yilonce, enddate=bugun)
bankaswap.rename(columns={'TP_TLDOV01_SWP':'TL DOLAR Swap'},inplace=True)
GrafikCiz(bankaswap,1,2,1)
##############################################################################################

############################################ Faiz Koridoru Bolgesi ############################
print("Faiz Koridoru Verisi Aliniyor ...")
apioranlari = yabancidegisim = evds.get_data(["TP.PY.P01.ON", "TP.PY.P02.ON", "TP.PY.P06.ON"], startdate=yilonce, enddate=bugun)
apioranlari.rename(columns={'TP_PY_P01_ON':'Koridor ALT', 'TP_PY_P02_ON':'Koridor UST', 'TP_PY_P06_ON':'Gerceklesen'},inplace=True)
GrafikCiz(apioranlari,3,0,1)
##################################################################################################

############################################# Mevduat Faizi Verileri #############################
print("Mevduat Faizi Verisi Aliniyor ...")
datafaiz = evds.get_data(['TP.TRY.MT02', "TP.TRY.MT03", "TP.TRY.MT06" ], startdate=yilonce, enddate=bugun)
datafaiz.rename(columns={'TP_TRY_MT02':'32-91 Gun Vadeli Mevduat', 'TP_TRY_MT03':'92-181 Gun Vadeli Mevduat', 'TP_TRY_MT06':'Toplam A.O'},inplace=True)
GrafikCiz(datafaiz,3,1,1)#mevduat
###################################################################################################

######################################## Kredi Faizi Verileri ######################################
print("Kredi Faizi Verisi Aliniyor ...")
kredifaizleri = evds.get_data(["TP.KTF18", "TP.KTFTUK01", "TP.KTF101", "TP.KTF11", "TP.KTF12"] , startdate=yilonce, enddate=bugun)
kredifaizleri.rename(columns={'TP_KTF18':'Ticari Krediler', 'TP_KTFTUK01':'Tuketici Kredisi', 'TP_KTF101':'Ihtiyac Kredisi', 'TP_KTF11':'Tasit Kredisi', 'TP_KTF12':'Konut Kredisi'},inplace=True)
GrafikCiz(kredifaizleri,3,2,1) # kredi faizleri
#####################################################################################################

###################################### Para Arzi Bolgesi ###############################################
print("Para Arzi Verisi Aliniyor ...")
arz3 = evds.get_data(['TP.PR.ARZ22'], startdate=yilonce, enddate=bugun, formulas=[1])
arz3.drop('TP_PR_ARZ22', axis=1, inplace=True)
Yuzdedegisimformatla(arz3)
arz3["TP_PR_ARZ22-1"] = arz3["TP_PR_ARZ22-1"] * 52
arz3["3 Aylık H.O Yıllıklandırılmış %"] = arz3["TP_PR_ARZ22-1"].rolling(window=13).mean()
arz3.rename(columns={'TP_PR_ARZ22-1':'M3 Para Arzı Haftalık Değişim Yıllıklandırılmış %' },inplace=True)
GrafikCiz(arz3,2,0,1)
###########################################################################################################

###################################### Kredi Hacmi Bolgesi ######################################################
print("Kredi Hacmi Verisi Aliniyor ...")
toplamkredidegisim = evds.get_data(['TP.KREDI.L001'], startdate=yilonce, enddate=bugun, formulas=[1])
toplamkredidegisim.drop(["TP_KREDI_L001"], axis=1, inplace=True)
Yuzdedegisimformatla(toplamkredidegisim)
toplamkredidegisim.rename(columns={'TP_KREDI_L001-1':'Toplam Kredi Hacmi Değişim %'},inplace=True)
GrafikCiz(toplamkredidegisim,2,2,1)
##################################################################################################################

##################################### Tuketici Kredisi Bolgesi ####################################################
print("Tuketici Kredisi Verisi Aliniyor ...")
tuketicikk = evds.get_data(['TP.BFTUKKRE.L002'], startdate=yilonce, enddate=bugun, formulas=[1])
tuketicikk.drop(['TP_BFTUKKRE_L002'], axis=1, inplace=True)
Yuzdedegisimformatla(tuketicikk)
tuketicikk.rename(columns={'TP_BFTUKKRE_L002-1':'Tüketici ve Kredi Kartları Değişim %'},inplace=True)
GrafikCiz(tuketicikk,2,2,1)
#####################################################################################################################

################################# Konut Kredisi Bolgesi ##################################################################
konut = evds.get_data(['TP.BFTUKKRE.L005'], startdate=yilonce, enddate=bugun, formulas=[1])
Yuzdedegisimformatla(konut)
konut.drop(["TP_BFTUKKRE_L005"], axis=1,inplace=True)
konut.rename(columns={'TP_BFTUKKRE_L005-1':'Konut Kredisi Hacmi Değişim %'},inplace=True)
GrafikCiz(konut,2,3,1)
#######################################################################################################################

#################################### Arac Kredisi Grafigi Bolgesi #######################################################
arac = evds.get_data(['TP.BFTUKKRE.L007'], startdate=yilonce, enddate=bugun, formulas=[1])
arac.drop(["TP_BFTUKKRE_L007"], axis=1, inplace=True)
Yuzdedegisimformatla(arac)
arac.rename(columns={'TP_BFTUKKRE_L007-1':'Araç Kredisi Hacmi Değişim %'},inplace=True)
GrafikCiz(arac,2,3,1)
#########################################################################################################################


############################## Yabanci Menkul Kiymet Grafigi Bolgesi ###############################################
print("Yabancilarin Menkul Kiymet Hareketleri Verisi Aliniyor ...")
yabancidegisim = evds.get_data(["TP.MKNETHAR.M7", "TP.MKNETHAR.M8"], startdate=yilonce, enddate=bugun)
yabancidegisim.rename(columns={'TP_MKNETHAR_M7': 'Yabancı Hisse Senedi Hareketi', 'TP_MKNETHAR_M8': 'Yabanci DIBS Hareketi'}, inplace=True)
GrafikCiz(yabancidegisim,2,1,1)
######################################################################################################################

############################# TLRef Grafigi Bolgesi ####################################################################
print("TLRef Verisi Aliniyor ...")
tlref = evds.get_data(["TP.BISTTLREF.ORAN"], startdate=yilonce, enddate=bugun)
tlref.rename(columns={'TP_BISTTLREF_ORAN' : 'TLRef Faizi'}, inplace=True)
tlref['TLRef Faizi Bilesik'] = (((tlref['TLRef Faizi']*1/36500+1) ** (365/1)) -1) * 100
GrafikCiz(tlref,3,3,1)
######################################################################################################################


########################### Likidite Grafigi Bolgesi ##################################################################
print("Likidite Verileri Aliniyor ...")
likidite = evds.get_data(["TP.PPIBSM", "TP.PPIGBTL"], startdate=yilonce, enddate=bugun)
likidite.rename(columns={"TP_PPIBSM":"Bankalar Serbest Mevduatı", "TP_PPIGBTL":"Gün Başı Toplam Likidite"}, inplace=True)
GrafikCiz(likidite,1,3,1)
#########################################################################################################################


#================================================= 2. Pencere Verileri =======================================================

################################################ ENFLASYON GRAFIGI BOLGESI ########################################################
print("Enflasyon Verileri Aliniyor ...")
yillikenflasyon = evds.get_data(["TP.FG.J0"], startdate=yilonce, enddate=bugun, formulas=[3])
yillikenflasyon.drop(["TP_FG_J0"], axis=1, inplace=True)
Yuzdedegisimformatla(yillikenflasyon)
yillikenflasyon.rename(columns={"TP_FG_J0-3": "Yillik TÜFE"}, inplace=True)
ufeyillik = evds.get_data(['TP.TUFE1YI.T1'], startdate=yilonce, enddate=bugun, formulas=[3])
ufeyillik.drop(["TP_TUFE1YI_T1"], axis=1, inplace=True)
Yuzdedegisimformatla(ufeyillik)
ufeyillik.rename(columns={"TP_TUFE1YI_T1-3": "Yillik ÜFE"}, inplace=True)
yillikenflasyon["Yillik ÜFE"] = ufeyillik["Yillik ÜFE"]
GrafikCiz(yillikenflasyon,0,0,2) # TARIHLER AY TARIH olarak geliyor gun ay yil olarak gelmeli
axes2[0][0].set_ylim(bottom=0)
#=========================== aylik ===================================
ayliktufe = evds.get_data(["TP.FG.J0"], startdate=yilonce, enddate=bugun, formulas=[1])
ayliktufe.drop(["TP_FG_J0"], axis=1, inplace=True)
Yuzdedegisimformatla(ayliktufe)
ayliktufe.rename(columns={"TP_FG_J0-1": "Aylik TÜFE"}, inplace=True)
aylikufe = evds.get_data(['TP.TUFE1YI.T1'], startdate=yilonce, enddate=bugun, formulas=[1])
aylikufe.drop(["TP_TUFE1YI_T1"],axis=1, inplace=True)
Yuzdedegisimformatla(aylikufe)
aylikufe.rename(columns={"TP_TUFE1YI_T1-1": "Aylik ÜFE"}, inplace=True)
aylikenflasyonax = axes2[0][0].twinx()
bar_width = 0.35
x = range(len(ayliktufe))
ayliktufebarlari = aylikenflasyonax.bar([pos - bar_width / 2 for pos in x], ayliktufe['Aylik TÜFE'], bar_width, color='tab:blue',alpha=0.8)
ufeaylikbarlari = aylikenflasyonax.bar([pos + bar_width / 2 for pos in x] , aylikufe['Aylik ÜFE'], bar_width, color='orange',alpha=0.8)
aylikenflasyonax.bar_label(ayliktufebarlari, fmt='%.1f', padding=1,fontsize=6)
aylikenflasyonax.bar_label(ufeaylikbarlari, fmt='%.1f', padding=1,fontsize=6)
axes2[0][0].margins(x=0.1)
axes2[0][0].set_xlim(-0.5, len(ayliktufe) - 0.5)
aylikenflasyonmaksdegeri = max(ayliktufe['Aylik TÜFE'].max(),aylikufe['Aylik ÜFE'].max())
aylikenflasyonax.set_ylim(top=aylikenflasyonmaksdegeri *2)


################################################ KONUT FIYAT ENDEKSI ###############################################################

print("Konut Fiyat Endeksi Verileri Aliniyor ...")
konutfiyatendeksiyillik = evds.get_data(["TP.KFE.TR"], startdate=yilonce, enddate=bugun, formulas=[3])
konutfiyatendeksiyillik.drop(["TP_KFE_TR"], axis=1, inplace=True)
Yuzdedegisimformatla(konutfiyatendeksiyillik)
konutfiyatendeksiyillik.rename(columns={"TP_KFE_TR-3": "Konut Fiyat Endeksi Yillik Degisim"}, inplace=True)
GrafikCiz(konutfiyatendeksiyillik,0,1,2)
axes2[0][1].set_ylim(bottom=0)


#=============================== kfe aylik ==================================

konutfiyatendeksiaylik = evds.get_data(["TP.KFE.TR"], startdate=yilonce, enddate=bugun, formulas=[1])
konutfiyatendeksiaylik.drop(["TP_KFE_TR"], axis=1, inplace=True)
Yuzdedegisimformatla(konutfiyatendeksiaylik)
konutfiyatendeksiaylik.rename(columns={"TP_KFE_TR-1": "K.F.E Aylik Değişim"}, inplace=True)

konutfiyatendeksiax = axes2[0][1].twinx()
konutfiyatendeksiaylikbarlari = konutfiyatendeksiax.bar(konutfiyatendeksiaylik['Tarih'], konutfiyatendeksiaylik['K.F.E Aylik Değişim'], color='tab:blue',alpha=0.8)
konutfiyatendeksiax.bar_label(konutfiyatendeksiaylikbarlari, fmt='%.1f')
konutfiyatendeksiaylikbarlarimaksdegeri = max(konutfiyatendeksiaylik['K.F.E Aylik Değişim'])
konutfiyatendeksiax.set_ylim(top=konutfiyatendeksiaylikbarlarimaksdegeri *2)

axes2[0][1].set_xlim(-0.5, len(konutfiyatendeksiaylik) - 0.5)


###################################################################################################################################

######## 1. Pencereyi Goster ################
fig.text(0.5 ,0.03 , 'Tarih: ' + bugun, ha='center', va='center', fontsize=15, color='gray',  weight='bold') 
fig.text(0.9 ,0.03 , 'Credits: Harun Erdoğan Github:hrn-erdgn Twitter:harun_erdgn ', ha='center', va='center', fontsize=8, color='gray', alpha=0.7 ) 

######## 2. Pencerei Goster ##################
fig2.text(0.5 ,0.03 , 'Tarih: ' + bugun, ha='center', va='center', fontsize=15, color='gray',  weight='bold') 
fig2.text(0.9 ,0.03 , 'Credits: Harun Erdoğan Github:hrn-erdgn Twitter:harun_erdgn ', ha='center', va='center', fontsize=8, color='gray', alpha=0.7 ) 



fig.subplots_adjust(left=0.03, right=0.96, top=0.96, hspace=0.45)
fig2.subplots_adjust(left=0.03, right=0.96, top=0.96, hspace=0.45)

plt.show()

