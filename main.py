# main.py (partes alteradas)

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

# O sistema de contador de mensagens continua igual.
CONTADOR_PATH = Path(__file__).parent / "comandos" / "historico" / "contador.json"

if os.path.exists(CONTADOR_PATH):
    with open(CONTADOR_PATH, "r") as f:
        contador_por_chat = json.load(f)
        contador_por_chat = {int(k): v for k, v in contador_por_chat.items()}
        print(contador_por_chat)
else:
    contador_por_chat = {}

def salvar_contador():
    with open(CONTADOR_PATH, "w") as f:
        json.dump(contador_por_chat, f)

load_dotenv()

token = os.getenv("BOT_API_KEY")

chat_fodaci = [1315799212595744878]
chat_ilegal = [1315774240787796048, 1396974089293398127, 1395813079887122584, 1395459917271404746, 1386791850001563648]
HOLDER = 20
HORARIO_ALVO = "07:00"

class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await gerais.registrar(self)
        await gemini.registrar(self)
        await self.tree.sync()

    async def on_message(self, message):
        if message.author == self.user:
            return

        # A importação agora é de duas funções
        from comandos.llm import enviar_para_gemini, substituir_emojis_custom
        
        MAX_LEN = 2000

        async def responder_billu(msg: discord.Message): # msg agora é do tipo discord.Message
            try:
                await message.channel.typing()
                print(f"fazendo aquisição na LLM, a: {msg.author}, m: {msg.content}")
                
                # A chamada foi simplificada e agora precisa de 'await'
                resposta = await enviar_para_gemini(msg) 
                
                resposta = substituir_emojis_custom(resposta)
                print("resposta pronta")
                
                if len(resposta) > MAX_LEN:
                    resposta = resposta[:MAX_LEN - 20] + "\n..."
                
                await msg.channel.send(resposta)
                print("mensagem enviada")
            except Exception as e:
                log_erro(e, contexto="responder_billu()")
                print(f"[ERRO] Falha ao responder ({type(e)}): {e}")
        
        # O resto da lógica de on_message permanece a mesma
        if message.reference and message.reference.resolved.author == self.user:
            await responder_billu(message)

        elif message.channel.id in chat_fodaci:
            await responder_billu(message)

        elif "billu" in message.content.lower():
            await responder_billu(message)

        elif message.channel.id not in chat_ilegal:
            contador = contador_por_chat.get(message.channel.id, 0) + 1
            contador_por_chat[message.channel.id] = contador
            salvar_contador()
            print(f"[DEBUG] Contador SPAM do canal {message.channel.name} (ID: {message.channel.id}): {contador}")
            if contador >= HOLDER:
                contador_por_chat[message.channel.id] = 0
                salvar_contador()
                await responder_billu(message)

    # ... (on_disconnect, on_resumed, on_ready permanecem iguais) ...
    async def on_disconnect(self):
        print("[!] Billu caiu da conexão com discord")
    
    async def on_resumed(self):
        print("[✓] Billu desfudeu e se reconectou")

    async def on_ready(self):
        print(f"o bot {self.user} ligou porra, LETSGOO")

        atividade = discord.Activity(
            type=discord.ActivityType.listening,
            name="O Pirata - Ave Sangria"
        )
        await self.change_presence(
            status=discord.Status.idle,
            activity=atividade
        )


async def dailybillu(bot):
    canal = bot.get_channel(1315773798980784210)

    # Importamos a nova função específica para isso
    from comandos.llm import gerar_tweet_billu, substituir_emojis_custom

    MAX_LEN = 2000

    try:
        # Usamos a nova função que não precisa de contexto de chat
        prompt = "você agora vai fazer um tweet! escreva sobre algum topico/assunto/problema/fodase. Termine com hastags fodas. Não faça metalinguagem com esse texto."
        resposta = await gerar_tweet_billu(prompt)
        
        resposta = substituir_emojis_custom(resposta)
        
        if len(resposta) > MAX_LEN:
            resposta = resposta[:MAX_LEN - 20] + "\n..."   

        await canal.send(resposta)
        print("mensagem diaria enviada")
    except Exception as e:
        log_erro(e, contexto="dailybillu()")
        print(f"[ERRO] Falha ao enviar mensagem diaria ({type(e)}): {e}")

# ... (watchdog, contador_diario, e main permanecem iguais) ...
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
    asyncio.create_task(watchdog(bot))
    asyncio.create_task(contador_diario(bot))
    await bot.start(token)

asyncio.run(main())