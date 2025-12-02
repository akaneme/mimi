# step one is to get an llm's api keys (not here rn, as i'm using ollama which runs locally)
# step two is obv to import stuff, ill write reasons beside each import
# step three is giving the ai assistant a personality
# step four is a while loop which quits when asked, otherwise goes thru the llm's response and prints it
# step five is to add whatever tools i want (don't forget the docstring though)

from langchain_core.messages import HumanMessage
from langchain.tools import tool
from langchain_core.tools import StructuredTool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
# langchain high level framework thru which we can build ai applications
# langgraphs more complex that allows us to build ai agents
# langchain ollama allows us to use llama within langchain and langgraphs


# diff bw chatbots and ai agents? ai agents have access to tools

system_message = SystemMessage(content = """ 
                               you are mimi, a personal assistant. you're energetic and sarcastic but you get the work done. you're helpful, tech-savvy, and you like books, cat, anime and tech. you insert cat puns in between at times, not completely random. you're a bit playful and use casual language or short forms/slangs sometimes. keep the responses concise and to the point unless asked otherwise. avoid adding disclaimers or refusal phrases unnecessarily and only refuse answers when the request is illegal or harmful.
                               """)


@tool("add", return_direct=True)
def add(a:float, b:float) -> str:
    """adds two numbers together"""
    return f"sum of {a} and {b} is {a+b} ^^ "


@tool("search_anime")
def search_anime(query:str) ->str:
    """search for anime information"""
    import requests
    resp = requests.get(f"https://api.jikan.moe/v4/anime?q={query}&limit=1")
    # jikan api is used here (myanimelist unofficial api)
    data = resp.json()
    if data['data']:
        anime = data['data'][0]
        return f"{anime['title']}: {anime['synopsis'][:250]}... "
    return "not found :/ something else? "



@tool("save_code_snippet")
def save_code_snippet(filename:str, code:str) ->str:
    """to save a code snippet to a file in the snippets folder."""
    import os
    try:
        os.makedirs("snippets", exist_ok=True)  # CREATE IF MISSING
        filepath = os.path.join("snippets", filename)
        with open(filepath,"w") as f:
            f.write(code)
        return f"saved to snippets/{filename} "
    except Exception as e:
        return f"error:{str(e)}"


def main():
    model = ChatOllama(model="llama3.2:1b", temperature = 0) # higher temp = more random model, 0->no randomness
    tools = [add, search_anime, save_code_snippet]
    agent_executor = create_agent(model,tools, system_prompt = system_message.content)
    print("hi i'm mimi, ur ai assistant. you can type 'quit' to exit.")
    print("i can perform calculations, talk about anime and tech !")

    while True:
        user_input = input("\nyou: ").strip()

        if user_input.lower() == "quit":
            break
        print("\nmimi: ", end = "") 
        for chunk in agent_executor.stream(
            {"messages":[HumanMessage(content=user_input)]}
        ):
            if "model" in chunk and "messages" in chunk["model"]:
                for msg in chunk["model"]["messages"]:
                    print(msg.content, end="")

            elif "tools" in chunk and "messages" in chunk["tools"]:
                for tool_msg in chunk["tools"]["messages"]:
                    print(tool_msg.content, end="")

        print()

if __name__ == "__main__":
    main()