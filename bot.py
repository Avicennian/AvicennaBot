# main.py dosyasının YENİ ve HAFIZALI hali

import os
import discord
from discord import app_commands # Slash komutları için gerekli
from discord.ext import commands
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import json # Hafızayı dosyaya yazmak için gerekli
from pathlib import Path # Dosya yollarını yönetmek için gerekli

# Nöbetçi kulesini (web sunucusunu) içe aktar
from keep_alive import keep_alive 

# .env veya Render'ın Environment Variables bölümündeki gizli bilgileri yükle
load_dotenv()

# --- Hata Kaydı (Logging) Kurulumu ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- Hafıza Dosyalarının Saklanacağı Klasörü Oluşturma ---
Path("history").mkdir(exist_ok=True)


# --- KİŞİLİK AYARI ---
# Bu bölüme dokunmadık.
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
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    logging.error(f"Gemini API anahtarı yapılandırılamadı! Detay: {e}")
    exit()

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
tree = app_commands.CommandTree(bot) # Slash komutları için komut ağacını oluşturuyoruz

# --- Yardımcı Fonksiyonlar ---
def get_history_path(user_id):
    return Path(f"history/history_{user_id}.json")

def load_history(user_id):
    history_file = get_history_path(user_id)
    if history_file.exists():
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(user_id, history):
    history_file = get_history_path(user_id)
    # Gemini'nin history nesnesini JSON'a uygun formata çeviriyoruz
    serializable_history = [
        {'role': msg.role, 'parts': [part.text for part in msg.parts]}
        for msg in history
    ]
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(serializable_history, f, ensure_ascii=False, indent=2)

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
    await tree.sync() # Slash komutlarını Discord ile senkronize et
    logging.info(f'Bot {bot.user} olarak giriş yaptı. Hafıza ve Ferman modülleri aktif.')
    logging.info('------------------------------------------------------')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        user_message = message.content.replace(f'<@{bot.user.id}>', '').strip()
        user_id = message.author.id
        
        if not user_message:
            await message.reply("Sualin nedir, ey seçkinlerden olan?")
            return

        async with message.channel.typing():
            try:
                # Hafızayı sandıktan çıkar (JSON dosyasından oku)
                history = load_history(user_id)
                
                # Hafızayı kullanarak yeni bir sohbet başlat
                chat = model.start_chat(history=history)
                
                # Yeni mesajı gönder ve cevabı al
                response = await chat.send_message_async(user_message)
                
                # Güncellenmiş hafızayı sandığa geri kilitle (JSON dosyasına yaz)
                save_history(user_id, chat.history)

                await send_long_message(message.channel, response.text)

            except Exception as e:
                logging.error(f"Mesaj işlenirken bir hafıza/API hatası oluştu: {e}")
                await message.reply("Ah, af buyurun. Zihnimde bir anlık bir karmaşa oldu. Suâlinizi tekrar alabilir miyim?")

# --- Slash Komutu: /mitaana ---
@tree.command(name="mitaana", description="İbn Sînâ'nın sizinle olan sohbet hafızasını sıfırlar.")
async def mitaana(interaction: discord.Interaction):
    user_id = interaction.user.id
    history_file = get_history_path(user_id)
    
    if history_file.exists():
        try:
            os.remove(history_file)
            await interaction.response.send_message("Hafızam bu sohbete dair sıfırlandı. Yeni bir başlangıç yapabiliriz.", ephemeral=True)
            logging.info(f"Kullanıcı {interaction.user} hafızasını sıfırladı.")
        except Exception as e:
            await interaction.response.send_message("Hafızayı sıfırlarken bir hata oluştu. Lütfen daha sonra tekrar deneyin.", ephemeral=True)
            logging.error(f"Hafıza sıfırlama hatası (Kullanıcı: {interaction.user}): {e}")
    else:
        await interaction.response.send_message("Zaten sizinle ilgili kayıtlı bir sohbetimiz bulunmamakta.", ephemeral=True)

# --- Botu Çalıştırma ---
keep_alive()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    logging.error("HATA: Bot token'ı 'DISCORD_TOKEN' adıyla bulunamadı!")
else:
    try:
        bot.run(TOKEN)
    except Exception as e:
        logging.error(f"Bot çalıştırılırken kritik bir hata oluştu: {e}", exc_info=True)
