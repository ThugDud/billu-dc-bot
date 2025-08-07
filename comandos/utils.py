from datetime import datetime
import traceback

LOG_PATH = "log.txt"

def log_erro(e: Exception, contexto: str = ""):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n[{agora}] ERRO: {contexto}\n")
        f.write(f"Tipo: {type(e).__name__}\n")
        f.write(f"Mensagem: {str(e)}\n")
        f.write(f"Stack:\n{traceback.format_exc()}\n")
        f.write("-" * 60 + "\n")
