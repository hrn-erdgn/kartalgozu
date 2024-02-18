# Kartal Gözü

Bu proje, Türkiye Cumhuriyet Merkez Bankası'nın (TCMB) Elektronik Veri Dağıtım Sistemi'nden (EVDS) makroekonomik verileri çekip, bu verileri anlamlı grafikler haline getiren bir Python uygulamasıdır.

![SS](https://github.com/hrn-erdgn/kartalgozu/blob/main/kartalgozu.jpg)
### Önkoşullar
Bu projeyi çalıştırmadan önce, Python'un yüklü olduğundan ve aşağıdaki kütüphanelerin kurulu olduğundan emin olun:
- matplotlib
- pandas
- evds
### Kurulum
1. Gerekli Python kütüphanelerini kurun
2. `kartalgozu.py` dosyasında bulunan `evdsAPI('Beni_Sil_Api_Key_Yaz')` satırını kendi EVDS API anahtarınızla değiştirin.
3. Uygulamayı şu komutla çalıştırın: `python kartalgozu.py` (Varsayılan olarak 1 yıllık veriler getirilir.
4. Geçmişe dönük daha fazla veri getirmek için örn. `python kartalgozu.py 3` komutunu çalıştırın son 3 yıllık veriler gelecektir.
### EVDS API Anahtarı nasıl alınır 
1. EVDS sayfasına giriş yaptıktan sonra Giriş Yap ve Kayıt Ol bağlantılarını izleyerek bir EVDS hesabı oluşturun
2. Ardından kullanıcı adınızın altında yer alan profil bağlantısına tıklayınız.
3. ![api](https://github.com/fatihmete/evds/blob/master/01.png)
4. Profil sayfanızın alt kısmında yer alan "API Anahtarı" butonuna tıklayınız ve açılan kutucukta yer alan
değeri kopyalayınız.

Evds python kütüphanesi için @fatihmete'ye teşekkürler.
