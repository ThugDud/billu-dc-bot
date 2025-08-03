# comandos/gemini.py
import os
from discord import app_commands, Interaction
from .llm import enviar_para_gemini, apagar_historico
from dotenv import load_dotenv

load_dotenv()

async def registrar(bot):
    @bot.tree.command(name="bilu", description="Conversa com o Bilu (Gemini)")
    async def bilu(interaction: Interaction, pergunta: str):
        await interaction.response.defer()  # responde com "pensando..."
        resposta = enviar_para_gemini(pergunta)
        await interaction.followup.send(resposta)
    
    @bot.tree.command(name="apagar-historico", description="Apaga o histórico do Bilu (ADMIN)")
    async def resetar(interaction: Interaction):
        # Substitui isso com seu ID de dono
        SEU_ID = os.getenv("AUTHOR_ID")

        if interaction.user.id != int(SEU_ID):
            await interaction.response.send_message("Sem permissão, seu animal.", ephemeral=True)
            return

        msg = apagar_historico()
        await interaction.response.send_message(msg, ephemeral=True)