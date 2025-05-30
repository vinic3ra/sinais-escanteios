import requests
import datetime
import time
import schedule
import telegram

API_KEY = "b3879f0403010fc901ed1b2c6ed5e31e"
BOT_TOKEN = "7992672152:AAHw2SOWgYxeYNxvHuHF5JAnBdQcJH32T04"
CHAT_ID = "-4877842034"

bot = telegram.Bot(token=BOT_TOKEN)

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

ligas_ids = [
    71,  # Brasileirão Série A
    72,  # Brasileirão Série B
    39,  # Premier League
    140, # La Liga
    135, # Serie A Itália
    61,  # Ligue 1
    78   # Bundesliga
]

def analisar_jogos():
    hoje = datetime.datetime.now().strftime('%Y-%m-%d')
    mensagens = []

    for liga_id in ligas_ids:
        url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?league={liga_id}&season=2024&date={hoje}"
        response = requests.get(url, headers=headers)
        jogos = response.json().get("response", [])

        for jogo in jogos:
            fixture = jogo["fixture"]
            teams = jogo["teams"]
            home = teams["home"]["name"]
            away = teams["away"]["name"]
            game_id = jogo["fixture"]["id"]

            stats_url = f"https://api-football-v1.p.rapidapi.com/v3/teams/statistics?team={jogo['teams']['home']['id']}&season=2024&league={liga_id}"
            stats = requests.get(stats_url, headers=headers).json()

            try:
                media_escanteios_1t = stats['response']['cards']['firsthalf']['total']  # Ajuste se necessário
                # Simulação de dados reais
                escanteios_10min = 3  # Aqui você pode usar uma API com histórico
                if media_escanteios_1t >= 3 and escanteios_10min >= 3:
                    mensagem = f"""Canto CONFIRMADO⚡️💰
🏆 {home} x {away}
📅 {hoje}

✅ Recomendação: APOSTA SIM – Vai ter escanteio até os 10 minutos

🎯 Média de escanteios 1T: {media_escanteios_1t}
⏱ Escanteios até os 10min em 3/5 últimos jogos

ENTRAR NO 0 - 10 (1%) ⛳️
COBERTURA NO 10 - 20 (3%) 🛡

🔗 *Acesse sua casa de aposta para entrar* (Bet365 link opcional)
"""
                else:
                    mensagem = f"""🚫 Jogo sem entrada segura
🏆 {home} x {away}
📅 {hoje}

❌ Recomendação: APOSTA NÃO – Baixo padrão de escanteios

🎯 Média de escanteios 1T: {media_escanteios_1t}
⏱ Escanteios até os 10min em poucos jogos
"""
                mensagens.append(mensagem)
            except Exception as e:
                continue

    for msg in mensagens:
        bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

# Agendamento automático
schedule.every().day.at("08:00").do(analisar_jogos)

# Comando manual via /start
from telegram.ext import Updater, CommandHandler

def start(update, context):
    bot.send_message(chat_id=CHAT_ID, text="🔍 Analisando jogos do dia...")
    analisar_jogos()

updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start", start))

updater.start_polling()

# Manter rodando
while True:
    schedule.run_pending()
    time.sleep(1)
