from discord import app_commands, Interaction

# função que registra os comandos no bot
async def registrar(bot):
    @bot.tree.command(name="ola-mundo", description="sei la")
    async def olamundo(interaction: Interaction):
        await interaction.response.send_message(f"Ola {interaction.user.id}, seu pau no cu desgraçado")
