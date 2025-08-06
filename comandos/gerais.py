import os
from discord import app_commands, Interaction
import subprocess
from dotenv import load_dotenv

load_dotenv()

# função que registra os comandos no bot
async def registrar(bot):
    @bot.tree.command(name="ola-mundo", description="sei la")
    async def olamundo(interaction: Interaction):
        await interaction.response.send_message(f"Ola {interaction.user.id}, seu pau no cu desgraçado")

    @bot.tree.command(name="ping")
    async def ping(interaction: Interaction):
        await interaction.response.send_message("Pong!")

    @bot.tree.command(name="debug")
    async def debug(interaction: Interaction):
        
        SEU_ID = os.getenv("AUTHOR_ID")
        
        if interaction.user.id != int(SEU_ID):
            await interaction.response.send_message("Sem permissão, seu animal.", ephemeral=True)
            return

        elif interaction.user.id == int(SEU_ID):
            await interaction.response.send_message(subprocess.run(['sensors'], capture_output=True, text=True), ephemeral=True)