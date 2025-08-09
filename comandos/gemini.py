# comandos/gemini.py
import os
from discord import app_commands, Interaction
# apagar_historico foi removido, não é mais necessário
from dotenv import load_dotenv

load_dotenv()

async def registrar(bot):
    # O comando @bot.tree.command(name="apagar-historico"...) foi removido.
    # Você pode adicionar novos comandos aqui no futuro, se quiser.
    print("[Comandos Gemini] Nenhum comando de barra para registrar.")
    pass