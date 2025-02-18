from os import system
from pyperclip import paste
from tkinter import messagebox
import re

plugin_info = {
    "title": "Paste Git Repository Here",
    "description": "Clone a git repository",
    "type": ["DIRECTORY_BACKGROUND"],
    "menu_name": "abd Utils",
}

def driver(folders: list[str] = [], params: str = ""):
    mat = re.match(r"(?:https?:\/\/)?github\.com\/([^\/]+)\/([^\/]+?)(?:\.git)?(?:\/.*)?$", paste())
    if mat:
        owner = mat.group(1)
        repo = mat.group(2)
    else:
        messagebox.showerror("Invalid URL", "The URL you pasted is not a valid GitHub repository URL")
        return
    system(f'git clone "https://github.com/{owner}/{repo}.git"')

if __name__ == "__main__":
    driver()
