# mimi is a personal assistant
she lives inside ur walls, i mean terminal.  

no paid apis and no keys: the llm is a small local model served by ollama, and the agent is built with langchain.

## what she can do
 
mimi is an agent, so she picks a tool based on what you ask:
 
| tool | what it does |
| --- | --- |
| `calculator` | evaluates arithmetic like `(3 + 4) * 5` or `2 ** 10` (+ - * / // % ** and brackets, parsed safely with `ast`, no `eval`) |
| `search_anime` | looks up an anime on the [jikan api](https://jikan.moe/) and returns the title and a short synopsis |
| `save_code_snippet` | saves code to a file inside the `snippets/` folder |
| `summarize_url` | fetches a webpage and summarises it with the local model |

## built with
 
- [langchain](https://www.langchain.com/) for the agent and tool calling
- [ollama](https://ollama.com/) to run the model locally (`qwen2.5:3b-instruct`)
- [gradio](https://www.gradio.app/) for the web chat ui, with replies streamed token by token
- jikan api for anime data 



## setup
 
1. install ollama (linux): `curl -fsSL https://ollama.com/install.sh | sh`
2. pull the model: `ollama pull qwen2.5:3b-instruct`
3. install uv if you don't have it yet: https://docs.astral.sh/uv/
4. install dependencies: `uv sync`

## run
 
web ui (opens at http://127.0.0.1:7860):
 
```
uv run python app.py
```
 
terminal chat (type `quit` to exit):
 
```
uv run python main.py
```


## project layout
 
```
app.py          gradio web ui (streams replies)
main.py         terminal chat loop
agent.py        builds the model + agent
tools.py        the four tools
personality.py  mimi's system prompt
snippets/       where saved code snippets go
```
 
## notes and limitations
 
- she's a 3b model, so she sometimes picks the wrong tool or ignores one. rephrasing the request usually helps.
- jikan rate limits requests, so rapid anime searches can fail for a few seconds.
- `summarize_url` only reads the first ~4000 characters of a page.
- the context window is set to 4096 tokens in `agent.py`. long chats or long pages can still overflow it.
- to use a different model, change `MODEL_NAME` in `agent.py` (it needs tool-calling support).
## ideas for later
 
- more tools
- keep chat history across restarts
- add screenshots
