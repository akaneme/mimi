# app.py
# gradio frontend for mimi
# run with: python app.py

import gradio as gr
from langchain_core.messages import HumanMessage, AIMessage
from agent import load_agent


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
