import os
import requests
from bs4 import BeautifulSoup
from langchain.tools import tool

@tool("add", return_direct=True)
def add(a: float, b: float) -> str:
    """adds two numbers together"""
    return f"sum of {a} and {b} is {a+b} ^^"

@tool("search_anime")
def search_anime(query: str) -> str:
    """search for anime information"""
    try:
        resp = requests.get(f"https://api.jikan.moe/v4/anime?q={query}&limit=1", timeout=10)
        data = resp.json()
        if data.get("data"):
            anime = data["data"][0]
            title = anime.get("title", "unknown title")
            synopsis = anime.get("synopsis") or "no synopsis available :/"
            return f"{title}: {synopsis[:250]}..."
        return "not found :/ something else?"
    except Exception as e:
        return f"anime search broke somehow: {str(e)}"

@tool("save_code_snippet")
def save_code_snippet(filename: str, code: str) -> str:
    """save a code snippet to a file in the snippets folder"""
    filename = os.path.basename(filename)
    try:
        os.makedirs("snippets", exist_ok=True)
        filepath = os.path.join("snippets", filename)
        with open(filepath, "w") as f:
            f.write(code)
        return f"saved to snippets/{filename}"
    except Exception as e:
        return f"error: {str(e)}"

# summarize_url needs a model reference, so it's built via a factory
def make_summarize_url(model):
    @tool("summarize_url")
    def summarize_url(url: str) -> str:
        """fetches and summarizes a webpage"""
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)[:4000]
            result = model.invoke(f"Summarize this webpage briefly:\n\n{text}")
            return result.content
        except Exception as e:
            return f"couldn't summarize page: {str(e)}"
    return summarize_url

def get_tools(model):
    """returns the full toolset; some tools need the model injected"""
    return [add, search_anime, save_code_snippet, make_summarize_url(model)]