from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from personality import system_message
from tools import get_tools

# the model has to be pulled first: ollama pull qwen2.5:3b-instruct
MODEL_NAME = "qwen2.5:3b-instruct"


# langchain high level framework thru which we can build ai applications
# langgraphs more complex that allows us to build ai agents
# langchain ollama allows us to use llama within langchain and langgraphs
def build_model():
    # num_ctx = how many tokens the model can see at once. summarize_url alone
    # can send ~1000 tokens of page text, and ollama silently cuts off anything
    # that doesn't fit, so 2048 was too tight once the system prompt, chat
    # history and tool schemas were added
    return ChatOllama(model=MODEL_NAME, temperature=0.2, num_ctx=4096)


def load_agent(model=None):
    model = model or build_model()
    tools = get_tools(model)
    return create_agent(model, tools, system_prompt=system_message.content)
