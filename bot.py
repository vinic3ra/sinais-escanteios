import requests
import datetime
import telegram
import schedule
import time

# === CONFIGURAÇÕES ===
API_KEY = "b3879f0403010fc901ed1b2c6ed5e31e"
BOT_TOKEN = "7992672152:AAHw2SOWgYxeYNxvHuHF5JAnBdQcJH32T04"
CHAT_ID = "-4877842034"

bot = telegram.Bot(token=BOT_TOKEN)

# === FUNÇÃO PRINCIPAL ===
def analisar_e_enviar_jogos():
    hoje = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
    headers = {"x-apisports-key": API_KEY}
    resposta = requests.get(url, headers=headers)
    dados = resposta.json()

    mensagens = []

    for jogo in dados["response"]:
        liga = jogo["league"]["name"]
        pais = jogo["league"]["country"]
        time_casa = jogo["teams"]["home"]["name"]
        time_fora = jogo["teams"]["away"]["name"]
        horario = jogo["fixture"]["date"][11:16]
        fixture_id = jogo["fixture"]["id"]

        estat_url = f"https://v3.football.api-sports.io/teams/statistics?team={jogo['teams']['home']['id']}&season=2024&league={jogo['league']['id']}"
        estat_res = requests.get(estat_url, headers=headers).json()

        try:
            ultimos_casa = estat_res["response"]["fixtures"]["last5"]["matches"]
            escanteios_casa = [
                m["statistics"]["corners"]["total"] for m in ultimos_casa if "corners" in m["statistics"]
            ]
        except:
            escanteios_casa = []

        estat_url = f"https://v3.football.api-sports.io/teams/statistics?team={jogo['teams']['away']['id']}&season=2024&league={jogo['league']['id']}"
        estat_res = requests.get(estat_url, headers=headers).json()

        try:
            ultimos_fora = estat_res["response"]["fixtures"]["last5"]["matches"]
            escanteios_fora = [
                m["statistics"]["corners"]["total"] for m in ultimos_fora if "corners" in m["statistics"]
            ]
        except:
            escanteios_fora = []

        # === CRITÉRIOS ===
        def criterios_ok(lista):
            return len(lista) >= 5 and sum([e > 4.5 for e in lista]) >= 3

        def mais_de_9_5(lista1, lista2):
            soma_total = [c1 + c2 for c1, c2 in zip(lista1, lista2)]
            return sum([t > 9.5 for t in soma_total]) >= 3

        if criterios_ok(escanteios_casa) and criterios_ok(escanteios_fora) and mais_de_9_5(escanteios_casa, escanteios_fora):
            mensagem = f"""📊 SINAL DE ESCANTEIO CONFIRMADO ⚽

🕒 Horário: {horario}
🏆 Campeonato: {liga} - {pais}
🔵 Jogo: {time_casa} x {time_fora}

✅ Critérios batidos:
• +4.5 escanteios por time nos últimos jogos
• Pelo menos 3 dos últimos 5 jogos de cada time com +9.5 escanteios

🎯 Entrada: Over 8.5 FT
💸 Stake: 1% da banca

🛡️ Cobertura: se o jogo tiver <3 escanteios até os 35min, entrar Over 6.5 LIVE

📍Link: [Inserir link Bet365 aqui]
"""
            mensagens.append(mensagem)

    if mensagens:
        for m in mensagens:
            bot.send_message(chat_id=CHAT_ID, text=m)
    else:
        bot.send_message(chat_id=CHAT_ID, text="Nenhum jogo bateu os critérios hoje.")


# === COMANDO /START ===
from telegram.ext import Updater, CommandHandler

def start(update, context):
    update.message.reply_text("🔎 Buscando sinais...")
    analisar_e_enviar_jogos()

def rodar_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    schedule.every().day.at("08:00").do(analisar_e_enviar_jogos)

    while True:
        schedule.run_pending()
        time.sleep(30)

rodar_bot()
