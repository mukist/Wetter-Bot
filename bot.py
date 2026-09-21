import requests
import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = "8806690662:AAGKnoR5LJaEqZkK-nIiP0eyve6X0QrxGS8"
WEATHER_API_KEY = "358c46403a373181ef7d0fb0f1b633c8"
DEFAULT_CITY = "Vienna"

def get_weather_and_outfit(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=tr"
    response = requests.get(url).json()

    if response.get("cod") != 200:
        return "Hava durumu bilgisi alınamadı."

    temp = round(response["main"]["temp"])
    desc = response["weather"][0]["description"].lower()
    weather_main = response["weather"][0]["main"].lower()
    wind_speed = round(response["wind"]["speed"] * 3.6)
    humidity = response["main"]["humidity"]

    if temp < 5:
        outfit = "🧥 *Sıcaklık:* Kalın mont, kazak ve termal içlik tercih etmelisin."
    elif 5 <= temp < 15:
        outfit = "🧥 *Sıcaklık:* Ceket, hırka veya hafif bir mont iyi bir seçim olur."
    elif 15 <= temp < 22:
        outfit = "👕 *Sıcaklık:* Uzun kollu tişört veya hafif bir sweat yeterli."
    else:
        outfit = "👕 *Sıcaklık:* İnce tişört, şort veya ferah kıyafetler giyebilirsin."

    equipments = []
    if weather_main == "clear" or "açık" in desc:
        equipments.append("🕶️ Güneş gözlüğünü yanına almayı unutma!")

    if "yağmur" in desc or "çisenti" in desc or weather_main == "rain":
        equipments.append("☔ Yanında mutlaka şemsiye veya su geçirmez ayakkabı bulundur.")

    if wind_speed >= 20:
        equipments.append("💨 Rüzgar kuvvetli! Rüzgarlık giymen veya kulaklarını koruman önerilir.")

    equipments_text = "\n".join(equipments) if equipments else "✨ Özel bir ekipman gerekmiyor, hava rahat."

    message = (
        f"📅 *Günlük Rapor - {city}*\n\n"
        f"🌡️ *Sıcaklık:* {temp}°C\n"
        f"☁️ *Durum:* {desc.capitalize()}\n"
        f"💨 *Rüzgar:* {wind_speed} km/h\n"
        f"💧 *Nem:* %{humidity}\n\n"
        f"💡 *Kıyafet Seçimi:*\n{outfit}\n\n"
        f"🎒 *Ekipman Önerileri:*\n{equipments_text}"
    )
    return message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Merhaba! Hava durumuna göre kıyafet ve ekipman tavsiyesi veren botuna hoş geldin.\n\n"
        "/hava - Anlık rapor alır.\n"
        "/bildirim - Her sabah 05:50'de otomatik bildirim başlatır."
    )

async def hava(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = context.args[0] if context.args else DEFAULT_CITY
    message = get_weather_and_outfit(city)
    await update.message.reply_text(message, parse_mode="Markdown")

async def send_daily_notification(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    message = get_weather_and_outfit(DEFAULT_CITY)
    await context.bot.send_message(job.chat_id, text=message, parse_mode="Markdown")

async def bildirim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    tz = pytz.timezone("Europe/Vienna")
    target_time = datetime.time(hour=5, minute=50, second=0, tzinfo=tz)

    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    context.job_queue.run_daily(
        send_daily_notification,
        time=target_time,
        chat_id=chat_id,
        name=str(chat_id)
    )
    await update.message.reply_text("✅ Günlük bildirimler Viyana saatiyle her sabah saat 05:50 olarak ayarlandı!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hava", hava))
    app.add_handler(CommandHandler("bildirim", bildirim))
    print("WetterV_bot çalışıyor...")
    app.run_polling()
