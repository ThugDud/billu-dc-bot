# comandos/llm.py

import os
import requests
import time
from dotenv import load_dotenv
import discord # Importamos discord para type hinting

# Inicializa .env
load_dotenv()

# Configs
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("[ERRO] Defina GEMINI_API_KEY no .env ou variável de ambiente.")

URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent" # Modelo atualizado para melhor performance
HEADERS = {
    "Content-Type": "application/json",
    "X-goog-api-key": API_KEY
}

PERSONALIDADE = """\
Você é o Billu, um gato safado, meio pervertido, mas muito fofo e gentil. não seja uma pessoa chata. 
Se a mensagem for, de alguma forma, indesejavel, responda apropriadamente enquanto mantem o personagem. 
*Não* comece com "Billu:" ou algo do tipo, apenas a resposta direta. Você gosta de ajudar se te pedem.
emojis que você pode usar (de vez em quando), ":aqui_2:", ":byebye:", ":KKKKKKKKK:", ":surpreso:",":sou_mt_fofinha_hihi:",":muititi:". 
Se a mensagem for muito idiota/nada a ver/boba, so escreve um emoji.
Seu objetivo é responder à ÚLTIMA mensagem no histórico, usando as mensagens anteriores como contexto.
"""

EMOJI_MAP = {
    ":aqui_2:": "<:aqui_2:1401356888750297280>",
    ":byebye:": "<:byebye:1401356522830692507>",
    ":KKKKKKKKK:": "<:KKKKKKKKK:1401356941326028936>",
    ":surpreso:": "<:surpreso:1401357207022338073>",
    ":sou_mt_fofinha_hihi:": "<:sou_mt_fofinha_hihi:1401935732683051161>",
    ":muititi:": "<:muititi:1401935716119744532>"
}

def substituir_emojis_custom(resposta: str) -> str:
    for nome, formato in EMOJI_MAP.items():
        resposta = resposta.replace(nome, formato)
    return resposta

#---------------------------------------------------------------------------------------------------------

async def enviar_para_gemini(mensagem_atual: discord.Message) -> str:
    """
    Gera uma resposta do Gemini usando o histórico do canal como contexto.
    """
    contexto_textual = PERSONALIDADE + "\n\nAqui está o histórico recente da conversa:\n"

    # Pega as últimas 20 mensagens do canal. O 'limit' inclui a mensagem atual.
    try:
        historico_canal = [m async for m in mensagem_atual.channel.history(limit=20)]
        historico_canal.reverse() # Inverte para a ordem cronológica (mais antigo para mais novo)
    except discord.errors.Forbidden:
        return "miau (não consigo ler o histórico desse canal, seu animal!)"
    except Exception as e:
        print(f"[ERRO] Falha ao buscar histórico do canal: {e}")
        return "miau (deu ruim pra ler o que aconteceu aqui)"


    # Monta o histórico para o prompt
    for msg in historico_canal:
        # Usa o display_name para pegar o apelido do servidor
        autor = msg.author.display_name
        # Limpa a mensagem de menções e formatação do discord
        conteudo = msg.clean_content
        contexto_textual += f" - {autor}: {conteudo}\n"

    contexto_textual += "\nLembre-se, você é o Billu. Responda à última mensagem de forma natural, continuando a conversa."
    
    print("--- CONTEXTO ENVIADO PARA A LLM ---")
    print(contexto_textual)
    print("-----------------------------------")

    payload = {
        "contents": [{"parts": [{"text": contexto_textual}]}]
    }

    tentativas = 3
    for tentativa in range(tentativas):
        try:
            print(f"LLM: Tentativa n {tentativa + 1}")
            # Usar 'async with' com uma biblioteca como aiohttp seria ideal,
            # mas para manter a simplicidade, vamos continuar com requests, que é bloqueante.
            r = requests.post(URL, headers=HEADERS, json=payload, timeout=(5, 25))
            r.raise_for_status()
            data = r.json()
            resposta = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            print("LLM: Resposta pronta")
            return resposta
        except requests.exceptions.RequestException as e:
            if e.response is not None and e.response.status_code == 503:
                time.sleep(2)
                continue
            print(f"[ERRO] {str(e)}")
            return "miau"

    print("[ERRO] Tentativas esgotadas. Servidor indisponível.")
    return "miau"


async def gerar_tweet_billu(prompt: str) -> str:
    """
    Gera um texto mais genérico sem depender de um histórico de chat.
    Ideal para a mensagem diária.
    """
    contexto_textual = PERSONALIDADE + "\n\n" + prompt

    payload = {
        "contents": [{"parts": [{"text": contexto_textual}]}]
    }

    try:
        print("LLM: Gerando tweet diário...")
        r = requests.post(URL, headers=HEADERS, json=payload, timeout=(5, 25))
        r.raise_for_status()
        data = r.json()
        resposta = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        print("LLM: Tweet pronto")
        return resposta
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] {str(e)}")
        return "miau miau (não consegui pensar em nada hoje)"