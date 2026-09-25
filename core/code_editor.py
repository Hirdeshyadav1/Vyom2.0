import os

def read_file(file_path):
    """File padhne ke liye"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def update_file(file_path, content):
    """File ka code rewrite karne ke liye"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully updated {file_path}"
    except Exception as e:
        return f"Error updating file: {str(e)}"
