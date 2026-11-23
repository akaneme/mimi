# app.py
# gradio frontend for mimi
# run with: uv run python app.py

import os

import gradio as gr
from langchain_core.messages import HumanMessage, AIMessage
from agent import load_agent


agent_executor = load_agent()

# optional local avatar: drop an image at assets/mimi.png (no internet needed)
AVATAR = "assets/mimi.png" if os.path.exists("assets/mimi.png") else None


# ── helpers ───────────────────────────────────────────────────────────────────
def message_text(content):
    """gradio can hand back message content as a string or a list of blocks,
    so normalise it to plain text"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "".join(parts)
    return ""


def to_langchain(history):
    """convert gradio history format -> langchain messages"""
    messages = []
    for msg in history:
        text = message_text(msg.get("content"))
        if not text:
            continue
        if msg["role"] == "user":
            messages.append(HumanMessage(content=text))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=text))
    return messages


# ── streaming chat (this is what gradio calls) ────────────────────────────────
def stream_reply(message, history):
    """yields mimi's reply as it grows. stream_mode="messages" gives us the
    model's output token by token, plus the tool results as they finish"""
    messages = to_langchain(history) + [HumanMessage(content=message)]

    reply = ""
    last_kind = None
    for token, meta in agent_executor.stream(
        {"messages": messages}, stream_mode="messages"
    ):
        node = meta.get("langgraph_node")
        if node == "model":
            kind = "model"
        elif node == "tools":
            kind = "tool"
        else:
            continue

        text = message_text(token.content)
        if not text:
            continue

        # keep tool output and the model's reply on separate paragraphs
        if reply and last_kind and kind != last_kind:
            reply += "\n\n"
        reply += text
        last_kind = kind
        yield reply


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
        avatar_images=(None, AVATAR),
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
        if not message.strip():
            yield "", chat_history
            return

        history = chat_history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": ""},
        ]
        yield "", history

        got_reply = False
        for partial in stream_reply(message, chat_history):
            got_reply = True
            yield "", history[:-1] + [{"role": "assistant", "content": partial}]

        if not got_reply:
            yield "", history[:-1] + [{"role": "assistant", "content": "..."}]

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    send.click(respond, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch()
