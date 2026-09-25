"""
Vyom - Web GUI (separate HTML/CSS/JS files)
"""

import os
import sys

_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _folder in ["core", "memory", "security", "tools", "agents", "orchestrator"]:
    _path = os.path.join(_base, _folder)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from flask import Flask, request, jsonify, render_template
from orchestrator import VyomOrchestrator
from security_brain import UserLevel

app = Flask(__name__)
orchestrator = None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    user_id = data.get("user_id", "web_user")
    response = orchestrator.handle_message(user_id, UserLevel.TRUSTED, message)
    return jsonify({"response": response})


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


def run_server(mode="gemini", host="0.0.0.0", port=5000, **orchestrator_kwargs):
    global orchestrator
    orchestrator = VyomOrchestrator(mode=mode, **orchestrator_kwargs)
    app.run(host=host, port=port)


if __name__ == "__main__":
    run_server()
