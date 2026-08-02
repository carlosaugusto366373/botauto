import asyncio
import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== CONFIGURAÇÕES DOS 3 CANAIS ====================
# Aqui você liga cada ID de canal à sua respectiva mensagem:
CANAIS_E_MENSAGENS = {
    # 1º Canal
    1526730887885226027: [
        "Entrega Automática!! Comprou? Chegou!! || @everyone @.gg/qzzcomunityy @here ||",
    ],
    # 2º Canal
    1514333562252300481: [
        "Proxy ON!! Android e Ios!! || @everyone @.gg/qzzcomunityy @here ||",
    ],
    # 3º Canal
    1514332751317172236: [
        "Proxy ON!! Android e Ios!! || @everyone @.gg/qzzcomunityy @here ||",
    ],
}

# Tempo em segundos (900 segundos = 15 minutos)
INTERVALO = 900
# ==================================================================


async def enviar_e_apagar():
    await bot.wait_until_ready()
    # Guarda a última mensagem enviada em cada canal para poder apagar depois
    ultimas_mensagens = {}

    while not bot.is_closed():
        for canal_id, mensagens in CANAIS_E_MENSAGENS.items():
            canal = bot.get_channel(canal_id)
            if canal and mensagens:
                try:
                    # Pega a primeira mensagem da lista daquele canal
                    texto_atual = mensagens[0]

                    # Envia a nova mensagem
                    nova_mensagem = await canal.send(texto_atual)

                    # Apaga a mensagem anterior daquele canal específico, se existir
                    if canal_id in ultimas_mensagens:
                        try:
                            await ultimas_mensagens[canal_id].delete()
                        except discord.HTTPException:
                            pass

                    # Salva a mensagem atual como a última enviada
                    ultimas_mensagens[canal_id] = nova_mensagem

                    # Rotaciona a lista para a próxima mensagem daquele canal ir na próxima rodada
                    mensagens.append(mensagens.pop(0))

                except Exception as e:
                    print(f"Erro no canal {canal_id}: {e}")

        await asyncio.sleep(INTERVALO)


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}!")
    bot.loop.create_task(enviar_e_apagar())


# Puxa o token de forma segura das variáveis do Render
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)