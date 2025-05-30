import requests
import datetime
import logging
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
import schedule
import time
import threading

# Seus dados exatos
BOT_TOKEN = "7992672152:AAHw2SOWgYxeYNxvHuHF5JAnBdQcJH32T04"
CHAT_ID = -4877842034
API_FOOTBALL_KEY = "b3879f0403010fc901ed1b2c6ed5e31e"

LEAGUES = [
    39,  # Premier League
    78,  # La Liga
    61,  # Bundesliga
    140, # Serie A
    135, # Ligue 1
    271, # Brasileirão Série A
    2,   # Copa do Brasil
]

HEADERS = {"x-apisports-key": API_FOOTBALL_KEY}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def get_today_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def fetch_fixtures():
    today = get_today_date()
    leagues_param = ",".join(map(str, LEAGUES))
    url = f"https://v3.football.api-sports.io/fixtures?date={today}&league={leagues_param}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    if data.get("errors"):
        logger.error("API Football errors: %s", data["errors"])
        return []
    return data.get("response", [])

def fetch_team_stats(team_id):
    url = f"https://v3.football.api-sports.io/teams/statistics?team={team_id}&last=5"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    if data.get("errors"):
        logger.error("API Football errors in stats: %s", data["errors"])
        return None
    return data.get("response", {})

def analyze_match(fixture):
    home = fixture['teams']['home']
    away = fixture['teams']['away']
    league = fixture['league']['name']
    kickoff = fixture['fixture']['date'][11:16]

    home_stats = fetch_team_stats(home['id'])
    away_stats = fetch_team_stats(away['id'])
    if not home_stats or not away_stats:
        return None

    def meets_criteria(stats):
        corner_avg_1t = stats.get("corners", {}).get("average", {}).get("first_half", 0)
        return corner_avg_1t >= 3.0

    home_meets = meets_criteria(home_stats)
    away_meets = meets_criteria(away_stats)

    aposta = "SIM" if home_meets or away_meets else "NÃO"

    return {
        "home": home['name'],
        "away": away['name'],
        "league": league,
        "time": kickoff,
        "aposta": aposta,
        "odd": "Ex: 1.85",
        "link_bet365": "https://www.bet365.com/#/AC/B18/C20604387/D43/E145825/F43/"
    }

def build_message():
    fixtures = fetch_fixtures()
    if not fixtures:
        return "Nenhum jogo encontrado para hoje."

    message = "*SINAIS DE ESCANTEIOS - HOJE*\n\n"
    for f in fixtures:
        result = analyze_match(f)
        if not result:
            continue
        message += f"⚽ *{result['home']} vs {result['away']}*\n"
        message += f"🏆 Liga: {result['league']}\n"
        message += f"🕒 Horário: {result['time']}\n"
        message += f"🎯 Aposta: *{result['aposta']}*\n"
        message += f"💰 Odd aproximada: {result['odd']}\n"
        message += f"🔗 [Link Bet365]({result['link_bet365']})\n"
        message += "-------------------------\n"

    return message

def send_signals(context=None):
    try:
        message = build_message()
        updater.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)
        logger.info("Lista enviada com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")

def start(update, context):
    update.message.reply_text("Buscando sinais para hoje, aguarde...")
    send_signals()
    update.message.reply_text("Lista enviada!")

def schedule_daily():
    schedule.every().day.at("08:00").do(send_signals)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    logger.info("Bot iniciado!")

    thread = threading.Thread(target=schedule_daily)
    thread.start()

    updater.idle()
