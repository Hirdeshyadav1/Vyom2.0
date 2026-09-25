"""
Vyom - Tool Calling System
Security se gated tools registry.
"""


class Tool:
    def __init__(self, name, func, description, danger_action=None):
        self.name = name
        self.func = func
        self.description = description
        self.danger_action = danger_action


class ToolRegistry:
    def __init__(self, security):
        self.security = security
        self.tools = {}

    def register(self, name, func, description, danger_action=None):
        self.tools[name] = Tool(name, func, description, danger_action)

    def list_tools(self):
        return {t.name: t.description for t in self.tools.values()}

    def call(self, name, user_id, user_level, **kwargs):
        tool = self.tools.get(name)
        if not tool:
            return {"ok": False, "error": "Unknown tool: " + name}

        if tool.danger_action:
            auth = self.security.authorize(user_id, user_level, tool.danger_action, details=kwargs)
            if not auth["allowed"]:
                return {"ok": False, "error": "Blocked: " + auth["reason"]}

        try:
            result = tool.func(**kwargs)
            return {"ok": True, "result": result}
        except Exception as e:
            return {"ok": False, "error": str(e)}


def calculator_tool(expression):
    import re
    if not re.fullmatch(r"[0-9+\-*/(). ]+", expression):
        raise ValueError("Invalid characters in expression")
    return str(eval(expression, {"__builtins__": {}}, {}))


def file_read_tool(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def file_write_tool(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return "Written " + str(len(content)) + " chars to " + path


def register_default_tools(registry):
    registry.register("calculator", calculator_tool, "Evaluate a basic arithmetic expression.")
    registry.register("read_file", file_read_tool, "Read a text file.", danger_action="access_private_files")
    registry.register("write_file", file_write_tool, "Write/overwrite a text file.", danger_action="delete_data")
