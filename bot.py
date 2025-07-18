# Gerekli tüm kütüphaneleri ve modülleri içe aktarıyoruz
import os
import discord
from discord.ext import commands
import google.generativeai as genai
from dotenv import load_dotenv
import logging
from keep_alive import keep_alive # Nöbetçi kulesini (web sunucusunu) içe aktar

# .env veya Render'ın Environment Variables bölümündeki gizli bilgileri yükle
load_dotenv()

# --- Hata Kaydı (Logging) Kurulumu ---
# Bu bölüm, botta olan biten her şeyi ve özellikle hataları sunucudaki bir log dosyasına yazar.
# Bu bizim kara kutumuzdur.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- KİŞİLİK AYARI ---
# Bu bölüme dokunmadık, sizin yazdığınız gibi kalacak.
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

# --- API ve Bot Kurulumu ---

# Render'daki Environment Variables'dan bilgileri alacağız
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini API'sini yapılandır
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    logging.error(f"Gemini API anahtarı yapılandırılamadı! Lütfen Render'daki Environment Variables'ı kontrol edin. Detay: {e}")
    exit()

# Gemini modelini başlat
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# Discord botu için gerekli "Intent"leri (izinleri) ayarlıyoruz.
intents = discord.Intents.default()
intents.message_content = True

# `discord.Client` yerine daha modern olan `commands.Bot` kullanıyoruz
bot = commands.Bot(command_prefix='!', intents=intents)


# Uzun mesajları bölerek gönderme fonksiyonu
async def send_long_message(channel, text):
    if len(text) <= 2000:
        await channel.send(text)
        return
    chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
    for chunk in chunks:
        await channel.send(chunk)

# --- Bot Olayları (Events) ---

@bot.event
async def on_ready():
    logging.info(f'Bot {bot.user} olarak giriş yaptı. Render üzerinde göreve hazır.')
    logging.info('------------------------------------------------------')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        user_message = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        if not user_message:
            await message.reply("Sualin nedir, ey seçkinlerden olan?")
            return

        async with message.channel.typing():
            try:
                response = await model.generate_content_async(user_message)
                await send_long_message(message.channel, response.text)
            except Exception as e:
                logging.error(f"Mesaj işlenirken bir hata oluştu: {e}")
                await message.reply("Ah, af buyurun. Feleklerin çarkına bir çomak takıldı galiba. Suâlinizi tekrar alabilir miyim?")

# Herhangi bir komutta veya olayda beklenmedik bir hata olursa burası devreye girer
@bot.event
async def on_error(event, *args, **kwargs):
    logging.error(f"Beklenmedik bir Discord olayı hatası: {event} | Args: {args} | Kwargs: {kwargs}", exc_info=True)


# --- Botu Çalıştırma ---

# Önce 7/24 aktiflik sunucusunu başlat
keep_alive()

# Token'ın var olup olmadığını kontrol et
if not DISCORD_TOKEN:
    logging.error("HATA: Bot token'ı 'DISCORD_TOKEN' adıyla bulunamadı!")
else:
    try:
        bot.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        logging.error("HATA: Geçersiz bir Discord token'ı girildi.")
    except Exception as e:
        logging.error(f"Bot çalıştırılırken kritik bir hata oluştu: {e}")
