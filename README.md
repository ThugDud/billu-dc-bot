# 🤖 Billu, o Gato

Um bot de Discord com alma de gato debochado, sarcástico, e cheio de personalidade. Ele responde quando quer, mas quando responde, manda a real. Alimentado por Google Gemini, emojis de zoeira e muita insolência.

---

## ⚙️ Requisitos

- Python 3.11 ou superior (idealmente)
- Discord bot token
- Gemini API key
- Git (pra clonar e fazer update)
- Sistema Operacional: **Windows ou Linux**

---

## 🧠 Instalação e Execução

### 1. Clone o repositório

```bash
git clone https://github.com/TeuUser/billu-dc-bot.git
cd billu-dc-bot
```

### 2. Crie o `.env`

Na raiz do projeto:

```dotenv
BOT_API_KEY=seu_token_do_discord
GEMINI_API_KEY=seu_token_da_gemini_api
AUTHOR_ID=seu_id_de_usuario_do_discord
```

### 3. Instale as dependências


```bash
pip install discord.py python-dotenv requests
```

### 4. Rode o bot

```bash
python main.py
```

---

## 🎮 Como Funciona

### Billu responde...

- Quando alguém escreve "billu" em um dos canais permitidos
- Automaticamente em alguns canais quando acumula spam de mensagens
- Em canais especiais tipo "fodaci", onde ele responde tudo
- Com personalidade programada (tipo um roleplay do Derik bot)

### Comando secreto de admin:

- `/apagarhistorico` — reseta o histórico de chat da LLM

---

## 🤬 Personalidade do Billu

> Ele é um gato sarcástico, debochado, e às vezes gentil, mas só quando convém.  
> Responde de forma espirituosa e com um toque de zoeira, as vezes sendo ofensivo por brincadeira.

Se quiser mudar isso, edita a variável `PERSONALIDADE` dentro de `llm.py`.

---

## 🧼 Segurança

- Tokens são lidos de `.env`
- Histórico da conversa salvo localmente em `comandos/historico/`
- Evita mensagens com mais de 2000 caracteres (discord limitation)

---

## 📂 Estrutura do Projeto

```
📁 comandos/
  ├─ historico/       # [!] crie essa pasta
  ├─ gemini.py        # comandos do Gemini
  ├─ gerais.py        # comandos gerais (/apagarhistorico, etc.)
  └─ llm.py           # lógica principal da LLM
main.py               # entrada principal do bot
.env                  # onde vão as chaves secretas
```

---

## 🐧 Rodando no Linux?

Sim. O código já usa `os` e `pathlib` de forma multiplataforma. Se tu tiver um linux, é só instalar o Python, clonar, pôr o `.env`, e rodar.

---

## 🪦 FAQ

**Q: O bot morreu depois de uma hora?**  
A: Sim. Isso é normal no Discord se tu não fizer reconexão automática. Mas o Billu tenta reconectar quando cai, desde que tu não tenha chutado a máquina.

**Q: Posso deixar rodando enquanto jogo?**  
A: Sim. O bot usa pouca CPU/RAM. Só toma cuidado se tua net for uma bosta.

**Q: Como adiciono novos comandos?**  
A: Cria funções dentro de `gerais.py` ou `gemini.py` e registra elas no `setup_hook()`.
