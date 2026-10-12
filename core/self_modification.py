import os
import shutil
import difflib
from datetime import datetime


class SelfModification:
    def __init__(self, security=None, package_root=None):
        self.package_root = os.path.abspath(package_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.backup_dir = os.path.join(self.package_root, "_self_edit_backups")
        os.makedirs(self.backup_dir, exist_ok=True)

    def _resolve_safe_path(self, relative_path):
        full_path = os.path.abspath(os.path.join(self.package_root, relative_path))
        if not full_path.startswith(self.package_root):
            raise PermissionError("Path traversal blocked.")
        return full_path

    def read_own_file(self, relative_path):
        path = self._resolve_safe_path(relative_path)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def preview_diff(self, relative_path, new_content):
        path = self._resolve_safe_path(relative_path)
        old_content = ""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                old_content = f.read()
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile="a/" + relative_path,
            tofile="b/" + relative_path,
        )
        return "".join(diff)

    def _check_syntax(self, relative_path, new_content):
        if not relative_path.endswith(".py"):
            return {"ok": True}
        try:
            compile(new_content, relative_path, "exec")
            return {"ok": True}
        except SyntaxError as e:
            return {"ok": False, "error": "Syntax error: " + str(e)}

    def edit_own_code(self, user_id, user_level, relative_path, new_content):
        path = self._resolve_safe_path(relative_path)
        diff_text = self.preview_diff(relative_path, new_content)

        syntax_check = self._check_syntax(relative_path, new_content)
        if not syntax_check["ok"]:
            return {"ok": False, "error": syntax_check["error"], "diff": diff_text}

        if os.path.exists(path):
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_name = os.path.basename(relative_path) + "." + timestamp + ".bak"
            shutil.copy2(path, os.path.join(self.backup_dir, backup_name))

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return {"ok": True, "message": "Updated " + relative_path, "diff": diff_text}

    def rollback(self, relative_path, backup_filename):
        backup_path = os.path.join(self.backup_dir, backup_filename)
        if not os.path.exists(backup_path):
            return {"ok": False, "error": "Backup not found."}
        target_path = self._resolve_safe_path(relative_path)
        shutil.copy2(backup_path, target_path)
        return {"ok": True, "message": "Rolled back " + relative_path}

    def list_backups(self):
        return sorted(os.listdir(self.backup_dir))

    def write_code_from_instruction(self, brain, user_id, user_level, relative_path, instruction):
        current = ""
        try:
            current = self.read_own_file(relative_path)
        except Exception:
            pass

        prompt = (
            "Tum ek Python file edit kar rahe ho: " + relative_path + "\n"
            "Current content:\n" + current + "\n\n"
            "Instruction: " + instruction + "\n\n"
            "Sirf poora naya file-content do, koi explanation nahi, koi markdown "
            "backticks nahi - sirf raw Python code."
        )
        new_content = brain.simple_ask(prompt).strip()
        if new_content.startswith("```"):
            lines = new_content.split("\n")
            new_content = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        return self.edit_own_code(user_id, user_level, relative_path, new_content)
