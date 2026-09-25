"""
Vyom - Internet Intelligence
Anthropic ke built-in web_search tool ka wrapper.
"""


class InternetIntelligence:
    def __init__(self, brain):
        self.brain = brain

    def search_and_answer(self, query):
        result = self.brain.chat(
            [{"role": "user", "content": query}],
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
        )
        if "error" in result:
            return "[Vyom] " + result["error"]
        texts = [b["text"] for b in result.get("content", []) if b.get("type") == "text"]
        return "\n".join(texts).strip()

    def compare_sources(self, topic):
        prompt = "'" + topic + "' ke baare mein multiple sources se information dhundo aur unme differences batao."
        return self.search_and_answer(prompt)
