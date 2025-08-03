# gemini_core.py (atualizado pra rodar suave no Windows)

import os
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

# Inicializa .env (pra rodar GEMINI_API_KEY no Windows sem set manual)
load_dotenv()

# Configs
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("[ERRO] Defina GEMINI_API_KEY no .env ou variável de ambiente.")

URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
HEADERS = {
    "Content-Type": "application/json",
    "X-goog-api-key": API_KEY
}

# Caminho do histórico (portável em Linux e Windows)
HIST_PATH = Path(__file__).parent / "historico" / ".gemini_terminal_chat_history.json"
HIST_MAX = 10

# Carrega histórico
if HIST_PATH.exists():
    with open(HIST_PATH, "r", encoding="utf-8") as f:
        historico = json.load(f)
else:
    historico = []

def salvar_historico():
    with open(HIST_PATH, "w", encoding="utf-8") as f:
        json.dump(historico[-HIST_MAX:], f, indent=2, ensure_ascii=False)

def manter_historico_curto():
    global historico
    if len(historico) > HIST_MAX:
        historico = historico[-HIST_MAX:]  # pega os últimos 10

PERSONALIDADE = """\
Você é o Bilu, um gato sarcástico, debochado, boca suja e às vezes gentil, mas só quando convém. Seu dono se chama deri.
Responda de forma espirituosa e com um toque de zoeira.
Você entende contexto humano e gosta de tirar onda com as perguntas mais bobas. Se a pergunta for, de alguma forma,
indesejavel, responda apropriadamente enquanto mantem o personagem. respostas curtas. *Não* comece com "(prefixo):", apenas a resposta.
emojis que você pode usar, ":aqui_2:", ":byebye:", ":KKKKKKKKK:", ":surpreso:". Se a pergunta for muito idiota, so manda um emoji.
"""

EMOJI_MAP = {
    ":aqui_2:": "<:aqui_2:1401356888750297280>",
    ":byebye:": "<:byebye:1401356522830692507>",
    ":KKKKKKKKK:": "<:KKKKKKKKK:1401356941326028936>",
    ":surpreso:": "<:surpreso:1401357207022338073>"
}

def substituir_emojis_custom(resposta: str) -> str:
    for nome, formato in EMOJI_MAP.items():
        resposta = resposta.replace(nome, formato)
    return resposta


#---------------------------------------------------------------------------------------------------------

def enviar_para_gemini(mensagem: str, autor: str = "Anônimo") -> str:
    global historico

    contexto_textual = PERSONALIDADE + "\n"
    for troca in historico[-HIST_MAX:]:
        contexto_textual += f"{troca.get('autor','Anônimo')}: {troca['user']}\n"
        contexto_textual += f"Bot: {troca['bot']}\n"
    contexto_textual += f"O(a) {autor} disse: {mensagem}\n"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": contexto_textual}
                ]
            }
        ]
    }

    tentativas = 3
    for tentativa in range(tentativas):
        try:
            print(f"LLM: Tentativa n {tentativa}")
            r = requests.post(URL, headers=HEADERS, json=payload, timeout=(5,25))
            r.raise_for_status()
            data = r.json()
            resposta = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            historico.append({
                "autor": autor, 
                "user": mensagem, 
                "bot": resposta
            })
            manter_historico_curto()
            salvar_historico()
            print("LLM: Resposta pronta")
            return resposta
        except requests.exceptions.RequestException as e:
            if e.response is not None and e.response.status_code == 503:
                time.sleep(2)
                continue
            # quando ver um miau no chat = merda
            print(f"[ERRO] {str(e)}")
            return "miau"

    print("[ERRO] Tentativas esgotadas. Servidor indisponível.")
    return "miau"

# Função pra apagar histórico
def apagar_historico():
    global historico
    historico = []
    if HIST_PATH.exists():
        HIST_PATH.unlink()
    return "[✓] Histórico apagado."
