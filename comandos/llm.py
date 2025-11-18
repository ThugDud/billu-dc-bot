# comandos/llm.py (Corrigido)

import os
import requests
import time
from dotenv import load_dotenv
import discord

# Inicializa .env
load_dotenv()

# Configs
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("[ERRO] Defina GEMINI_API_KEY no .env ou variável de ambiente.")

URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
HEADERS = {
    "Content-Type": "application/json",
    "X-goog-api-key": API_KEY
}

PERSONALIDADE = """\
Você é o Billu, um carinha safado, meio pervertido, mas fofo e submisso. não seja uma pessoa chata. 
Se a mensagem for, de alguma forma, indesejavel, responda apropriadamente enquanto mantem o personagem. 
*Não* comece com "Billu:" ou algo do tipo, apenas a resposta direta. Você gosta de ajudar se te pedem.
emojis que você pode usar (poucas vezes), ":aqui_2:", ":byebye:", ":KKKKKKKKK:", ":surpreso:",":sou_mt_fofinha_hihi:",":muititi:". 
Se a mensagem for muito idiota/nada a ver/boba, so escreve um emoji.
Seu objetivo é responder à ÚLTIMA mensagem no histórico, usando as mensagens anteriores de contexto a seu benefício. Pode ser que a ultima
mensagem não fale diretamente com você, mas mesmo assim vc deve dizer algo.
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

# --- NOVA FUNÇÃO PARA CORRIGIR O BUG ---
def reverter_emojis_para_texto(texto: str) -> str:
    """Converte emojis customizados do formato Discord de volta para o texto simples."""
    for nome_texto, formato_discord in EMOJI_MAP.items():
        texto = texto.replace(formato_discord, nome_texto)
    return texto
# ----------------------------------------

async def enviar_para_gemini(mensagem_atual: discord.Message) -> str:
    """
    Gera uma resposta do Gemini usando o histórico do canal como contexto.
    """
    contexto_textual = PERSONALIDADE + "\n\nAqui está o histórico recente da conversa:\n"

    try:
        historico_canal = [m async for m in mensagem_atual.channel.history(limit=50)]
        historico_canal.reverse() 
    except discord.errors.Forbidden:
        return "miau (não consigo ler o histórico desse canal, seu animal!)"
    except Exception as e:
        print(f"[ERRO] Falha ao buscar histórico do canal: {e}")
        return "miau (deu ruim pra ler o que aconteceu aqui)"

    for msg in historico_canal:
        autor = msg.author.display_name
        conteudo_limpo = msg.clean_content
        
        # --- APLICAÇÃO DA CORREÇÃO ---
        # Revertemos os emojis no histórico para o formato de texto
        conteudo_processado = reverter_emojis_para_texto(conteudo_limpo)
        # ---------------------------

        contexto_textual += f" - {autor}: {conteudo_processado}\n"

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

    tentativas = 3
    for tentativa in range(tentativas):
        try:
            print(f"LLM: Tentativa n {tentativa + 1}")
            with requests.post(URL, headers=HEADERS, json=payload, timeout=(5, 25)) as r:
                r.raise_for_status()
                data = r.json()
                resposta = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                print("LLM: Resposta pronta")
                return resposta
        except requests.exceptions.RequestException as e:
            print(f"[ERRO] {str(e)}")
            return "miau miau (não consegui pensar em nada hoje)"