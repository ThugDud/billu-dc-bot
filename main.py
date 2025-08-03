import os
import discord
import asyncio
from discord import app_commands, Interaction
from comandos import gerais, gemini
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("BOT_API_KEY")
#Chats que são permitidos respostas automaticas do billu
#Chat_permitidos: Culto do billu - "chat", "comandos", "midia" | bleff - "geral"
#Chat_spam: Culto do billu - "chat", "desabafo", "midia" | bleff - "chat"
#chat_fodaci: Culto do billu - "gpt" | bleff - "bumbum"

chat_permitido = [1315756598223962122, 1315758567793365042, 1315758951786348687, 881222601043742754]
chat_spam = [1315756598223962122, 1068101736302133268, 1315758951786348687, 881222601043742754]
chat_fodaci = [1315799212595744878]
contador_por_chat = {}

class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self): # odeio função assíncrona
        await gerais.registrar(self)
        await gemini.registrar(self)
        await self.tree.sync()

    async def on_message(self, message):
    # ignora mensagem do próprio bot
        if message.author == self.user:
            return

        from comandos.llm import enviar_para_gemini, substituir_emojis_custom  # importa aqui pra evitar import circular
        loop = asyncio.get_running_loop()
        
        MAX_LEN = 2000

        async def responder_billu(msg):
            await message.channel.typing()
            print("fazendo aquisição na LLM")
            resposta = await loop.run_in_executor(None, enviar_para_gemini, msg.content, str(msg.author))
            resposta = substituir_emojis_custom(resposta)
            print("resposta pronta")
            
            if len(resposta) > MAX_LEN:
                resposta = resposta[:MAX_LEN - 20] + "\n..."
            
            await msg.channel.send(resposta)

        # -- chat fodaci: resposta automatica sem pré-requisito
        if message.channel.id in chat_fodaci:
            await responder_billu(message)

        # --- modo 1: resposta direta quando alguém menciona "billu"
        if message.channel.id in chat_permitido and "billu" in message.content.lower():
            await responder_billu(message)

        # --- modo 2: chat_spam -> responde automaticamente após 10 mensagens
        if message.channel.id in chat_spam:
            contador = contador_por_chat.get(message.channel.id, 0) + 1
            contador_por_chat[message.channel.id] = contador
            print(f"[DEBUG] Contador SPAM do canal {message.channel.name} (ID: {message.channel.id}): {contador}")
            if contador >= 15:
                contador_por_chat [message.channel.id] = 0
                await responder_billu(message)

    async def on_disconnect(self):
        print("[!] Billu caiu da conexão com discord")
    
    async def on_resumed(self):
        print("[✓] Billu desfudeu e se reconectou")

    async def on_ready(self):
        print(f"o bot {self.user} ligou porra, LETSGOO")

        # muda status e atividade
        atividade = discord.Activity(
            type=discord.ActivityType.listening,  # jogando, ouvindo, assistindo, etc
            name="Mama's Boy"
        )
        await self.change_presence(
            status=discord.Status.idle,  # online, idle, dnd, invisible
            activity=atividade
        )
    

bot = MyBot()

bot.run(token)