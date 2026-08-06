import asyncio
import os
import discord
from discord.ext import commands
from aiohttp import web

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== CONFIGURAÇÕES DOS CANAIS ====================
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

INTERVALO = 3600  # 60 minutos (1 hora)
# ==================================================================


async def enviar_e_apagar():
    await bot.wait_until_ready()
    ultimas_mensagens = {}

    while not bot.is_closed():
        for canal_id, mensagens in CANAIS_E_MENSAGENS.items():
            canal = bot.get_channel(canal_id)
            if canal and mensagens:
                try:
                    texto_atual = mensagens[0]
                    
                    # Envia a mensagem incluindo o rótulo/flag de Mensagem Automática
                    nova_mensagem = await canal.send(
                        content=texto_atual, 
                        flags=discord.MessageFlags(crossposted=True)
                    )

                    if canal_id in ultimas_mensagens:
                        try:
                            await ultimas_mensagens[canal_id].delete()
                        except discord.HTTPException:
                            pass

                    ultimas_mensagens[canal_id] = nova_mensagem
                    mensagens.append(mensagens.pop(0))

                except Exception as e:
                    print(f"Erro no canal {canal_id}: {e}")

        await asyncio.sleep(INTERVALO)


# Servidor web simples para o Render (Web Service Live)
async def handle(request):
    return web.Response(text="Bot do Discord rodando com sucesso!")


async def start_web_server():
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}!")
    bot.loop.create_task(enviar_e_apagar())


async def main():
    await start_web_server()
    TOKEN = os.getenv("DISCORD_TOKEN")
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
