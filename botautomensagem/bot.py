import asyncio
import os
import discord
import aiohttp
from discord.ext import commands
from aiohttp import web

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== CONFIGURAÇÕES ====================
CANAL_VERIFICACAO_ID = 1525114015238455457
CARGO_ID = 1525115321516560445
SERVIDOR_ID = 1510067989104427211  # ID do seu servidor

CLIENT_ID = "1533627256524509286"
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")  # Puxa do Render com segurança
REDIRECT_URI = "https://bot-verificacao-baz1.onrender.com/callback"

# Configuração dos canais de envio automático de mensagens
CANAIS_E_MENSAGENS = {
    1526730887885226027: [
        "Entrega Automática!! Comprou? Chegou!! || @everyone @.gg/qzzcomunityy @here ||",
    ],
    1514333562252300481: [
        "Proxy ON!! Android e Ios!! || @everyone @.gg/qzzcomunityy @here ||",
    ],
    1514332751317172236: [
        "Proxy ON!! Android e Ios!! || @everyone @.gg/qzzcomunityy @here ||",
    ],
}

INTERVALO = 3600  # 60 minutos (1 hora)
# ========================================================


# Função de envio e limpeza de mensagens automáticas
async def enviar_e_apagar():
    await bot.wait_until_ready()
    ultimas_mensagens = {}

    while not bot.is_closed():
        for canal_id, mensagens in CANAIS_E_MENSAGENS.items():
            canal = bot.get_channel(canal_id)
            if canal and mensagens:
                try:
                    texto_atual = mensagens[0]
                    
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


# Função para dar o cargo automaticamente ao usuário verificado
async def dar_cargo(user_id):
    guild = bot.get_guild(SERVIDOR_ID)
    if guild:
        try:
            member = await guild.fetch_member(user_id)
            role = guild.get_role(CARGO_ID)
            if member and role:
                await member.add_roles(role)
                print(f"Sucesso: Cargo entregue para o usuário {user_id}!")
        except Exception as e:
            print(f"Erro ao entregar o cargo para o usuário {user_id}: {e}")


# Rota web que recebe o código do Discord após o usuário autorizar no site
async def handle_callback(request):
    code = request.query.get("code")
    if not code:
        return web.Response(text="Erro: Nenhum código de autorização recebido.", status=400)

    # Troca o código pelo Token de Acesso
    async with aiohttp.ClientSession() as session:
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        async with session.post("https://discord.com/api/oauth2/token", data=data, headers=headers) as resp:
            token_data = await resp.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                return web.Response(text=f"Erro ao autenticar com o Discord: {token_data}", status=400)
        
        # Pega o ID do usuário que autorizou
        user_headers = {"Authorization": f"Bearer {access_token}"}
        async with session.get("https://discord.com/api/users/@me", headers=user_headers) as resp:
            user_data = await resp.json()
            user_id = user_data.get("id")

    if user_id:
        # Atribui o cargo no servidor
        await dar_cargo(int(user_id))
        return web.Response(text="Verificação concluída com sucesso! Pode fechar esta aba e voltar ao Discord.")
    
    return web.Response(text="Erro ao identificar o usuário.", status=400)


# Classe do Botão de Verificação (Aponta para o site no Vercel)
class BotaoVerificacao(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        url_site_vercel = "https://qzzcommunity.vercel.app/"
        self.add_item(
            discord.ui.Button(
                label="Verificar Agora",
                style=discord.ButtonStyle.secondary,
                url=url_site_vercel,
            )
        )


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}!")
    bot.add_view(BotaoVerificacao())
    bot.loop.create_task(enviar_e_apagar())


# Comando para enviar o painel no canal configurado
@bot.command()
@commands.has_permissions(administrator=True)
async def painel(ctx):
    canal = bot.get_channel(CANAL_VERIFICACAO_ID)
    if not canal:
        await ctx.send("Canal de verificação não encontrado!")
        return

    embed = discord.Embed(
        title="Sistema de Verificação",
        description=(
            "Para acessar todos os canais do servidor e participar da comunidade, "
            "você precisa se verificar primeiro.\n\n**Como funciona:**\n"
            "• Clique no botão abaixo\n• Complete a autorização\n• Feche a aba do"
            " navegador e volte ao Discord!\n\nApós a verificação, você terá"
            " acesso completo ao servidor!"
        ),
        color=discord.Color.blue(),
    )
    embed.set_footer(text="Proteção e Segurança do Servidor")
    embed.set_image(
        url=(
            "https://cdn.discordapp.com/attachments/1491626518219198639/1533630932785827850/ChatGPT_Image_2_de_ago._de_2026_21_21_33.png?ex=6a71309b&is=6a6fdf1b&hm=0d4b7d09c69feb7d2b1d87229aeadfbb1b69feb9a2375249b79371d8fd59dc7b&"
        )
    )

    await canal.send(embed=embed, view=BotaoVerificacao())
    await ctx.send("Painel de verificação enviado com sucesso!", ephemeral=True)


# Servidor web integrado para o Render (gerencia a home e a rota de callback do OAuth)
async def start_web_server():
    app = web.Application()
    app.add_routes([
        web.get("/", lambda r: web.Response(text="Bot do Discord rodando com sucesso!")),
        web.get("/callback", handle_callback)
    ])
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main():
    await start_web_server()
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("Erro: Token não configurado nas variáveis de ambiente!")
        return
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
