from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from personality import system_message
from tools import get_tools

# langchain high level framework thru which we can build ai applications
# langgraphs more complex that allows us to build ai agents
# langchain ollama allows us to use llama within langchain and langgraphs
def build_model():
    return ChatOllama(model="qwen2.5:3b-instruct", temperature=0.2, num_ctx=2048)

def load_agent(model=None):
    model = model or build_model()
    tools = get_tools(model)
    return create_agent(model, tools, system_prompt=system_message.content)