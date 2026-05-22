# mimi is a personal assistant
she lives inside ur walls, i mean terminal.  


mimi is built using:
- LangChain
- Ollama
- local LLMs
- Gradio


## features
- a personality
- local AI (runs fully on your machine waaa)
- anime search using Jikan API
- calculator tool
- saves code snippets to files
- gradio web UI
- Ollama integration



## demo

(need to add screenshots/gif here later)

might also add:
- demo vid/gif
- Gradio UI screenshots


  
## setup
step one: install ollama:
`curl -fsSL https://ollama.com/install.sh | sh`  
step two: pull model: 
`ollama pull llama3.2:1b`  
step three: install uv, if you don’t have it yet. (check https://docs.astral.sh/uv/ or use the installer you already used)  
step four: install deps: 
`uv sync`  
step five: run: 
`uv run python main.py`

## dependencies are listed in `pyproject.toml`.


reminder to future: work on snippet saver, try to include maybe more tools? and add screenshots
