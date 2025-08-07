import os
import discord
import asyncio

from discord import app_commands, Interaction
from comandos import gerais, gemini
from comandos.utils import log_erro
from dotenv import load_dotenv
from pathlib import Path

import json
import time, datetime

CONTADOR_PATH = Path(__file__).parent / "comandos" / "historico" / "contador.json"

if os.path.exists(CONTADOR_PATH):
    with open(CONTADOR_PATH, "r") as f:
        contador_por_chat = json.load(f)
        # converte as chaves de string pra int
        contador_por_chat = {int(k): v for k, v in contador_por_chat.items()}
        print(contador_por_chat)
else:
    contador_por_chat = {}

# função pra salvar
def salvar_contador():
    with open(CONTADOR_PATH, "w") as f:
        json.dump(contador_por_chat, f)

load_dotenv()

token = os.getenv("BOT_API_KEY")
#Chats que são permitidos respostas automaticas do billu
#Chat_permitidos: Culto do billu - "chat", "comandos", "midia" | bleff - "geral"
#Chat_spam: Culto do billu - "chat", "midia" | bleff - "chat"
#chat_fodaci: Culto do billu - "gpt" | bleff - "bumbum"

chat_fodaci = [1315799212595744878]
chat_ilegal = [1315774240787796048, 1396974089293398127, 1395813079887122584, 1395459917271404746, 1386791850001563648]
HOLDER = 20

# Horário alvo (pode ajustar)
HORARIO_ALVO = "07:00"

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
            try:
                await message.channel.typing()
                print(f"fazendo aquisição na LLM, a: {msg.author}, m: {msg.content}")
                resposta = enviar_para_gemini(msg.content, str(msg.author))
                resposta = substituir_emojis_custom(resposta)
                print("resposta pronta")
                
                if len(resposta) > MAX_LEN:
                    resposta = resposta[:MAX_LEN - 20] + "\n..."
                
                await msg.channel.send(resposta)
                print("mensagem enviada")
            except Exception as e:
                log_erro(e, contexto="responder_billu()")
                print(f"[ERRO] Falha ao responder ({type(e)}): {e}")
        
        if message.reference and message.reference.resolved.author == self.user:
            await responder_billu(message)

        # -- chat fodaci: resposta automatica sem pré-requisito
        elif message.channel.id in chat_fodaci:
            await responder_billu(message)

        # --- modo 1: resposta direta quando alguém menciona "billu"
        elif "billu" in message.content.lower():
            await responder_billu(message)

        # --- modo 2: chat_spam -> responde automaticamente após 10 mensagens
        elif message.channel.id not in chat_ilegal:
            contador = contador_por_chat.get(message.channel.id, 0) + 1
            contador_por_chat[message.channel.id] = contador
            salvar_contador()
            print(f"[DEBUG] Contador SPAM do canal {message.channel.name} (ID: {message.channel.id}): {contador}")
            if contador >= HOLDER:
                contador_por_chat[message.channel.id] = 0
                salvar_contador()
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
            name="Agua de beber"
        )
        await self.change_presence(
            status=discord.Status.idle,  # online, idle, dnd, invisible
            activity=atividade
        )

async def dailybillu(bot):
    canal = bot.get_channel(1315773798980784210)

    from comandos.llm import enviar_para_gemini, substituir_emojis_custom

    MAX_LEN = 2000

    try:
        resposta = enviar_para_gemini("você agora vai fazer um tweet! escreva sobre algum topico/assunto/problema/fodase. Termine com hastags fodas. Não faça metalinguagem com esse texto.", "developer")
        resposta = substituir_emojis_custom(resposta)
        
        if len(resposta) > MAX_LEN:
            resposta = resposta[:MAX_LEN - 20] + "\n..."   

        await canal.send(resposta)
        print("mensagem diaria enviada")
    except Exception as e:
        log_erro(e, contexto="dailybillu()")
        print(f"[ERRO] Falha ao enviar mensagem diaria ({type(e)}): {e}")

async def watchdog(bot):
    while True:
        await asyncio.sleep(60)
        if bot.is_closed():
            print("[!!] bot aparentemente caiu, reiniciando...")
            os._exit(1)
    
async def contador_diario(bot):
    ultimo_dia_executado = None

    while True:
        agora = datetime.datetime.now()
        hora_atual = agora.strftime("%H:%M")
        dia_atual = agora.date()

        if hora_atual == HORARIO_ALVO and dia_atual != ultimo_dia_executado:
            await dailybillu(bot)
            ultimo_dia_executado = dia_atual
        await asyncio.sleep(30)

async def main():
    bot = MyBot()
    asyncio.create_task(watchdog(bot))  # <-- safe e bonito
    asyncio.create_task(contador_diario(bot)) # <-- eu acho que safe e bonito
    await bot.start(token)

asyncio.run(main())
