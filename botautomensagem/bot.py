import asyncio
import os
import discord
from discord.ext import commands, tasks
from aiohttp import web

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== CONFIGURAÇÕES DOS 3 CANAIS ====================
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

# Dicionário global para guardar a última mensagem enviada em cada canal
ultimas_mensagens = {}
# ==================================================================


# Tarefa automática oficial (a cada 15 minutos)
@tasks.loop(minutes=15)
async def enviar_e_apagar():
  print("🔄 Executando o ciclo de automensagens...")
  for canal_id, mensagens in CANAIS_E_MENSAGENS.items():
    canal = bot.get_channel(canal_id)
    if canal:
      try:
        texto_atual = mensagens[0]
        nova_mensagem = await canal.send(texto_atual)
        print(f"✅ Mensagem enviada no canal {canal_id}")

        # Apaga a mensagem anterior se existir
        if canal_id in ultimas_mensagens:
          try:
            await ultimas_mensagens[canal_id].delete()
          except discord.HTTPException:
            pass

        ultimas_mensagens[canal_id] = nova_mensagem
        mensagens.append(mensagens.pop(0))

      except Exception as e:
        print(f"❌ Erro ao enviar no canal {canal_id}: {e}")
    else:
      print(
          f"⚠️ Canal {canal_id} não encontrado! Verifique se o ID está correto"
          " e se o bot está no servidor."
      )


@enviar_e_apagar.before_loop
async def before_enviar_e_apagar():
  # Aguarda o bot ficar totalmente pronto antes de iniciar o loop pela primeira vez
  await bot.wait_until_ready()
  print("⏳ Bot pronto! A primeira rodada de mensagens automáticas vai rodar agora.")


# Servidor web simples para o Render
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
  # Inicia o loop de tarefas se já não estiver rodando
  if not enviar_e_apagar.is_running():
    enviar_e_apagar.start()


@bot.command()
async def testar(ctx):
  await ctx.send("Pong! O bot está ativo e respondendo aos comandos.")


async def main():
  await start_web_server()
  TOKEN = os.getenv("DISCORD_TOKEN")
  if not TOKEN:
    print(
        "Erro: A variável de ambiente DISCORD_TOKEN não foi encontrada no"
        " Render!"
    )
    return
  await bot.start(TOKEN)


if __name__ == "__main__":
  asyncio.run(main())
