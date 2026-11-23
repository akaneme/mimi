import ast
import operator
import os

import requests
from bs4 import BeautifulSoup
from langchain.tools import tool

# ── calculator ────────────────────────────────────────────────────────────────
# evaluates the expression by walking its syntax tree, so only plain
# arithmetic is allowed (no eval(), no function calls, no variable names).
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _evaluate(node):
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and not isinstance(node.value, bool)
    ):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("that exponent is too big")
        return _OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.operand))
    raise ValueError("only plain arithmetic is supported")


@tool("calculator", return_direct=True)
def calculator(expression: str) -> str:
    """evaluates an arithmetic expression like '42 + 58', '(3 + 4) * 5',
    '2 ** 10' or '100 / 8'. supports + - * / // % ** and parentheses"""
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _evaluate(tree)
        if isinstance(result, float):
            result = int(result) if result.is_integer() else round(result, 10)
        return f"{expression.strip()} = {result} ^^"
    except ZeroDivisionError:
        return "can't divide by zero, even i know that :/"
    except (ValueError, SyntaxError, OverflowError) as e:
        return f"couldn't calculate that: {e}"


# ── anime search ──────────────────────────────────────────────────────────────
@tool("search_anime")
def search_anime(query: str) -> str:
    """search for anime information"""
    try:
        resp = requests.get(
            "https://api.jikan.moe/v4/anime",
            params={"q": query, "limit": 1},
            timeout=10,
        )
        if resp.status_code == 429:
            return "jikan is rate limiting me, try again in a few seconds :/"
        resp.raise_for_status()
        data = resp.json()
        if data.get("data"):
            anime = data["data"][0]
            title = anime.get("title", "unknown title")
            synopsis = anime.get("synopsis") or "no synopsis available :/"
            if len(synopsis) > 250:
                synopsis = synopsis[:250] + "..."
            return f"{title}: {synopsis}"
        return "not found :/ something else?"
    except Exception as e:
        return f"anime search broke somehow: {str(e)}"


# ── snippet saver ─────────────────────────────────────────────────────────────
@tool("save_code_snippet")
def save_code_snippet(filename: str, code: str) -> str:
    """save a code snippet to a file in the snippets folder"""
    filename = os.path.basename(filename.strip())
    if not filename:
        return "i need a filename to save that, like hello.py"
    try:
        os.makedirs("snippets", exist_ok=True)
        filepath = os.path.join("snippets", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        return f"saved to snippets/{filename}"
    except Exception as e:
        return f"error: {str(e)}"


# ── page summariser ───────────────────────────────────────────────────────────
# summarize_url needs a model reference, so it's built via a factory
def make_summarize_url(model):
    @tool("summarize_url")
    def summarize_url(url: str) -> str:
        """fetches and summarizes a webpage"""
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            return "that doesn't look like a link, it should start with http:// or https://"
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
    return [calculator, search_anime, save_code_snippet, make_summarize_url(model)]
