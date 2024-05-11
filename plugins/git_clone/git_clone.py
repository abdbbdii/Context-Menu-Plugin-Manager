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

def driver(folders, params):
    mat = re.match(r".*github\.com/(\w+/[\w-]+)", paste())
    if mat:
        repo = mat.group(1)
    else:
        messagebox.showerror("Invalid URL", "The URL you pasted is not a valid GitHub repository URL")
        return
    system(f'git clone "https://github.com/{repo}.git"')