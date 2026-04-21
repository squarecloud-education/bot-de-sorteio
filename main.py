import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os, random

load_dotenv(".env", override=True)

MANAGER_ID = int(os.getenv("CARGO_MANAGER"))

def is_manager(interaction:discord.Interaction):
    return any(r.id == MANAGER_ID for r in interaction.user.roles)

async def checar_manager(interaction:discord.Interaction):
    if is_manager(interaction):
        return True
    
    await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
    return False

intents = discord.Intents.all()

bot = commands.Bot("!", intents=intents)

sorteios_ativos = {}

class SorteioDados:
    def __init__(
            self,
            premio,
            duracao_segundos,
            qtd_ganhadores,
            criador,
            canal
    ):
        self.premio = premio
        self.duracao_segundos = duracao_segundos
        self.qtd_ganhadores = qtd_ganhadores
        self.criador = criador
        self.canal = canal
        self.participantes = set()
        self.encerra_em = datetime.utcnow() + timedelta(seconds=duracao_segundos)
        self.mensagem = None
        self.encerrado = False
    
    @property
    def segundos_restantes(self):
        delta = self.encerra_em - datetime.utcnow()
        return max(0, int(delta.total_seconds()))

    def tempo_formatado(self):
        s = self.segundos_restantes
        if s >= 3600:
            h, resto = divmod(s, 3600)
            m, s = divmod(resto, 60)
            return f"{h}h {m}m s{s}"
        elif s >= 60:
            m, s = divmod(s, 60)
            return f"{m}m {s}s"
        
        return f"{s}s"
    
    def build_embed(self):
        cor = discord.Color.gold() if not self.encerrado else discord.Color.dark_gray()
        embed = discord.Embed(title="Sorteio 🎉", description=f"**Prêmio:** {self.premio}", color=cor)

        embed.add_field(name="👥 Participantes", value=str(len(self.participantes)), inline=True)
        embed.add_field(name="🏆 Ganhadores", value=str(self.qtd_ganhadores), inline=True)
        
        if not self.encerrado:
            embed.add_field(name="⏳ Encerra em", value=self.tempo_formatado())

        embed.set_footer(text=f"Criado por {self.criador.display_name}")
        return embed

class SorteioView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Participar", style=discord.ButtonStyle.green, custom_id="sorteio:participar")
    async def participar(self, interaction:discord.Interaction, button):
        msg_id = interaction.message.id
        sorteio = sorteios_ativos.get(msg_id)

        if sorteio is None:
            await interaction.response.send_message("Este sorteio não está mais ativo.", ephemeral=True)
            return
        
        if sorteio.encerrado:
            await interaction.response.send_message("Este sorteio já foi encerrado!", ephemeral=True)
            return
        
        uid = interaction.user.id

        if uid in sorteio.participantes:
            sorteio.participantes.discard(uid)
            await interaction.response.send_message("Você saiu do sorteio.", ephemeral=True)
        else:
            sorteio.participantes.add(uid)
            await interaction.response.send_message("Você entrou no sorteio! Boa sorte.", ephemeral=True)
        
        await interaction.message.edit(embed=sorteio.build_embed())
    
@tasks.loop(seconds=10)
async def tick_sorteios():
    encerrados = []

    for msg_id, sorteio in sorteios_ativos.items():
        if sorteio.encerrado:
            continue
        
        if sorteio.segundos_restantes <= 0:
            await encerrar_sorteio(sorteio)
            encerrados.append(msg_id)
        else:
            if sorteio.mensagem:
                try:
                    await sorteio.mensagem.edit(embed=sorteio.build_embed())
                except discord.NotFound:
                    encerrados.append(msg_id)
    
    for msg_id in encerrados:
        sorteios_ativos.pop(msg_id)

async def encerrar_sorteio(sorteio:SorteioDados):
    sorteio.encerrado = True

    if not sorteio.participantes:
        resultado = "Ninguém participou do sorteio 😥"
        ganhadores_mencoes = ""
    else:
        pool = list(sorteio.participantes)
        qtd = min(sorteio.qtd_ganhadores, len(pool))
        ganhadores_ids = random.sample(pool, qtd)

        ganhadores_mencoes = " ".join(f"<@{uid}>" for uid in ganhadores_ids)
        resultado = f"🏆 **Parabéns aos ganhadores:** {ganhadores_mencoes}"
    
    embed = sorteio.build_embed()
    embed.title = "SORTEIO ENCERRADO"
    embed.add_field(name="Resultado", value=resultado, inline=False)

    view = discord.ui.View()
    if sorteio.mensagem:
        try:
            await sorteio.mensagem.edit(embed=embed, view=view)
        except discord.NotFound:
            pass
    
    await sorteio.canal.send(
        f"🎉 O sorteio de **{sorteio.premio}** acabou!\n{resultado}"
    )

_UNIDADES = {"s":1, "m":60, "h":3600, "d":86400}
_DURACAO_MIN = 10
_DURACAO_MAX = _UNIDADES["d"] * 15

def parsear_duracao(text:str):
    texto = text.strip().lower()
    if not texto:
        return None

    unidade = texto[-1]
    if unidade not in _UNIDADES:
        return None
    
    try:
        valor = int(text[:-1])
    except ValueError:
        return None
    
    if valor <= 0:
        return None

    return valor * _UNIDADES[unidade]

@bot.tree.command(name="sorteio", description="Inicia um novo sorteio")
@app_commands.describe(
    premio="O que será sorteado",
    duracao = "Duração: 30s, 10m, 2h, 1d (s=segundos, m=minutos, h=horas, d=dias)",
    ganhadores = "Quantidade de ganhadores (padrão: 1)"
)
async def sorteio(interaction:discord.Interaction, premio:str, duracao:str, ganhadores:app_commands.Range[int, 1, 20]):
    if not await checar_manager(interaction):
        return
    
    segundos = parsear_duracao(duracao)

    if segundos is None:
        await interaction.response.send_message("Formato de duração inválido.", ephemeral=True)
        return True

    if segundos < _DURACAO_MIN:
        await interaction.response.send_message(f"A duração mínima é {_DURACAO_MIN}s", ephemeral=True)
        return

    if segundos > _DURACAO_MAX:
        await interaction.response.send_message(f"A duração máxima é {_DURACAO_MAX}d")
        return
    
    await interaction.response.defer()

    sorteio = SorteioDados(premio, segundos, ganhadores, interaction.user, interaction.channel)
    view = SorteioView()
    msg = await interaction.followup.send(embed=sorteio.build_embed(), view=view)

    sorteio.mensagem = msg
    sorteios_ativos[msg.id] = sorteio

    if not tick_sorteios.is_running():
        tick_sorteios.start()

@bot.tree.command(name="cancelar_sorteio", description="Cancela um sorteio ativo")
async def cancelar(interaction:discord.Interaction):
    if not await checar_manager(interaction):
        return
    
    alvo = next((s for s in sorteios_ativos.values() if s.canal == interaction.channel_id and not s.encerrado), None)

    if alvo is None:
        await interaction.response.send_message("Não há sorteio ativo neste canal.", ephemeral=True)
        return
    
    alvo.encerrado = True
    if alvo.mensagem:
        embed = alvo.build_embed()
        embed.title = "SORTEIO CANCELADO"
        await alvo.mensagem.edit(embed=embed, view=discord.ui.View())
    
    sorteios_ativos.pop(alvo.mensagem.id, None)
    await interaction.response.send_message("Sorteio cancelado", ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(SorteioView())

    await bot.tree.sync()
    print(f"Bot online como {bot.user}!")

bot.run(os.getenv("TOKEN"))