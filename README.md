# mimi is a personal assistant
she lives inside ur walls, i mean terminal.
she is a customized ai agent built with LangChain and Llama that reflects a bit of personality.

## features include
- a personality
- calculator 
- code snippet saver
- can search anime using Jikan API 
- runs locally using Ollama and is free waaa

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
