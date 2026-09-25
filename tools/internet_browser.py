"""
Vyom - Real Internet Browsing
Actual webpage fetch + content extraction.
"""

import requests
from urllib.parse import urlparse


class InternetBrowser:
    def __init__(self, user_agent="VyomAssistant/1.0"):
        self.headers = {"User-Agent": user_agent}

    def fetch_page(self, url, timeout=10):
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return {"ok": False, "error": "Sirf http/https URLs allowed hain."}

        try:
            resp = requests.get(url, headers=self.headers, timeout=timeout)
            resp.raise_for_status()
            return {"ok": True, "status": resp.status_code, "html": resp.text, "url": resp.url}
        except requests.exceptions.RequestException as e:
            return {"ok": False, "error": str(e)}

    def extract_text(self, url, max_chars=5000):
        from bs4 import BeautifulSoup

        page = self.fetch_page(url)
        if not page["ok"]:
            return page

        soup = BeautifulSoup(page["html"], "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = " ".join(soup.get_text(separator=" ").split())
        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        return {
            "ok": True,
            "title": title,
            "text": text[:max_chars],
            "truncated": len(text) > max_chars,
            "url": page["url"],
        }

    def extract_links(self, url):
        from bs4 import BeautifulSoup

        page = self.fetch_page(url)
        if not page["ok"]:
            return page

        soup = BeautifulSoup(page["html"], "html.parser")
        links = [{"text": a.get_text(strip=True), "href": a.get("href")} for a in soup.find_all("a", href=True)]
        return {"ok": True, "links": links[:50], "url": page["url"]}


class InternetIntelligenceLLM:
    def __init__(self, brain, browser=None):
        self.brain = brain
        self.browser = browser or InternetBrowser()

    def summarize_page(self, url, question=""):
        result = self.browser.extract_text(url)
        if not result["ok"]:
            return "[Vyom] Page fetch nahi ho payi: " + result["error"]

        from prompt_injection_guard import PromptInjectionGuard
        guard = PromptInjectionGuard()
        safe_content = guard.sanitize_for_llm(result["text"], source=url)

        prompt_text = question if question else "Summarize karo."
        prompt = prompt_text + "\n\nTitle: " + result["title"] + "\nContent: " + safe_content
        return self.brain.simple_ask(prompt)
