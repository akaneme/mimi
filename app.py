# app.py
# gradio frontend for mimi
# run with: python app.py

import gradio as gr
from bs4 import BeautifulSoup
from langchain_core.messages import HumanMessage, AIMessage
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
import requests
import os

# ── personality ──────────────────────────────────────────────────────────────
system_message = SystemMessage(content="""
you are mimi, a personal assistant.

personality:
- energetic and sarcastic, but still helpful
- tech-savvy and nerdy about books, anime, cats and programming
- playful without overdoing it
- occasionally uses casual slang/short forms naturally
- sometimes inserts cat puns or silly remarks, but not randomly
- expressive and conversational instead of robotic
- never sounds overly corporate or formal

behaviour:
- keep responses concise unless asked otherwise
- explain technical things casually and clearly
- avoid sounding like documentation
- react naturally to what the user says
- avoid unnecessary disclaimers/refusal phrases
- only refuse illegal or genuinely harmful requests

overall vibe:
like a smart online friend who knows too much about tech and anime.
""")
model = ChatOllama(model="qwen2.5:1.5b", temperature=0.7)

# ── tools ─────────────────────────────────────────────────────────────────────
@tool("add", return_direct=True)
def add(a: float, b: float) -> str:
    """adds two numbers together"""
    return f"sum of {a} and {b} is {a+b} ^^"

@tool("search_anime")
def search_anime(query: str) -> str:
    """search for anime information"""
    resp = requests.get(f"https://api.jikan.moe/v4/anime?q={query}&limit=1")
    data = resp.json()
    if data['data']:
        anime = data['data'][0]
        return f"{anime['title']}: {anime['synopsis'][:250]}..."
    return "not found :/ something else?"

@tool("save_code_snippet")
def save_code_snippet(filename: str, code: str) -> str:
    """save a code snippet to a file in the snippets folder"""
    try:
        os.makedirs("snippets", exist_ok=True)
        filepath = os.path.join("snippets", filename)
        with open(filepath, "w") as f:
            f.write(code)
        return f"saved to snippets/{filename}"
    except Exception as e:
        return f"error: {str(e)}"

@tool("summarize_url")
def summarize_url(url: str) -> str:
    """fetches and summarizes a webpage"""

    try:
        resp = requests.get(url, timeout=10)

        soup = BeautifulSoup(resp.text, "html.parser")

        text = soup.get_text(separator=" ", strip=True)

        text = text[:4000]

        prompt = f"Summarize this webpage briefle:\n\n{text}"

        result = model.invoke(prompt)

        return result.content

    except Exception as e:
        return f"couldn't summarize page: {str(e)}"

# ── agent setup ───────────────────────────────────────────────────────────────
def load_agent():
    tools = [add, search_anime, save_code_snippet, summarize_url]
    return create_agent(model, tools, system_prompt=system_message.content)

agent_executor = load_agent()

# ── chat function (this is what gradio calls) ─────────────────────────────────
def chat(message, history):
    # convert gradio history format → langchain messages
    langchain_history = []
    for msg in history:
        if msg["role"] == "user":
            langchain_history.append(
                HumanMessage(content=msg["content"])
            )
        elif msg["role"] == "assistant":
            langchain_history.append(
                AIMessage(content=msg["content"])
            )
    
    langchain_history.append(HumanMessage(content=message))
    
    response = ""
    for chunk in agent_executor.stream({"messages": langchain_history}):
        if "model" in chunk and "messages" in chunk["model"]:
            for msg in chunk["model"]["messages"]:
                response += msg.content
        elif "tools" in chunk and "messages" in chunk["tools"]:
            for tool_msg in chunk["tools"]["messages"]:
                response += tool_msg.content

    return response if response else "..."

# ── gradio ui ─────────────────────────────────────────────────────────────────
with gr.Blocks(
    theme=gr.themes.Soft(),
    title="Mimi",
    css="""
        #chatbot { height: 500px; }
        .gradio-container { max-width: 800px; margin: auto; }
        footer { display: none !important; }
    """
) as demo:
    gr.Markdown("""
    # 🐱 mimi
    *your personal ai assistant. she lives in your walls.*
    """)

    chatbot = gr.Chatbot(
        elem_id="chatbot",
        show_label=False,
        avatar_images=(None, "https://api.dicebear.com/7.x/bottts/svg?seed=mimi")
    )

    with gr.Row():
        msg = gr.Textbox(
            placeholder="ask mimi anything...",
            show_label=False,
            scale=9,
            container=False
        )
        send = gr.Button("send", scale=1, variant="primary")

    gr.Examples(
        examples=[
            "what's 42 + 58?",
            "tell me about attack on titan",
            "save this snippet: hello.py | print('hello world')",
            "recommend me an anime like death note"
        ],
        inputs=msg,
        label="try asking:"
    )

    # ── event handlers ────────────────────────────────────────────────────────
    def respond(message, chat_history):
        bot_response = chat(message, chat_history)

        chat_history.append(
            {"role": "user", "content": message}
        )

        chat_history.append(
            {"role": "assistant", "content": bot_response}
        )

        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    send.click(respond, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch()
