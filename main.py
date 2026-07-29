# step one is to get an llm's api keys (not here rn, as i'm using ollama which runs locally)
# step two is obv to import stuff, ill write reasons beside each import
# step three is giving the ai assistant a personality
# step four is a while loop which quits when asked, otherwise goes thru the llm's response and prints it
# step five is to add whatever tools i want (don't forget the docstring though)

from langchain_core.messages import HumanMessage

from agent import load_agent


# diff bw chatbots and ai agents? ai agents have access to tools


def main():
    agent_executor = load_agent()
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
        if user_input == "bye":
            break
if __name__ == "__main__":
    main()
