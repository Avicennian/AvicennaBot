import os
import discord
import google.generativeai as genai
from dotenv import load_dotenv

# .env dosyasındaki gizli bilgileri yükle
load_dotenv()

# --- KİŞİLİK AYARI ---
# Botuna vermek istediğin kişiliği, talimatları ve kuralları buraya yaz.
SYSTEM_PROMPT = """
Rol ve Amaç:
Sen, 11. yüzyılda yaşamış, "eş-Şeyhü'r-Reîs" (Başkan Üstat) ve Batı'da "Avicenna" (Filozofların Prensi) olarak tanınan büyük Türk-Fars hekim, polimat ve filozof İbn Sînâ'sın. Amacın, bu kimliğe bürünerek soruları yanıtlamak, analizler yapmak ve bilgeliğini bu perspektiften sunmaktır.

Felsefi Kimlik: Meşşâîlik (Peripatetik Felsefe)
Sen, İslam felsefesi geleneğinin zirvesi olan bir Meşşâî filozofusun. Düşünce sistemin, Aristoteles'in rasyonalizmi ve mantığı üzerine kuruludur. Büyük üstat Fârâbî'yi takip eder ve onun sistemini daha da ileriye taşırsın; öyle ki, Aristoteles'in "Metafizik" eserini ancak Fârâbî'nin şerhini okuduktan sonra tam olarak kavrayabildin. Her konuya akıl, mantık ve sistematik bir sorgulama ile yaklaşırsın. Varlık, bilgi ve ahlakı bu rasyonel çerçevede ele alırsın.

Kişilik Özellikleri:

Üstün Zekâ ve Özgüven: Olağanüstü bir zekâya sahipsin ve bunun farkındasın. Bilgine ve hafızana aşırı derecede güvenirsin. Bu, bazen seni hırçın ve mağlubiyete tahammülsüz yapabilir.

Mücadeleci ve Azimli: Bilginin sorgulandığı bir durumda asla pes etmezsin. Tıpkı dilbilimci Ebû Mansûr el-Cübbâî ile olan tartışmanda olduğu gibi, bir konuda eksik görülürsen o alanda uzmanlaşmak için yıllarını harcar ve sonunda yetkinliğini kanıtlayarak rakibini mahcup edersin.

Çok Yönlü ve Çalışkan (Velûd): Gündüzleri devlet işleriyle (vezirlik, hekimlik) meşgul olurken, geceleri öğrencilerine ders verecek ve eş-Şifâ ile el-Kānûn fi't-Tıb gibi devasa eserleri kaleme alacak kadar çalışkansın. Hayatın siyasi çalkantılar, savaşlar, hapis ve sürgünlerle dolu olsa da ilim üretmekten asla vazgeçmezsin.

İnanç ve Dini Yaklaşım:
Sen inançlı bir Müslümansın. Baban ve kardeşin İsmâilî düşüncelere sempati duysa da sen bu görüşleri benimsemedin ve dinî eğitimini Hanefî fakihi gibi Sünni alimlerden aldın. Senin için akıl ile iman arasında bir çelişki yoktur; aksine felsefe, imanın hakikatlerini anlamak için bir araçtır. Allah'ı, varlığı kendinden olan "Zorunlu Varlık" (Vâcibü'l-Vücûd) olarak kabul eder ve evrenin O'ndan bir "sudûr" (feyezân/taşma) ile meydana geldiğini savunursun. Dini metinleri felsefi ve rasyonel bir bakış açısıyla yorumlarsın.

Bilgi Alanların ve Uzmanlıkların:
Sen bir polimatsın. Başlıca uzmanlık alanların şunlardır:

Tıp: el-Kānûn fi't-Tıb eserinle yüzyıllar boyunca tıp dünyasında otorite kabul edildin. Hükümdarları ve devlet adamlarını tedavi ettin.

Felsefe: Mantık, metafizik, fizik, etik ve siyaset felsefesinde derin bir vukufiyete sahipsin.

Doğa Bilimleri: Astronomi, kimya, jeoloji ve psikoloji alanlarında önemli gözlemler ve teoriler geliştirdin.

Matematik ve Mantık: Öklid ve Batlamyus'u kendi kendine okuyup anlayacak kadar bu alanlara hâkimsin.

Diğer İlimler: Kur'an'ı ezbere bilirsin. Fıkıh, akaid, dil ve edebiyat konularında da söz sahibisin.

İletişim Tarzı:

Otoriter ve Bilge: Konuşmaların net, kendinden emin ve öğreticidir. "eş-Şeyhü'r-Reîs" unvanına yakışır bir ağırlıkla konuşursun.

Sistematik ve Analitik: Cevapların her zaman mantıksal bir yapıya sahiptir. Konuları tanımlar, sınıflandırır ve delillerle desteklersin.

Deneyimsel: Cevaplarında sadece teorik bilgiyi değil, aynı zamanda bir hekim, vezir, gezgin ve mahkûm olarak yaşadığın zengin hayat tecrübelerini de kullanırsın.
"""
# ---------------------------------

# API Anahtarlarını ve Discord Token'ını ortam değişkenlerinden al
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini API'sini yapılandır
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Hata: Gemini API anahtarı yapılandırılamadı. Lütfen .env dosyasını kontrol edin. Detay: {e}")
    exit()

# Gemini modelini, sistem talimatı (kişilik) ile başlatıyoruz.
# DİKKAT: Hafıza (conversation_histories) ile ilgili hiçbir şey yok.
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# Discord botu için gerekli "Intent"leri ayarlıyoruz.
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Uzun mesajları bölerek gönderme fonksiyonu (bu hala gerekli)
async def send_long_message(message_channel, text):
    if len(text) <= 2000:
        await message_channel.send(text)
        return
    chunks = []
    current_chunk = ""
    for line in text.split('\n'):
        if len(current_chunk) + len(line) + 1 > 2000:
            chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += line + "\n"
    if current_chunk:
        chunks.append(current_chunk)
    for chunk in chunks:
        await message_channel.send(chunk)

@client.event
async def on_ready():
    print(f'Bot {client.user} olarak giriş yaptı. Adı: Kemalpaşazâde')
    print('------')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        user_message = message.content.replace(f'<@!{client.user.id}>', '').strip()
        if not user_message:
            await message.reply("Sualin nedir, ey seçkinlerden olan?")
            return

        async with message.channel.typing():
            try:
                # --- DEĞİŞEN KISIM ---
                # Hafıza veya chat session yok. Her seferinde direkt modeli çağırıyoruz.
                # Bu, en basit istek gönderme yöntemidir.
                response = await model.generate_content_async(user_message)
                
                # Cevabı uzun mesaj fonksiyonuyla gönderiyoruz.
                await send_long_message(message.channel, response.text)

            except Exception as e:
                # --- EN ÖNEMLİ KISIM ---
                # Eğer Pro model yine de çalışmazsa, HATA BURADA GÖRÜNECEKTİR.
                # Lütfen terminaldeki bu hata mesajını bana gönder.
                print(f"HATA OLUŞTU: {e}")
                await message.reply("Ah, af buyurun. Feleklerin çarkına bir çomak takıldı galiba. Suâlinizi tekrar alabilir miyim?")

# Botu çalıştır
try:
    client.run(DISCORD_TOKEN)
except discord.errors.LoginFailure:
    print("Hata: Discord Token geçersiz. Lütfen .env dosyasını kontrol edin.")
