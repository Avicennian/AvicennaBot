# AvicennaBot (İbn Sînâ Discord Botu)

Bu proje, 11. yüzyılın büyük Fars hekimi ve filozofu İbn Sînâ'nın (Batı'da bilinen adıyla Avicenna) kimliğine bürünerek Discord üzerinde soruları yanıtlamak üzere tasarlanmış bir yapay zeka botudur. Bot, Google'ın Gemini modeli tarafından desteklenmekte ve kendisine yöneltilen sorulara İbn Sînâ'nın bilge ve rasyonel üslubuyla cevap vermektedir.

## Özellikler

* **Derinlikli Kişilik:** İbn Sînâ'nın felsefi (Meşşâîlik), bilimsel ve kişisel özelliklerine sadık kalarak tutarlı yanıtlar üretir.
* **Geniş Bilgi Alanı:** Felsefe, tıp, mantık, metafizik ve doğa bilimleri gibi konulardaki soruları bu perspektiften yanıtlar.
* **Etkileşim:** Sunucularda kendisinden bahsedildiğinde (`@AvicennaBot`) veya kendisine gönderilen özel mesajlarla (DM) çalışır.
* **Modern Teknoloji:** Google Gemini AI entegrasyonu ile güçlü bir anlama ve üretme yeteneğine sahiptir.

## Kullanılan Teknolojiler

* Python 3
* discord.py
* google-generativeai
* python-dotenv

## Kurulum ve Çalıştırma

Bu botu kendi bilgisayarınızda veya bir sunucuda çalıştırmak için aşağıdaki adımları izleyin:

1.  **Projeyi Klonlayın:**
    ```bash
    git clone https://github.com/Avicennian/AvicennaBot.git
    cd AvicennaBot
    ```

2.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Yapılandırma Dosyasını Oluşturun:**
    Proje ana dizininde `.env` adında bir dosya oluşturun ve içine kendi API anahtarlarınızı aşağıdaki formatta girin:
    ```env
    DISCORD_BOT_TOKEN="BURAYA_SİZİN_DISCORD_BOT_TOKENINIZ_GELECEK"
    GEMINI_API_KEY="BURAYA_SİZİN_GEMINI_API_ANAHTARINIZ_GELECEK"
    ```

4.  **Botu Başlatın:**
    ```bash
    python bot.py
    ```

## Kullanım

Botu Discord sunucunuza davet ettikten sonra, herhangi bir kanalda ondan `@AvicennaBot` şeklinde bahsederek veya ona özel mesaj göndererek soru sorabilirsiniz.

**Örnek:**
> `@AvicennaBot Varlık nedir?`
