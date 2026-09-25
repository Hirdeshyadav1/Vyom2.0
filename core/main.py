"""
Vyom - CLI entry point.
Run: python main.py
Set ANTHROPIC_API_KEY env var to enable live LLM responses.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from vyom.orchestrator.orchestrator import VyomOrchestrator
from vyom.security.security_brain import UserLevel


def main():
    print("=== Vyom ===")
    print("Wake word: 'Vyom'. Type 'exit' to quit.\n")

    print("Kaunsa mode chalana hai?")
    print("  1 = Local (FREE, offline, Ollama chahiye — koi bill nahi)")
    print("  2 = Cloud (Anthropic API, paid, zyada capable)")
    choice = input("Choose (1/2, default 1): ").strip() or "1"

    if choice == "1":
        host = input("Home server ka IP address (ENTER = isi machine par, 'localhost'): ").strip() or "localhost"
        orchestrator = VyomOrchestrator(mode="local", local_host=host)
        if not orchestrator.brain.is_available():
            print(
                f"\n[Warning] Home server ({orchestrator.brain.base_url}) nahi mila. Check karo:\n"
                "  1. https://ollama.com/download se server par install karo\n"
                "  2. Server par: ollama pull llama3.2\n"
                "  3. Poore network pe available karne ke liye: OLLAMA_HOST=0.0.0.0 ollama serve\n"
                "  4. Server ka sahi local IP address diya hai (router se milega)\n"
                "  5. Dono devices same WiFi/network par hain\n"
            )
    else:
        orchestrator = VyomOrchestrator(mode="cloud")

    user_id = "local_user"
    user_level = UserLevel.TRUSTED

    while True:
        try:
            message = input("Tum: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nVyom band ho raha hai...")
            break

        if message.lower() in ("exit", "quit", "band karo"):
            print("Vyom: Alvida!")
            break
        if not message:
            continue

        response = orchestrator.handle_message(user_id, user_level, message)
        print(f"Vyom: {response}\n")


if __name__ == "__main__":
    main()
